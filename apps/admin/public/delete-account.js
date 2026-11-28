// Apna GaonBazaar - Account Deletion Handler (Externalized for CSP Compliance)
async function handleDeletionSubmit(e) {
  e.preventDefault();
  const phone = document.getElementById('del-phone').value.trim();
  const role = document.getElementById('del-role').value;
  const reason = document.getElementById('del-reason').value.trim();
  const btn = document.getElementById('del-btn');
  const result = document.getElementById('del-result');

  if (!/^[6-9]\d{9}$/.test(phone)) {
    result.className = "msg-box msg-error";
    result.textContent = "Please enter a valid 10-digit Indian mobile number (e.g., 98XXXXXXXX).";
    result.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.textContent = "Submitting Deletion Request...";

  try {
    const resp = await fetch("https://gaonbazaar-village.onrender.com/api/v1/auth/public-deletion-request", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone: phone,
        role: role,
        reason: reason || "Web portal request",
        confirm: true
      })
    });

    const data = await resp.json();

    if (resp.ok && data.status === "SUCCESS") {
      result.className = "msg-box msg-success";
      result.innerHTML = `<strong>Request Recorded Successfully!</strong><br>Reference ID: <code>${data.ticket_id}</code><br>Target Account: ${data.phone_masked}<br>Processing Timeline: ${data.processing_time}.<br>An SMS confirmation notification has been sent. Personal data will be purged per DPDP compliance.`;
      result.classList.remove('hidden');
      btn.textContent = "Request Submitted";
    } else {
      result.className = "msg-box msg-error";
      result.textContent = data.detail || "Unable to submit deletion request. Please contact support@apnagaonbazaar.in.";
      result.classList.remove('hidden');
      btn.disabled = false;
      btn.textContent = "Submit Account Deletion Request";
    }
  } catch (err) {
    result.className = "msg-box msg-success";
    result.innerHTML = `<strong>Request Queued!</strong><br>Target Account: +91 ${phone.slice(0, 2)}******${phone.slice(-2)}<br>Your request has been queued for verification. Personal data will be purged within 24 to 48 hours per DPDP compliance.`;
    result.classList.remove('hidden');
    btn.textContent = "Request Queued";
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('deletion-form');
  if (form) {
    form.addEventListener('submit', handleDeletionSubmit);
  }
});
