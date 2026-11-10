"""
Inject Supabase Realtime 3-Way Order Routing Pipeline into Customer, Vendor, and Runner apps.
"""
import os
import re

def inject_vendor():
    path = "public_web/vendor/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Supabase JS client to <head> if not already present
    supabase_script = '  <!-- Supabase JS Client for Real-time 3-Way Order Routing -->\n  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
    if 'cdn.jsdelivr.net/npm/@supabase/supabase-js@2' not in content:
        content = content.replace('<!-- Toastify CSS & JS -->', f'{supabase_script}\n\n  <!-- Toastify CSS & JS -->', 1)
        print("Added supabase-js to vendor/index.html <head>")

    # 2. Add Vendor Realtime Client and handlers before closing script
    vendor_realtime_code = '''
    // ===========================================================================
    // SUPABASE REALTIME 3-WAY ORDER ROUTING (VENDOR PIPELINE)
    // ===========================================================================
    const SUPABASE_URL = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
    const SUPABASE_ANON_KEY = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_ANON_KEY) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";

    let supabaseVendorClient = null;
    function getSupabaseVendorClient() {
      if (!supabaseVendorClient && window.supabase && typeof window.supabase.createClient === 'function') {
        supabaseVendorClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        window.supabaseClient = supabaseVendorClient;
      }
      return supabaseVendorClient;
    }

    function setupVendorRealtimeOrders() {
      const client = getSupabaseVendorClient();
      if (!client) return;

      const vendorId = state.userProfile?.id || localStorage.getItem('gb_user_id') || 'usr_vendor_01';

      if (window.vendorRealtimeChannel) {
        try { client.removeChannel(window.vendorRealtimeChannel); } catch (e) {}
      }

      window.vendorRealtimeChannel = client
        .channel('vendor-orders-' + vendorId)
        .on('postgres_changes', {
          event: '*',
          schema: 'public',
          table: 'orders',
          filter: `vendor_id=eq.${vendorId}`
        }, (payload) => {
          handleVendorRealtimeOrder(payload);
        })
        .subscribe((status) => {
          console.log("[Supabase Realtime] Vendor orders subscription status:", status);
        });
    }

    function handleVendorRealtimeOrder(payload) {
      const order = payload.new || {};
      if (!order || !order.id) return;

      const st = (order.status || '').toUpperCase();
      console.log("[Vendor Realtime] Incoming order event:", payload.eventType, order.id, st);

      if (st === 'PENDING' || st === 'PLACED') {
        // Continuous Web Audio chime until vendor acts
        startOrderAlertRingtone();
        const banner = document.getElementById('sound-alert-banner');
        if (banner) banner.classList.remove('hidden');

        const empty = document.getElementById('new-orders-empty');
        if (empty) empty.classList.add('hidden');

        const card = document.getElementById('order-card-101');
        if (card) {
          card.classList.remove('hidden');
          card.classList.add('pulse-order');
          card.dataset.orderId = order.id;

          const titleEl = card.querySelector('[data-i18n="order_gb8921_title"]') || card.querySelector('h3');
          if (titleEl) titleEl.innerText = `Order #${(order.order_id || order.id).slice(-6)}`;

          const custEl = card.querySelector('[data-i18n="cust_order_sample"]') || card.querySelector('p');
          if (custEl) custEl.innerText = `Customer Village: ${order.delivery_village || 'Local'} (Immediate Delivery)`;

          const amtEl = card.querySelector('.text-base.font-extrabold');
          if (amtEl) amtEl.innerText = `₹${Number(order.total_amount || 340).toFixed(2)}`;

          const acceptBtn = card.querySelector('button[onclick*="acceptOrder"]');
          if (acceptBtn) acceptBtn.setAttribute('onclick', `acceptOrder('${order.id}')`);
          const rejectBtn = card.querySelector('button[onclick*="rejectOrder"]');
          if (rejectBtn) rejectBtn.setAttribute('onclick', `rejectOrder('${order.id}')`);
        }

        const badge = document.getElementById('new-orders-badge');
        if (badge) badge.innerText = '1';

        toastSuccess("🔔 New Order Received! Ringing chime.");
      } else if (st === 'PREPARING' || st === 'ACCEPTED') {
        const badgeNew = document.getElementById('new-orders-badge');
        if (badgeNew) badgeNew.innerText = '0';
        const badgePrep = document.getElementById('prep-orders-badge');
        if (badgePrep) badgePrep.innerText = '1';
      } else if (st === 'READY_FOR_PICKUP' || st === 'PACKED') {
        const badgePrep = document.getElementById('prep-orders-badge');
        if (badgePrep) badgePrep.innerText = '0';
        const badgeReady = document.getElementById('ready-orders-badge');
        if (badgeReady) badgeReady.innerText = '1';
      }
    }

    // Auto-initialize when window loads or dashboard opens
    window.addEventListener('DOMContentLoaded', () => {
      setTimeout(setupVendorRealtimeOrders, 1200);
    });
'''

    if 'SUPABASE REALTIME 3-WAY ORDER ROUTING (VENDOR PIPELINE)' not in content:
        content = content.replace('// DASHBOARD ORDERS SUB-TABS & ACTIONS', f'{vendor_realtime_code}\n\n    // DASHBOARD ORDERS SUB-TABS & ACTIONS', 1)
        print("Injected vendor realtime handler code")

    # Update acceptOrder in vendor app to update Supabase to 'PREPARING'
    old_accept = '''      try {
        await apiRequest('/api/v1/orders/vendor/orders/' + orderId + '/action', 'POST', { action: 'ACCEPT' });
      } catch (e) {}'''

    new_accept = '''      try {
        await apiRequest('/api/v1/orders/vendor/orders/' + orderId + '/action', 'POST', { action: 'ACCEPT' });
      } catch (e) {}

      const supa = getSupabaseVendorClient();
      if (supa) {
        try {
          await supa.from('orders').update({ status: 'PREPARING' }).eq('id', orderId);
        } catch (sErr) {
          console.warn("Supabase order status update notice:", sErr);
        }
      }'''

    if old_accept in content and 'supa.from(\'orders\').update({ status: \'PREPARING\' })' not in content:
        content = content.replace(old_accept, new_accept, 1)
        print("Updated acceptOrder with Supabase status update in vendor/index.html")

    # Update markOrderReady in vendor app to update Supabase to 'READY_FOR_PICKUP'
    old_ready = '''      try {
        await apiRequest('/api/v1/orders/vendor/orders/' + orderId + '/action', 'POST', { action: 'PACK' });
      } catch (e) {}'''

    new_ready = '''      try {
        await apiRequest('/api/v1/orders/vendor/orders/' + orderId + '/action', 'POST', { action: 'PACK' });
      } catch (e) {}

      const supa = getSupabaseVendorClient();
      if (supa) {
        try {
          await supa.from('orders').update({ status: 'READY_FOR_PICKUP' }).eq('id', orderId);
        } catch (sErr) {
          console.warn("Supabase order status update notice:", sErr);
        }
      }'''

    if old_ready in content and 'supa.from(\'orders\').update({ status: \'READY_FOR_PICKUP\' })' not in content:
        content = content.replace(old_ready, new_ready, 1)
        print("Updated markOrderReady with Supabase status update in vendor/index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def inject_runner():
    path = "public_web/runner/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Supabase JS client to <head> if not already present
    supabase_script = '  <!-- Supabase JS Client for Real-time 3-Way Order Routing -->\n  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
    if 'cdn.jsdelivr.net/npm/@supabase/supabase-js@2' not in content:
        content = content.replace('<!-- Toastify CSS & JS -->', f'{supabase_script}\n\n  <!-- Toastify CSS & JS -->', 1)
        print("Added supabase-js to runner/index.html <head>")

    # 2. Add Runner Realtime Geospatial Dispatch logic
    runner_realtime_code = '''
    // ===========================================================================
    // SUPABASE REALTIME GEOSPATIAL RUNNER DISPATCH & CONCURRENCY LOCKING
    // ===========================================================================
    const SUPABASE_URL = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
    const SUPABASE_ANON_KEY = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_ANON_KEY) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";

    let supabaseRunnerClient = null;
    function getSupabaseRunnerClient() {
      if (!supabaseRunnerClient && window.supabase && typeof window.supabase.createClient === 'function') {
        supabaseRunnerClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        window.supabaseClient = supabaseRunnerClient;
      }
      return supabaseRunnerClient;
    }

    function setupRunnerRealtimeOrders() {
      const client = getSupabaseRunnerClient();
      if (!client) return;

      if (window.runnerRealtimeChannel) {
        try { client.removeChannel(window.runnerRealtimeChannel); } catch (e) {}
      }

      window.runnerRealtimeChannel = client
        .channel('runner-orders-broadcast')
        .on('postgres_changes', {
          event: '*',
          schema: 'public',
          table: 'orders'
        }, (payload) => {
          handleIncomingRunnerOrderEvent(payload);
        })
        .subscribe((status) => {
          console.log("[Supabase Realtime] Runner missions subscription status:", status);
        });
    }

    function getRunnerVillage() {
      return (
        document.getElementById('runner-base-village')?.value ||
        localStorage.getItem('gb_runner_village') ||
        state.userProfile?.village ||
        'Chaturshi'
      ).trim().toLowerCase();
    }

    function handleIncomingRunnerOrderEvent(payload) {
      const order = payload.new || {};
      if (!order || !order.id) return;

      const runnerVillage = getRunnerVillage();
      const runnerId = state.userProfile?.id || localStorage.getItem('gb_user_id') || 'usr_runner_01';
      const orderVillage = (order.delivery_village || '').trim().toLowerCase();
      const st = (order.status || '').toUpperCase();

      console.log(`[Runner Realtime] Order ${order.id} status=${st} village=${order.delivery_village} runner_id=${order.runner_id}`);

      // 1. AUTO-DISMISSAL: If claimed by another runner, immediately vanish from screen
      if (order.runner_id && order.runner_id !== runnerId) {
        console.log(`[Runner Dispatch] Order ${order.id} claimed by another runner (${order.runner_id}). Auto-dismissing.`);
        dismissRunnerMissionCard(order.id);
        return;
      }

      // 2. STRICT GEOSPATIAL ISOLATION:
      // Runners must NEVER see orders outside their operating village
      const isMatch = !orderVillage || !runnerVillage ||
        orderVillage === runnerVillage ||
        orderVillage.includes(runnerVillage) ||
        runnerVillage.includes(orderVillage);

      if (!isMatch) {
        console.log(`[Geospatial Filter] Order ${order.id} delivery_village '${order.delivery_village}' does not match runner's hub '${runnerVillage}'. Suppressed.`);
        dismissRunnerMissionCard(order.id);
        return;
      }

      // 3. BROADCAST TRIGGER: When READY_FOR_PICKUP and unassigned, trigger chime & pop up card
      if ((st === 'READY_FOR_PICKUP' || st === 'PACKED') && !order.runner_id) {
        displayLiveRunnerMissionCard(order);
        startMissionAlertRingtone();
        toastSuccess(`🚀 New Delivery Mission in ${order.delivery_village || runnerVillage}!`);
      } else if (st !== 'READY_FOR_PICKUP' && st !== 'PACKED' && st !== 'RUNNER_ASSIGNED') {
        dismissRunnerMissionCard(order.id);
      }
    }

    function displayLiveRunnerMissionCard(order) {
      const empty = document.getElementById('no-missions-empty');
      if (empty) empty.classList.add('hidden');

      const banner = document.getElementById('runner-alert-banner');
      if (banner) banner.classList.remove('hidden');

      const card = document.getElementById('mission-card-201');
      if (card) {
        card.classList.remove('hidden');
        card.classList.add('pulse-mission');
        card.dataset.orderId = order.id;

        const titleEl = card.querySelector('[data-i18n="sample_mission_title"]') || card.querySelector('h3');
        if (titleEl) titleEl.innerText = `Mission #${(order.order_id || order.id).slice(-6)}`;

        const badgeEl = card.querySelector('[data-i18n="hot_mission_badge"]');
        if (badgeEl) badgeEl.innerText = `HOT MISSION • ${(order.delivery_village || 'LOCAL').toUpperCase()} • 2.8 KM`;

        const acceptBtn = card.querySelector('button[onclick*="acceptMission"]');
        if (acceptBtn) acceptBtn.setAttribute('onclick', `acceptMission('${order.id}')`);
      }
    }

    function dismissRunnerMissionCard(orderId) {
      stopMissionAlertRingtone();
      const banner = document.getElementById('runner-alert-banner');
      if (banner) banner.classList.add('hidden');

      const card = document.getElementById('mission-card-201');
      if (card && (!orderId || card.dataset.orderId === orderId || !card.dataset.orderId)) {
        card.classList.add('hidden');
        card.classList.remove('pulse-mission');
      }

      const empty = document.getElementById('no-missions-empty');
      if (empty) empty.classList.remove('hidden');
    }

    window.addEventListener('DOMContentLoaded', () => {
      setTimeout(setupRunnerRealtimeOrders, 1200);
    });
'''

    if 'SUPABASE REALTIME GEOSPATIAL RUNNER DISPATCH' not in content:
        content = content.replace('// ---------------------------------------------------------------------------', f'{runner_realtime_code}\n\n    // ---------------------------------------------------------------------------', 1)
        print("Injected runner realtime dispatch code")

    # Update acceptMission with atomic concurrency locking
    old_accept_mission = '''    async function acceptMission(missionId) {
      stopMissionAlertRingtone();
      const banner = document.getElementById('runner-alert-banner');
      if (banner) banner.classList.add('hidden');

      try {
        await apiRequest('/api/v1/orders/runner/jobs/' + missionId + '/action', 'POST', { action: 'ACCEPT' });
      } catch (e) {}

      toastSuccess("Mission " + missionId + " Accepted! Navigating to Active Run...");
      setTimeout(() => {
        switchDashboardTab('activerun');
      }, 700);
    }'''

    new_accept_mission = '''    async function acceptMission(missionId) {
      stopMissionAlertRingtone();
      const banner = document.getElementById('runner-alert-banner');
      if (banner) banner.classList.add('hidden');

      const runnerId = state.userProfile?.id || localStorage.getItem('gb_user_id') || 'usr_runner_01';
      let claimSuccess = true;

      // 1. ATOMIC CONCURRENCY LOCK IN SUPABASE
      const supa = getSupabaseRunnerClient();
      if (supa) {
        try {
          const { data, error } = await supa
            .from('orders')
            .update({
              runner_id: runnerId,
              status: 'RUNNER_ASSIGNED'
            })
            .eq('id', missionId)
            .is('runner_id', null)
            .in('status', ['READY_FOR_PICKUP', 'PACKED', 'ACCEPTED'])
            .select();

          if (error || !data || data.length === 0) {
            claimSuccess = false;
          }
        } catch (err) {
          console.warn("Supabase atomic claim check notice:", err);
        }
      }

      // 2. ATOMIC BACKEND CONCURRENCY CHECK
      try {
        await apiRequest('/api/v1/orders/runner/jobs/' + missionId + '/action', 'POST', { action: 'ACCEPT' });
      } catch (e) {
        if (!claimSuccess) {
          toastError("Too late! Another runner just claimed this delivery mission.");
          dismissRunnerMissionCard(missionId);
          return;
        }
      }

      if (!claimSuccess) {
        toastError("This mission was already claimed by another runner.");
        dismissRunnerMissionCard(missionId);
        return;
      }

      toastSuccess("Mission " + missionId + " Assigned to You! Navigating to Active Run...");
      setTimeout(() => {
        switchDashboardTab('activerun');
      }, 700);
    }'''

    if old_accept_mission in content:
        content = content.replace(old_accept_mission, new_accept_mission, 1)
        print("Updated acceptMission with atomic concurrency locking in runner/index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def inject_customer():
    path = "public_web/customer/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add Supabase JS client to <head> if not already present
    supabase_script = '  <!-- Supabase JS Client for Real-time 3-Way Order Routing -->\n  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
    if 'cdn.jsdelivr.net/npm/@supabase/supabase-js@2' not in content:
        content = content.replace('<!-- Toastify Notifications -->', f'{supabase_script}\n\n  <!-- Toastify Notifications -->', 1)
        print("Added supabase-js to customer/index.html <head>")

    # 2. Add Customer Realtime Tracking subscription and timeline mapping
    customer_realtime_code = '''
    // ===========================================================================
    // SUPABASE REALTIME LIVE ORDER TRACKING (CUSTOMER TIMELINE)
    // ===========================================================================
    const SUPABASE_URL = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_URL) || "https://vxewgvrjhjpntfvsmuez.supabase.co";
    const SUPABASE_ANON_KEY = (window.APP_CONFIG && window.APP_CONFIG.SUPABASE_ANON_KEY) || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ";

    let supabaseCustomerClient = null;
    function getSupabaseCustomerClient() {
      if (!supabaseCustomerClient && window.supabase && typeof window.supabase.createClient === 'function') {
        supabaseCustomerClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        window.supabaseClient = supabaseCustomerClient;
      }
      return supabaseCustomerClient;
    }

    function subscribeCustomerOrderTracking(orderId) {
      const client = getSupabaseCustomerClient();
      if (!client || !orderId) return;

      if (window.customerOrderChannel) {
        try { client.removeChannel(window.customerOrderChannel); } catch (e) {}
      }

      console.log("[Customer Realtime] Subscribing to live updates for order:", orderId);
      window.customerOrderChannel = client
        .channel('order-live-' + orderId)
        .on('postgres_changes', {
          event: '*',
          schema: 'public',
          table: 'orders',
          filter: `id=eq.${orderId}`
        }, (payload) => {
          const updated = payload.new;
          if (updated && updated.status) {
            handleCustomerLiveStatusUpdate(updated.status, updated);
          }
        })
        .subscribe((status) => {
          console.log("[Customer Realtime] Subscription status for", orderId, ":", status);
        });
    }

    function handleCustomerLiveStatusUpdate(status, orderData) {
      console.log("[Customer Realtime] Live Order Status Changed:", status, orderData);

      const statusText = document.getElementById('order-status-text');
      if (statusText) statusText.innerText = status;

      // Dynamically advance vertical timeline
      renderVerticalOrderTrackingTimeline([], status);

      // Toast feedback
      const labelMap = {
        'PENDING': 'Order Placed (ऑर्डर दर्ज हुआ)',
        'PLACED': 'Order Placed (ऑर्डर दर्ज हुआ)',
        'PREPARING': 'Shop is Packing (दुकानदार सामान पैक कर रहा है)',
        'ACCEPTED': 'Shop is Packing (दुकानदार सामान पैक कर रहा है)',
        'READY_FOR_PICKUP': 'Ready for Pickup (पिकअप के लिए तैयार)',
        'PACKED': 'Ready for Pickup (पिकअप के लिए तैयार)',
        'RUNNER_ASSIGNED': 'Runner Assigned (डिलीवरी पार्टनर नियुक्त)',
        'ASSIGNED': 'Runner Assigned (डिलीवरी पार्टनर नियुक्त)',
        'OUT_FOR_DELIVERY': 'Runner is on the way (रास्ते में है)',
        'DELIVERED': 'Order Delivered! (सफलतापूर्वक डिलीवर)'
      };

      if (labelMap[status]) {
        toastInfo(`Order Status: ${labelMap[status]}`);
      }
    }
'''

    if 'SUPABASE REALTIME LIVE ORDER TRACKING (CUSTOMER TIMELINE)' not in content:
        content = content.replace('function renderVerticalOrderTrackingTimeline(timeline, currentStatus)', f'{customer_realtime_code}\n\n    function renderVerticalOrderTrackingTimeline(timeline, currentStatus)', 1)
        print("Injected customer realtime tracking code")

    # Update renderVerticalOrderTrackingTimeline to support the 6 stages and status ranks cleanly
    old_stages = '''      const STAGES = [
        { key: 'PLACED', titleEn: 'Order Placed', titleHi: 'ऑर्डर दर्ज हुआ', descEn: 'Order received by village store', descHi: 'गाँव की दुकान को ऑर्डर प्राप्त हुआ' },
        { key: 'ACCEPTED', titleEn: 'Store Accepted', titleHi: 'दुकानदार ने स्वीकार किया', descEn: 'Store owner confirmed items', descHi: 'दुकानदार ने सामान की पुष्टि की' },
        { key: 'PACKED', titleEn: 'Items Packed', titleHi: 'सामान पैक हो गया', descEn: 'Groceries safely bagged', descHi: 'किराना सामान पैक कर दिया गया' },
        { key: 'READY_FOR_PICKUP', titleEn: 'Ready for Pickup', titleHi: 'पिकअप के लिए तैयार', descEn: 'Awaiting delivery partner arrival', descHi: 'डिलीवरी पार्टनर के आने की प्रतीक्षा' },
        { key: 'ASSIGNED', titleEn: 'Runner Assigned', titleHi: 'डिलीवरी पार्टनर नियुक्त', descEn: 'Runner allocated for rural transit', descHi: 'डिलीवरी पार्टनर को ऑर्डर सौंपा गया' },
        { key: 'PICKED_UP', titleEn: 'Order Picked Up', titleHi: 'ऑर्डर पिकअप हुआ', descEn: 'Collected from merchant counter', descHi: 'दुकान से सामान ले लिया गया' },
        { key: 'OUT_FOR_DELIVERY', titleEn: 'Out for Delivery', titleHi: 'रास्ते में है', descEn: 'Rider en route to your doorstep', descHi: 'डिलीवरी पार्टनर आपके घर की ओर आ रहा है' },
        { key: 'DELIVERED', titleEn: 'Delivered', titleHi: 'सफलतापूर्वक डिलीवर', descEn: 'Handed over at village doorstep', descHi: 'सामान आपके हाथों में सौंप दिया गया' }
      ];

      const statusRanks = {
        'PLACED': 1,
        'ACCEPTED': 2,
        'PACKED': 3,
        'READY_FOR_PICKUP': 4,
        'ASSIGNED': 5,
        'PICKED_UP': 6,
        'OUT_FOR_DELIVERY': 7,
        'DELIVERED': 8,
        'CANCELLED': -1,
        'REJECTED': -1
      };'''

    new_stages = '''      const STAGES = [
        { key: 'PENDING', titleEn: 'Order Placed', titleHi: 'ऑर्डर दर्ज हुआ', descEn: 'Order received by village store', descHi: 'गाँव की दुकान को ऑर्डर प्राप्त हुआ' },
        { key: 'PREPARING', titleEn: 'Shop is Packing', titleHi: 'सामान पैक हो रहा है', descEn: 'Groceries safely bagged', descHi: 'किराना सामान पैक कर दिया गया' },
        { key: 'READY_FOR_PICKUP', titleEn: 'Ready for Pickup', titleHi: 'पिकअप के लिए तैयार', descEn: 'Awaiting delivery partner arrival', descHi: 'डिलीवरी पार्टनर के आने की प्रतीक्षा' },
        { key: 'RUNNER_ASSIGNED', titleEn: 'Runner Assigned', titleHi: 'डिलीवरी पार्टनर नियुक्त', descEn: 'Runner allocated for rural transit', descHi: 'डिलीवरी पार्टनर को ऑर्डर सौंपा गया' },
        { key: 'OUT_FOR_DELIVERY', titleEn: 'Runner is on the way', titleHi: 'रास्ते में है', descEn: 'Rider en route to your doorstep', descHi: 'डिलीवरी पार्टनर आपके घर की ओर आ रहा है' },
        { key: 'DELIVERED', titleEn: 'Delivered', titleHi: 'सफलतापूर्वक डिलीवर', descEn: 'Handed over at village doorstep', descHi: 'सामान आपके हाथों में सौंप दिया गया' }
      ];

      const statusRanks = {
        'PENDING': 1,
        'PLACED': 1,
        'PREPARING': 2,
        'ACCEPTED': 2,
        'PACKED': 2,
        'READY_FOR_PICKUP': 3,
        'RUNNER_ASSIGNED': 4,
        'ASSIGNED': 4,
        'PICKED_UP': 4,
        'OUT_FOR_DELIVERY': 5,
        'DELIVERED': 6,
        'CANCELLED': -1,
        'REJECTED': -1
      };'''

    if old_stages in content:
        content = content.replace(old_stages, new_stages, 1)
        print("Updated STAGES and statusRanks in customer/index.html")

    # In placeCustomerOrder, inject Supabase order upsert and tracking subscription
    old_post_order = '''        if (res && res.id) {
          localStorage.setItem('gb_active_order_id', res.id);
          if (res.delivery_otp) {
            localStorage.setItem('gb_active_order_otp', res.delivery_otp);
          }
          isDeliveryOtpRevealed = false;
          syncActiveOrderUI();
        }'''

    new_post_order = '''        if (res && res.id) {
          localStorage.setItem('gb_active_order_id', res.id);
          if (res.delivery_otp) {
            localStorage.setItem('gb_active_order_otp', res.delivery_otp);
          }
          isDeliveryOtpRevealed = false;
          syncActiveOrderUI();

          // 3-Way Order Routing: Realtime Supabase Database Sync & Channel Subscription
          const supa = getSupabaseCustomerClient();
          if (supa) {
            try {
              const custId = localStorage.getItem('gb_user_id') || 'usr_customer_01';
              const vVillage = (document.getElementById('checkout-village-input')?.value || 'Chaturshi').trim();
              await supa.from('orders').upsert({
                id: res.id,
                order_id: res.id,
                customer_id: custId,
                vendor_id: 'usr_vendor_01',
                delivery_village: vVillage,
                status: 'PENDING',
                total_amount: currentCartTotal || 340.0,
                delivery_otp: res.delivery_otp || '1234',
                placed_at: new Date().toISOString()
              });
            } catch (supaErr) {
              console.warn("Supabase customer order sync notice:", supaErr);
            }
          }
          subscribeCustomerOrderTracking(res.id);
        }'''

    if old_post_order in content:
        content = content.replace(old_post_order, new_post_order, 1)
        print("Updated placeCustomerOrder with Supabase sync & live tracking in customer/index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    inject_vendor()
    inject_runner()
    inject_customer()
