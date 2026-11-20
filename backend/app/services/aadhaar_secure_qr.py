"""
GaonBazaar UIDAI Secure QR Code Verification Service
===================================================
Implements offline cryptographic verification of UIDAI Digitally Signed
Aadhaar Secure QR Codes (e-Aadhaar, PVC Card, physical Aadhaar letter).

Cryptographic Architecture:
- Format: Compressed Big-Endian GZIP byte stream encoded as Base-10 Integer
- Delimiter: 0xFF (Byte 255) for demographic fields
- Signature: Trailing 256 bytes (RSA-2048 PKCS#1 v1.5 with SHA-256)
- Signed Content: All bytes preceding the 256-byte signature
- Trust Anchor: Official UIDAI Public Key Certificate Store
"""

import io
import re
import gzip
import zlib
import base64
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

logger = logging.getLogger("gaonbazaar.aadhaar_qr")

DELIMITER = b"\xff"
RSA_SIGNATURE_LEN = 256

LEGACY_FIELDS = [
    "email_mobile", "reference_id", "name", "dob", "gender",
    "careof", "dist", "landmark", "house", "loc", "pc", "po",
    "state", "street", "subdist", "vtc"
]

VERSIONED_FIELDS = [
    "version", "email_mobile", "reference_id", "name", "dob", "gender",
    "careof", "dist", "landmark", "house", "loc", "pc", "po",
    "state", "street", "subdist", "vtc", "mobile_last_four"
]


class AadhaarQrError(Exception):
    """Base exception for Aadhaar QR operations"""
    pass


class MalformedQrPayloadError(AadhaarQrError):
    """Raised when QR payload format is invalid or unparseable"""
    pass


class UnsupportedAadhaarFormatError(MalformedQrPayloadError):
    """Raised when an unsupported QR format (e.g. UPI, URL) is scanned"""
    pass


class UnsupportedLegacyAadhaarFormatError(MalformedQrPayloadError):
    """Raised when an old XML Aadhaar QR format without signature is scanned"""
    pass


class InvalidAadhaarSignatureError(AadhaarQrError):
    """Raised when UIDAI cryptographic signature verification fails"""
    pass


class NoCertificateConfiguredError(AadhaarQrError):
    """Raised when no trusted UIDAI certificate is found"""
    pass


# ---------------------------------------------------------------------------
# Certificate Store
# ---------------------------------------------------------------------------
class UidaiCertificateStore:
    """
    Manages trusted UIDAI public certificates for offline signature validation.
    Loads .cer (DER) and .pem certificates from directory and configuration.
    """
    _instance = None

    def __init__(self, cert_dir: Optional[str] = None):
        self.cert_dir = Path(cert_dir) if cert_dir else Path(__file__).resolve().parent.parent / "certificates" / "uidai"
        self._certificates: List[Tuple[str, Any]] = [] # list of (source_name, public_key)
        self._test_keypair: Optional[Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey, str]] = None
        self.reload()

    def reload(self):
        """Loads all certificates from the certificate directory."""
        self._certificates.clear()
        if not self.cert_dir.exists():
            self.cert_dir.mkdir(parents=True, exist_ok=True)

        for path in self.cert_dir.glob("*"):
            if path.suffix.lower() in [".cer", ".crt", ".der", ".pem"]:
                try:
                    raw = path.read_bytes()
                    pub_key = self._parse_certificate(raw)
                    if pub_key:
                        self._certificates.append((path.name, pub_key))
                        logger.info("Loaded UIDAI trusted certificate: %s", path.name)
                except Exception as exc:
                    logger.warning("Failed to load certificate from %s: %s", path.name, exc)

    def _parse_certificate(self, data: bytes) -> Optional[Any]:
        """Parses DER or PEM certificate into a public key object."""
        if b"-----BEGIN CERTIFICATE-----" in data:
            cert = x509.load_pem_x509_certificate(data, default_backend())
            return cert.public_key()
        elif b"-----BEGIN PUBLIC KEY-----" in data:
            from cryptography.hazmat.primitives.serialization import load_pem_public_key
            return load_pem_public_key(data, default_backend())
        else:
            try:
                cert = x509.load_der_x509_certificate(data, default_backend())
                return cert.public_key()
            except Exception:
                from cryptography.hazmat.primitives.serialization import load_der_public_key
                return load_der_public_key(data, default_backend())

    def add_pem_certificate(self, pem_str: str, source_name: str = "custom_pem"):
        """Adds a PEM certificate in-memory."""
        pub_key = self._parse_certificate(pem_str.encode("utf-8"))
        if pub_key:
            self._certificates.append((source_name, pub_key))

    def get_public_keys(self) -> List[Tuple[str, Any]]:
        """Returns all loaded public keys."""
        return list(self._certificates)

    def get_or_create_test_identity(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey, str]:
        """Provides a self-signed synthetic keypair for unit tests and local simulation."""
        if not self._test_keypair:
            priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            pub = priv.public_key()
            from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
            pub_pem = pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode("utf-8")
            self._test_keypair = (priv, pub, pub_pem)
        return self._test_keypair

    @classmethod
    def get_default(cls) -> "UidaiCertificateStore":
        if cls._instance is None:
            cls._instance = UidaiCertificateStore()
        return cls._instance


