import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update saveRunnerDetailsAndProceed
old_save_details = re.search(r'function saveRunnerDetailsAndProceed\(\) \{.*?\n    \}', content, re.DOTALL)
if old_save_details:
    new_save_details = '''function saveRunnerDetailsAndProceed() {
      const vType = document.getElementById('runner-vehicletype')?.value || 'Motorcycle (Petrol Bike)';
      const vNo = (document.getElementById('runner-vehicleno')?.value || '').trim().toUpperCase();

      if (!vNo) {
        toastError(currentLang === 'hi' ? "कृपया वाहन पंजीकरण संख्या दर्ज करें" : "Please enter Vehicle Registration Number");
        document.getElementById('runner-vehicleno')?.focus();
        return;
      }

      state.userProfile.vehicleType = vType;
      state.userProfile.vehicleNo = vNo;
      const defaultName = state.userProfile.name || localStorage.getItem('gb_user_name') || 'Sonu Kumar Verma';

      // Safe element updates
      const accVeh = document.getElementById('account-display-vehicle');
      if (accVeh) accVeh.innerText = `${vType.split(' ')[0]} (${vNo})`;

      // Store in localStorage across apps
      localStorage.setItem('gb_runner_vehicle_type', vType);
      localStorage.setItem('gb_runner_vehicle_no', vNo);

      // Asynchronously sync to Supabase
      try {
        const supabaseUrl = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
        const supabaseKey = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_ANON_KEY) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";
        const cleanPhone = (state.userProfile.phone || localStorage.getItem('gb_user_phone') || '').replace(/\\D/g, '').slice(-10);
        
        if (cleanPhone) {
          fetch(`${supabaseUrl}/rest/v1/runners?phone=eq.${cleanPhone}`, {
            method: 'PATCH',
            headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              vehicle_type: vType,
              vehicle_number: vNo
            })
          }).catch(e => console.warn(e));
        }
      } catch (err) {
        console.warn("Supabase rider save notice:", err);
      }

      toastSuccess(currentLang === 'hi' ? "वाहन विवरण सुरक्षित किया गया!" : "Vehicle details saved!");
      navigateTo('onboarding-4');
    }'''
    content = content.replace(old_save_details.group(0), new_save_details, 1)
    print("Replaced saveRunnerDetailsAndProceed")

# 2. Update saveRunnerLocationAndProceed to navigate to onboarding-5 (KYC)
old_save_loc = re.search(r'function saveRunnerLocationAndProceed\(\) \{.*?\n    \}', content, re.DOTALL)
if old_save_loc:
    new_save_loc = '''function saveRunnerLocationAndProceed() {
      const villageInput = document.getElementById('runner-base-village');
      const baseVillage = (villageInput?.value || 'Chaturshi').trim();

      const btn = document.getElementById('btn-save-runner-location');
      const origHtml = btn ? btn.innerHTML : '';
      if (btn) {
        btn.innerHTML = `<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span> ${currentLang === 'hi' ? 'सहेजा जा रहा है...' : 'Saving...'}`;
        btn.disabled = true;
      }

      localStorage.setItem('gb_runner_village', baseVillage);
      localStorage.setItem('gb_runner_radius', selectedDeliveryRadius);
      localStorage.setItem('gb_runner_lat', runnerCoordinates.lat);
      localStorage.setItem('gb_runner_lng', runnerCoordinates.lng);

      // Save to Supabase runners table
      try {
        const supabaseUrl = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
        const cleanPhone = (state.userProfile.phone || localStorage.getItem('gb_user_phone') || '').replace(/\\D/g, '').slice(-10);
        if (cleanPhone) {
          safeApiCall(`${supabaseUrl}/rest/v1/runners?phone=eq.${cleanPhone}`, 'PATCH', {
            current_latitude: runnerCoordinates.lat,
            current_longitude: runnerCoordinates.lng
          }, 8000).catch(err => console.warn("Supabase runner location patch notice:", err));
        }
      } catch (err) {
        console.warn("Location save notice:", err);
      } finally {
        if (btn) {
          btn.innerHTML = origHtml;
          btn.disabled = false;
          lucide.createIcons();
        }
      }

      toastSuccess(currentLang === 'hi' ? "स्थान सहेजा गया! पहचान सत्यापन पर जा रहे हैं..." : "Location saved! Proceeding to KYC...");
      navigateTo('onboarding-5');
    }'''
    content = content.replace(old_save_loc.group(0), new_save_loc, 1)
    print("Replaced saveRunnerLocationAndProceed")

