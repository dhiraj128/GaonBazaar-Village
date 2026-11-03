import os
import ssl
import socket
import pytest
import certifi
from app.db import session

def test_session_configuration_has_no_insecure_tls_flags():
    """Verify that insecure CERT_NONE and check_hostname = False are strictly absent."""
    with open(session.__file__, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "CERT_NONE" not in content, "Found insecure ssl.CERT_NONE in session.py"
    assert "check_hostname = False" not in content, "Found insecure check_hostname = False in session.py"
    assert "ssl.CERT_REQUIRED" in content, "Missing strict ssl.CERT_REQUIRED in session.py"
    assert "check_hostname = True" in content, "Missing strict check_hostname = True in session.py"
    assert "verify-full" in content, "Missing sync verify-full sslmode in session.py"

def test_supabase_ca_cert_file_exists_and_valid():
    """Verify that the Supabase root CA certificate is present and valid."""
    assert os.path.exists(session.SUPABASE_CA_CERT), f"Supabase CA cert not found at {session.SUPABASE_CA_CERT}"
    assert os.path.getsize(session.SUPABASE_CA_CERT) > 1000

def test_verified_tls_handshake_to_supabase_pooler():
    """Verify successful TLS handshake to Supabase pooler with strict certificate & hostname verification."""
    hostname = "aws-0-ap-south-1.pooler.supabase.com"
    port = 5432

    ctx = ssl.create_default_context(cafile=session.SUPABASE_CA_CERT)
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            # Send Postgres SSLRequest packet (8 bytes)
            sock.sendall(bytes([0, 0, 0, 8, 4, 210, 22, 47]))
            resp = sock.recv(1)
            assert resp == b"S", "Postgres server declined SSL request"
            
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                sans = [entry[1] for entry in cert.get("subjectAltName", []) if entry[0] == "DNS"]
                assert "*.pooler.supabase.com" in sans or hostname in sans
    except (socket.gaierror, socket.timeout) as e:
        pytest.skip(f"Network connectivity to Supabase pooler unavailable: {e}")

def test_rejection_of_untrusted_ca_certificate():
    """Verify that using an untrusted or invalid CA strictly fails TLS handshake with SSLCertVerificationError."""
    hostname = "aws-0-ap-south-1.pooler.supabase.com"
    port = 5432

    # Standard public certifi CA does not contain Supabase's private root CA
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            sock.sendall(bytes([0, 0, 0, 8, 4, 210, 22, 47]))
            resp = sock.recv(1)
            if resp != b"S":
                pytest.skip("Postgres server declined SSL")
            
            with pytest.raises(ssl.SSLCertVerificationError) as exc_info:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    pass
            assert "certificate verify failed" in str(exc_info.value).lower()
    except (socket.gaierror, socket.timeout) as e:
        pytest.skip(f"Network connectivity to Supabase pooler unavailable: {e}")