# ---------------------------------------------------------------------------
# Core Secure QR Parser & Signature Verifier
# ---------------------------------------------------------------------------
class AadhaarSecureQrParser:
    """
    Decodes and cryptographically validates UIDAI Secure QR codes according
    to the official UIDAI specification.
    """

    def __init__(self, cert_store: Optional[UidaiCertificateStore] = None):
        self.cert_store = cert_store or UidaiCertificateStore.get_default()

    def parse_and_verify(
        self,
        raw_qr_input: str,
        allow_test_identity: bool = False
    ) -> Dict[str, Any]:
        """
        Parses the scanned QR string, validates the UIDAI RSA-2048 SHA-256
        digital signature, extracts permitted demographics, and decodes the photo.
        """
        raw_qr_input = raw_qr_input.strip()
        if not raw_qr_input:
            raise MalformedQrPayloadError("Empty QR code data provided.")

        # 1. Convert scanned payload into bytes
        decompressed_bytes = self._decompress_payload(raw_qr_input)
        total_len = len(decompressed_bytes)

        if total_len <= RSA_SIGNATURE_LEN:
            raise MalformedQrPayloadError(f"Payload too short ({total_len} bytes). Expected > 256 bytes.")

        # 2. Separate signed content and signature
        signature = decompressed_bytes[-RSA_SIGNATURE_LEN:]
        signed_data = decompressed_bytes[:-RSA_SIGNATURE_LEN]

        # 3. Cryptographically verify signature
        sig_valid, matching_cert_name = self._verify_signature(
            signed_data,
            signature,
            allow_test_identity=allow_test_identity
        )

        if not sig_valid:
            raise InvalidAadhaarSignatureError(
                "UIDAI digital signature verification failed. "
                "The QR payload has been tampered with, corrupted, or was not signed by a trusted UIDAI certificate."
            )

        # 4. Parse demographic fields
        demographics, photo_bytes = self._extract_demographics_and_photo(signed_data)

        # 5. Format address and reference info
        ref_id = demographics.get("reference_id") or ""
        last_4_digits = demographics.get("mobile_last_four") or (ref_id[:4] if len(ref_id) >= 4 else "XXXX")

        full_address = self._build_full_address(demographics)

        # 6. Process photo
        photo_base64 = self._process_photo_bytes(photo_bytes)

        return {
            "valid": True,
            "signature_verified": True,
            "verification_method": "UIDAI_SECURE_QR",
            "algorithm": "SHA256withRSA-2048",
            "matching_certificate": matching_cert_name,
            "reference_id": ref_id,
            "last_4_digits": last_4_digits,
            "name": demographics.get("name") or "Resident",
            "dob": demographics.get("dob") or "",
            "gender": (demographics.get("gender") or "").upper(),
            "address": full_address,
            "split_address": {
                "care_of": demographics.get("careof") or "",
                "house": demographics.get("house") or "",
                "street": demographics.get("street") or "",
                "landmark": demographics.get("landmark") or "",
                "locality": demographics.get("loc") or "",
                "village_town": demographics.get("vtc") or "",
                "sub_district": demographics.get("subdist") or "",
                "district": demographics.get("dist") or "",
                "state": demographics.get("state") or "",
                "pincode": demographics.get("pc") or ""
            },
            "photo_base64": photo_base64,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "message": "Aadhaar Secure QR digital signature verified successfully"
        }

    def _decompress_payload(self, raw_input: str) -> bytes:
        """
        Converts Base-10 integer string (or raw bytes) to decompressed payload bytes.
        """
        clean_input = re.sub(r"[\s\r\n]", "", raw_input)

        # Check for legacy XML or non-Aadhaar QR formats
        if "<PrintLetterBarcodeData" in raw_input or "<?xml" in raw_input:
            raise UnsupportedLegacyAadhaarFormatError("This QR format isn't supported.")

        if raw_input.startswith(("upi://", "http://", "https://", "WIFI:", "BEGIN:VCARD")):
            raise UnsupportedAadhaarFormatError("This QR format isn't supported.")

        # Case A: Scanned as standard Base-10 integer string
        if clean_input.isdigit():
            val = int(clean_input)
            byte_len = (val.bit_length() + 7) // 8
            raw_bytes = val.to_bytes(byte_len, byteorder="big")
        # Case B: Base-64 encoded gzip stream
        elif re.match(r"^[A-Za-z0-9+/=]+$", clean_input) and len(clean_input) > 50:
            try:
                raw_bytes = base64.b64decode(clean_input)
            except Exception:
                raw_bytes = clean_input.encode("latin-1")
        # Case C: Direct binary stream
        else:
            raw_bytes = raw_input.encode("latin-1")

        # Decompress GZIP or ZLIB with offset resilience
        gzip_idx = raw_bytes.find(b"\x1f\x8b")
        if gzip_idx != -1 and gzip_idx < 16:
            try:
                return gzip.decompress(raw_bytes[gzip_idx:])
            except Exception:
                pass

        if raw_bytes.startswith(b"\x1f\x8b"):
            try:
                return gzip.decompress(raw_bytes)
            except Exception as exc:
                raise MalformedQrPayloadError(f"QR detected but couldn't be read. Please retry.")
        else:
            try:
                return zlib.decompress(raw_bytes, 16 + zlib.MAX_WBITS)
            except Exception:
                try:
                    return zlib.decompress(raw_bytes)
                except Exception:
                    try:
                        return zlib.decompress(raw_bytes, -zlib.MAX_WBITS)
                    except Exception as exc:
                        raise MalformedQrPayloadError(f"QR detected but couldn't be read. Please retry.")

    def _verify_signature(
        self,
        signed_data: bytes,
        signature: bytes,
        allow_test_identity: bool = False
    ) -> Tuple[bool, str]:
        """
        Checks RSA PKCS#1 v1.5 SHA-256 signature against all trusted certificates.
        """
        if len(signature) != RSA_SIGNATURE_LEN:
            logger.warning("Invalid signature byte length: %d (expected 256)", len(signature))
            return False, ""

        keys = self.cert_store.get_public_keys()

        # If test identity is allowed (staging / pytest), include the test keypair
        if allow_test_identity:
            _, test_pub, _ = self.cert_store.get_or_create_test_identity()
            keys.append(("uidai_synthetic_test_cert", test_pub))

        if not keys:
            logger.warning("No UIDAI certificates loaded in store.")
            raise NoCertificateConfiguredError(
                "No UIDAI public key certificate is configured to verify signatures."
            )

        for cert_name, pub_key in keys:
            try:
                pub_key.verify(
                    signature,
                    signed_data,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                logger.info("Cryptographic signature verified matching: %s", cert_name)
                return True, cert_name
            except InvalidSignature:
                continue
            except Exception as exc:
                logger.debug("Verification error with certificate %s: %s", cert_name, exc)
                continue

        return False, ""

    def _extract_demographics_and_photo(
        self,
        signed_data: bytes
    ) -> Tuple[Dict[str, str], Optional[bytes]]:
        """
        Extracts delimited text fields and resident photograph bytes.
        """
        # Check Versioned layout (V2, V3, etc.)
        version_match = re.match(rb"^V(\d+)\xff", signed_data)
        if version_match:
            field_names = VERSIONED_FIELDS
            has_version = True
        else:
            field_names = LEGACY_FIELDS
            has_version = False

        demographics: Dict[str, str] = {}
        offset = 0

        for name in field_names:
            end = signed_data.find(DELIMITER, offset)
            if end == -1:
                break
            raw_field = signed_data[offset:end]
            try:
                demographics[name] = raw_field.decode("iso-8859-1").strip()
            except Exception:
                demographics[name] = raw_field.decode("utf-8", errors="ignore").strip()
            offset = end + 1

        # Extract photo bytes
        # In versioned layout, photo starts immediately after the last demographic field
        indicator = demographics.get("email_mobile", "0")
        has_email = (not has_version) and indicator in ("1", "3")
        has_mobile = (not has_version) and indicator in ("2", "3")
        hash_bytes_len = (int(has_email) + int(has_mobile)) * 32

        photo_len = len(signed_data) - offset - hash_bytes_len
        photo_bytes = None
        if photo_len > 0:
            photo_bytes = signed_data[offset: offset + photo_len]

        return demographics, photo_bytes

    def _build_full_address(self, d: Dict[str, str]) -> str:
        """Composes a human-readable address from available fields."""
        parts = []
        for key in ["careof", "house", "street", "landmark", "loc", "vtc", "subdist", "dist", "state"]:
            val = d.get(key)
            if val and val.strip():
                parts.append(val.strip())
        pc = d.get("pc")
        if pc and pc.strip():
            parts.append(f"PIN: {pc.strip()}")
        return ", ".join(parts) if parts else "Address Not Available"

    def _process_photo_bytes(self, photo_bytes: Optional[bytes]) -> Optional[str]:
        """Converts raw image bytes (JPEG / JPEG2000) into a base64 Data URL."""
        if not photo_bytes or len(photo_bytes) < 16:
            return None
        try:
            # Check for standard JPEG header
            if photo_bytes.startswith(b"\xff\xd8\xff"):
                b64 = base64.b64encode(photo_bytes).decode("ascii")
                return f"data:image/jpeg;base64,{b64}"

            # Open with Pillow if available (handles JPEG, JPEG2000, PNG)
            if HAS_PIL:
                img = Image.open(io.BytesIO(photo_bytes))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                b64 = base64.b64encode(buf.getvalue()).decode("ascii")
                return f"data:image/jpeg;base64,{b64}"
        except Exception as exc:
            logger.debug("Photo extraction notice: %s", exc)
            try:
                # Direct fallback if valid image buffer
                b64 = base64.b64encode(photo_bytes).decode("ascii")
                return f"data:image/jpeg;base64,{b64}"
            except Exception:
                return None


# ---------------------------------------------------------------------------
# Document & Image QR Extractors (Server-Side Fallback)
# ---------------------------------------------------------------------------
def extract_qr_from_image_bytes(image_bytes: bytes) -> Optional[str]:
    """
    Detects and decodes QR code string from raw image bytes using OpenCV or Pyzbar.
    """
    if not HAS_OPENCV:
        logger.warning("OpenCV is not available for server-side QR decoding.")
        return None

    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        # 1. Standard OpenCV QRCodeDetector
        detector = cv2.QRCodeDetector()
        val, pts, _ = detector.detectAndDecode(img)
        if val and val.strip():
            return val.strip()

        # 2. Try grayscale + threshold for lower contrast images
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        val, pts, _ = detector.detectAndDecode(gray)
        if val and val.strip():
            return val.strip()

        # 3. Otsu thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        val, pts, _ = detector.detectAndDecode(thresh)
        if val and val.strip():
            return val.strip()

    except Exception as exc:
        logger.warning("OpenCV QR extraction error: %s", exc)

    return None


def extract_qr_from_pdf_bytes(pdf_bytes: bytes) -> Optional[str]:
    """
    Extracts QR code from embedded images in e-Aadhaar PDF.
    """
    if not HAS_PYPDF:
        logger.warning("pypdf is not available for server-side PDF extraction.")
        return None

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            for img_file in page.images:
                qr_val = extract_qr_from_image_bytes(img_file.data)
                if qr_val:
                    return qr_val
    except Exception as exc:
        logger.warning("PDF QR extraction error: %s", exc)

    return None


# ---------------------------------------------------------------------------
# Test Synthetic Payload Generator
# ---------------------------------------------------------------------------
def create_synthetic_signed_qr(
    name: str = "Ramesh Kumar Sharma",
    dob: str = "15-05-1994",
    gender: str = "M",
    careof: str = "S/O: Ram Lal Sharma",
    district: str = "Muzaffarpur",
    vtc: str = "Chaturshi",
    pincode: str = "843128",
    state: str = "Bihar",
    last_four_mobile: str = "9012"
) -> Tuple[str, str]:
    """
    Generates a valid, cryptographically signed synthetic Secure QR payload
    and returns (encoded_qr_string, public_key_pem).
    Used exclusively for test suites and sandbox validation.
    """
    store = UidaiCertificateStore.get_default()
    priv_key, pub_key, pub_pem = store.get_or_create_test_identity()

    ref_id = f"5489{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}001"
    fields = [
        "V2", "3", ref_id, name, dob, gender, careof, district,
        "Near Shiv Mandir", "House No 12", "Ward 4", pincode,
        "Chaturshi SO", state, "Main Bazar Road", "Minapur", vtc, last_four_mobile
    ]

    signed_data = b"".join(f.encode("iso-8859-1") + DELIMITER for f in fields)
    # JPEG stub (1x1 pixel JPEG)
    photo_stub = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\xff\xd9"
    signed_data += photo_stub

    signature = priv_key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    decompressed = signed_data + signature
    gz_data = gzip.compress(decompressed)
    num = int.from_bytes(gz_data, byteorder="big")

    return str(num), pub_pem