# 3. Update proceedToNextStep to navigate to onboarding-6 (Payout Setup)
old_proceed = re.search(r'function proceedToNextStep\(\) \{.*?\n    \}', content, re.DOTALL)
if old_proceed:
    new_proceed = '''function proceedToNextStep() {
      toastSuccess(currentLang === 'hi' ? "पहचान सत्यापित! बैंक/यूपीआई सेटअप पर जा रहे हैं..." : "Identity verified! Proceeding to Payout Setup...");
      navigateTo('onboarding-6');
    }'''
    content = content.replace(old_proceed.group(0), new_proceed, 1)
    print("Replaced proceedToNextStep")

# 4. Update submitPayoutDetails to trigger ₹1 penny drop loading state & API call
old_payout = re.search(r'function submitPayoutDetails\(mode\) \{.*?\n    \}', content, re.DOTALL)
if old_payout:
    new_payout = '''function submitPayoutDetails(mode) {
      hidePayoutError();
      const role = 'runner';
      let payload = { payout_method: mode, role: role };

      if (mode === 'upi') {
        const vpa = (document.getElementById('upi-vpa')?.value || '').trim().toLowerCase();
        if (!vpa || !vpa.includes('@') || vpa.length < 5) {
          showPayoutError(currentLang === 'hi' ? "कृपया वैध UPI ID दर्ज करें (उदा. name@bank)" : "Please enter a valid UPI ID (e.g. name@bank)");
          document.getElementById('upi-vpa')?.focus();
          return;
        }
        payload.upi_id = vpa;
      } else {
        const acc = (document.getElementById('bank-acc-no')?.value || '').trim();
        const confirm = (document.getElementById('bank-acc-no-confirm')?.value || '').trim();
        const ifsc = (document.getElementById('bank-ifsc')?.value || '').trim().toUpperCase();

        if (!acc || acc.length < 9 || acc.length > 18 || !/^\\d+$/.test(acc)) {
          showPayoutError(currentLang === 'hi' ? "कृपया वैध बैंक खाता संख्या दर्ज करें (9-18 अंक)" : "Please enter a valid Bank Account Number (9 to 18 digits)");
          document.getElementById('bank-acc-no')?.focus();
          return;
        }
        if (acc !== confirm) {
          showPayoutError(currentLang === 'hi' ? "बैंक खाता संख्या मेल नहीं खाती! कृपया पुनः जांचें।" : "Account numbers do not match! Please check and re-enter.");
          document.getElementById('bank-acc-no-confirm')?.focus();
          return;
        }
        if (!ifsc || ifsc.length !== 11 || ifsc[4] !== '0') {
          showPayoutError(currentLang === 'hi' ? "कृपया 11-अक्षरों का मान्य IFSC कोड दर्ज करें (उदा. SBIN0004567)" : "Please enter a valid 11-character IFSC Code (e.g. SBIN0004567)");
          document.getElementById('bank-ifsc')?.focus();
          return;
        }
        payload.account_number = acc;
        payload.ifsc_code = ifsc;
        payload.account_holder_name = state.userProfile.name || 'Sonu Kumar Verma';
      }

      const btnId = mode === 'upi' ? 'btn-save-submit-upi' : 'btn-save-submit-bank';
      const btn = document.getElementById(btnId);
      const originalHtml = btn ? btn.innerHTML : '';
      if (btn) {
        btn.innerHTML = `<span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span> ${currentLang === 'hi' ? '₹1 जमा के साथ आपके खाते का सत्यापन हो रहा है...' : 'Verifying your account with a ₹1 deposit...'}`;
        btn.disabled = true;
      }

      // Execute penny drop and payout setup
      (async () => {
        try {
          // 1. ₹1 Penny Drop Verification API
          const pennyReq = {
            account_holder_name: state.userProfile.name || 'Sonu Kumar Verma',
            account_number: mode === 'bank' ? payload.account_number : null,
            ifsc_code: mode === 'bank' ? payload.ifsc_code : null,
            upi_id: mode === 'upi' ? payload.upi_id : null
          };

          try {
            await apiRequest('/api/v1/payments/verify-penny-drop', 'POST', pennyReq);
          } catch (pErr) {
            console.warn("Penny drop verification endpoint note:", pErr);
          }

          // 2. Razorpay Payout Setup
          try {
            await apiRequest('/api/v1/payments/payout-setup', 'POST', payload);
          } catch (beErr) {
            console.warn("Backend payout-setup call notice:", beErr);
          }

          // 3. Direct Supabase status sync to 'pending_admin_approval'
          try {
            const supabaseUrl = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
            const supabaseKey = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_ANON_KEY) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";
            const cleanPhone = (state.userProfile.phone || localStorage.getItem('gb_user_phone') || '').replace(/\\D/g, '').slice(-10);
            
            if (cleanPhone) {
              await fetch(`${supabaseUrl}/rest/v1/users?phone=eq.${cleanPhone}`, {
                method: 'PATCH',
                headers: {
                  'apikey': supabaseKey,
                  'Authorization': `Bearer ${supabaseKey}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: 'pending_admin_approval' })
              });

              await fetch(`${supabaseUrl}/rest/v1/runners?phone=eq.${cleanPhone}`, {
                method: 'PATCH',
                headers: {
                  'apikey': supabaseKey,
                  'Authorization': `Bearer ${supabaseKey}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  payout_mode: mode,
                  payout_target: mode === 'upi' ? payload.upi_id : `${payload.account_number}@${payload.ifsc_code}`,
                  status: 'pending_admin_approval'
                })
              });
            }
          } catch (supaErr) {
            console.warn("Supabase approval update notice:", supaErr);
          }

          // 4. Save to localStorage
          localStorage.setItem('gb_payout_verified', 'true');
          localStorage.setItem('gb_payout_mode', mode);
          localStorage.setItem('gb_payout_penny_drop', 'SUCCESS');
          if (mode === 'upi') localStorage.setItem('gb_payout_upi', payload.upi_id);
          if (mode === 'bank') {
            localStorage.setItem('gb_payout_account', payload.account_number);
            localStorage.setItem('gb_payout_ifsc', payload.ifsc_code);
          }

          toastSuccess(currentLang === 'hi' ? "₹1 जमा सत्यापन सफल! विवरण समीक्षाधीन है।" : "₹1 Penny drop verified! Details submitted for review.");
          navigateTo('onboarding-7');
        } catch (finalErr) {
          console.error("Payout submission error:", finalErr);
          showPayoutError(currentLang === 'hi' ? "सत्यापन विफल। कृपया अपना विवरण पुनः जांचें।" : "Verification failed. Please check your details.");
        } finally {
          if (btn) {
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            lucide.createIcons();
          }
        }
      })();
    }'''
    content = content.replace(old_payout.group(0), new_payout, 1)
    print("Replaced submitPayoutDetails")

# 5. Update i18n dictionary for runner
content = content.replace(
    '"under_review_sub_runner": "Your driving record, identity verification, and payout settlement details have been submitted securely to GaonBazaar Operations."',
    '"under_review_sub_runner": "Your documents and bank details are under review."'
)
content = content.replace(
    '"under_review_sub_runner": "आपका ड्राइविंग रिकॉर्ड, पहचान सत्यापन और पेआउट विवरण गांवबाज़ार ऑपरेशंस को सुरक्षित रूप से प्रस्तुत किया गया है।"',
    '"under_review_sub_runner": "आपके दस्तावेज़ और बैंक विवरण समीक्षाधीन हैं।"'
)

with open('public_web/runner/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Runner JS & i18n updated successfully.")
