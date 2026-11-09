import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove style="display: none;" from screen-onboarding-1
old_s1 = '<div id="screen-onboarding-1" class="app-screen flex-1 p-6 flex flex-col justify-between hidden" style="display: none;">'
new_s1 = '<div id="screen-onboarding-1" class="app-screen flex-1 p-6 flex flex-col justify-between hidden">'
if old_s1 in content:
    content = content.replace(old_s1, new_s1)
    print("SUCCESS: Removed hardcoded inline display:none from screen-onboarding-1")
else:
    # also check if hidden class was omitted or different order
    import re
    content = re.sub(
        r'<div id="screen-onboarding-1" class="([^"]*)" style="display:\s*none;?"',
        r'<div id="screen-onboarding-1" class="\1"',
        content
    )
    print("APPLIED: regex clean on screen-onboarding-1 inline style")

# 2. Add SectionErrorBoundary class definition before navigateTo
error_boundary_code = """
    // ===========================================================================
    // SECTION ERROR BOUNDARY COMPONENT
    // Protects functional areas (Dashboard, Orders, Inventory, Ledger, Account)
    // from crashing the application into a white screen of death.
    // ===========================================================================
    class SectionErrorBoundary {
      static wrap(sectionId, renderFn, sectionTitle = 'Section') {
        const container = document.getElementById(sectionId);
        if (!container) return;
        try {
          renderFn();
        } catch (err) {
          console.error(`[ErrorBoundary] Caught error in ${sectionId} (${sectionTitle}):`, err);
          SectionErrorBoundary.renderFallback(container, sectionTitle, err);
        }
      }

      static renderFallback(container, sectionTitle, err) {
        if (!container) return;
        container.classList.remove('hidden');
        container.style.display = 'block';
        container.innerHTML = `
          <div class="section-error-boundary p-6 text-center space-y-3 bg-red-50/90 border border-red-200 rounded-2xl m-4 shadow-sm animate-fade-in">
            <div class="w-12 h-12 bg-red-100 text-red-600 rounded-full mx-auto flex items-center justify-center shadow-xs">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
            </div>
            <h3 class="text-sm font-bold text-slate-900">Something went wrong loading this section. Please refresh.</h3>
            <p class="text-xs text-slate-600 leading-relaxed max-w-xs mx-auto">
              ${sectionTitle} encountered an unexpected render issue. You can refresh this section or continue navigating the rest of GaonBazaar.
            </p>
            <div class="pt-2 flex items-center justify-center space-x-2">
              <button onclick="location.reload()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs active:scale-95 transition">
                Refresh Section
              </button>
              <button onclick="switchDashboardTab('orders')" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl shadow-xs active:scale-95 transition">
                Go to Orders
              </button>
            </div>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
      }
    }
    window.SectionErrorBoundary = SectionErrorBoundary;

    // Global Window Error Boundary
    window.addEventListener('error', function(event) {
      console.error('[Global Error Boundary]:', event.error || event.message);
      const viewport = document.getElementById('main-viewport');
      if (viewport) {
        const activeTabs = Array.from(document.querySelectorAll('.dashboard-tab')).filter(t => !t.classList.contains('hidden') && t.style.display !== 'none');
        const activeScreens = Array.from(document.querySelectorAll('.app-screen')).filter(s => !s.classList.contains('hidden') && s.style.display !== 'none');
        if (activeTabs.length === 0 && activeScreens.length === 0) {
          console.warn('[Global Error Boundary] Recovering from empty viewport...');
          if (state.currentScreen === 'dashboard') {
            switchDashboardTab(state.activeTab || 'orders', false);
          } else {
            navigateTo(state.currentScreen || 'onboarding-1', false);
          }
        }
      }
    });
"""

# Insert SectionErrorBoundary right before `function navigateTo`
if 'class SectionErrorBoundary' not in content:
    nav_idx = content.find('function navigateTo(screenId, pushHistory = true)')
    if nav_idx != -1:
        content = content[:nav_idx] + error_boundary_code + '\n    ' + content[nav_idx:]
        print("SUCCESS: Injected SectionErrorBoundary class & global error handler")
    else:
        print("ERROR: Could not find function navigateTo")

# 3. Update navigateTo to ensure target.style.display = ''
old_nav_block = """    function navigateTo(screenId, pushHistory = true) {
      document.querySelectorAll('.app-screen').forEach(s => s.classList.add('hidden'));
      document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.add('hidden'));

      let target = document.getElementById('screen-' + screenId);
      if (!target) {
        console.warn('Target screen not found: screen-' + screenId + ', falling back to screen-onboarding-1');
        target = document.getElementById('screen-onboarding-1');
        screenId = 'onboarding-1';
      }
      const bottomNav = document.getElementById('bottom-tabs');
      const backBtn = document.getElementById('nav-back-btn');

      if (target) {
        target.classList.remove('hidden');
        state.currentScreen = screenId;
        if (bottomNav) bottomNav.classList.add('hidden');"""

new_nav_block = """    function navigateTo(screenId, pushHistory = true) {
      document.querySelectorAll('.app-screen').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      document.querySelectorAll('.dashboard-tab').forEach(t => {
        t.classList.add('hidden');
        t.style.display = 'none';
      });

      let target = document.getElementById('screen-' + screenId);
      if (!target) {
        console.warn('Target screen not found: screen-' + screenId + ', falling back to screen-onboarding-1');
        target = document.getElementById('screen-onboarding-1');
        screenId = 'onboarding-1';
      }
      const bottomNav = document.getElementById('bottom-tabs');
      const backBtn = document.getElementById('nav-back-btn');

      if (target) {
        target.classList.remove('hidden');
        target.style.display = '';
        state.currentScreen = screenId;
        if (bottomNav) {
          bottomNav.classList.add('hidden');
          bottomNav.style.display = 'none';
        }"""

if old_nav_block in content:
    content = content.replace(old_nav_block, new_nav_block)
    print("SUCCESS: Updated navigateTo with display reset")
else:
    print("WARNING: old_nav_block not found exactly, checking variant")

# 4. Update switchDashboardTab to reset targetTab.style.display = '' and wrap in Error Boundary
old_switch_tab_start = """    function switchDashboardTab(tabName, pushHistory = true) {
      state.activeTab = tabName;
      state.currentScreen = 'dashboard';

      // STRICT ROUTING: Suppress all onboarding screens (including language selector) on the dashboard
      document.querySelectorAll('.app-screen').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      const s1 = document.getElementById('screen-onboarding-1');
      if (s1) { s1.classList.add('hidden'); s1.style.display = 'none'; }

      document.querySelectorAll('.dashboard-tab').forEach(t => {
        t.classList.add('hidden');
        t.style.display = 'none';
      });
      
      const targetTab = document.getElementById('tab-' + tabName);
      if (targetTab) {
        targetTab.classList.remove('hidden');
      }

      document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('text-emerald-600', 'font-bold');
        btn.classList.add('text-slate-500', 'font-medium');
      });
      const activeBtn = document.getElementById('tab-btn-' + tabName);
      if (activeBtn) {
        activeBtn.classList.remove('text-slate-500', 'font-medium');
        activeBtn.classList.add('text-emerald-600', 'font-bold');
      }

      if (pushHistory) {
        history.pushState({ screen: 'dashboard', tab: tabName, view: 'dashboard' }, '', '#dashboard-' + tabName);
      }

      window.scrollTo(0, 0);
      lucide.createIcons();
    }"""

new_switch_tab_start = """    function switchDashboardTab(tabName, pushHistory = true) {
      state.activeTab = tabName;
      state.currentScreen = 'dashboard';

      // STRICT ROUTING: Suppress all onboarding screens (including language selector) on the dashboard
      document.querySelectorAll('.app-screen').forEach(s => {
        s.classList.add('hidden');
        s.style.display = 'none';
      });
      const s1 = document.getElementById('screen-onboarding-1');
      if (s1) { s1.classList.add('hidden'); s1.style.display = 'none'; }

      // Hide all tabs
      document.querySelectorAll('.dashboard-tab').forEach(t => {
        t.classList.add('hidden');
        t.style.display = 'none';
      });
      
      const targetTab = document.getElementById('tab-' + tabName);
      if (targetTab) {
        targetTab.classList.remove('hidden');
        targetTab.style.display = '';
      }

      document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('text-emerald-600', 'font-bold');
        btn.classList.add('text-slate-500', 'font-medium');
      });
      const activeBtn = document.getElementById('tab-btn-' + tabName);
      if (activeBtn) {
        activeBtn.classList.remove('text-slate-500', 'font-medium');
        activeBtn.classList.add('text-emerald-600', 'font-bold');
      }

      // Safeguard tab render cycles inside SectionErrorBoundary
      SectionErrorBoundary.wrap('tab-' + tabName, () => {
        if (tabName === 'inventory') {
          if (typeof renderSampleBarcodes === 'function') renderSampleBarcodes();
          if (typeof renderLooseItemChips === 'function') renderLooseItemChips();
        } else if (tabName === 'orders') {
          if (typeof updateOrdersUIFromData === 'function') updateOrdersUIFromData();
        }
        if (window.lucide) lucide.createIcons();
      }, tabName.charAt(0).toUpperCase() + tabName.slice(1) + ' Section');

      if (pushHistory) {
        history.pushState({ screen: 'dashboard', tab: tabName, view: 'dashboard' }, '', '#dashboard-' + tabName);
      }

      window.scrollTo(0, 0);
      if (window.lucide) lucide.createIcons();
    }"""

if old_switch_tab_start in content:
    content = content.replace(old_switch_tab_start, new_switch_tab_start)
    print("SUCCESS: Updated switchDashboardTab with style.display='' and SectionErrorBoundary wrap")
else:
    print("WARNING: old_switch_tab_start not found exactly")

# 5. Update openDashboard to reset bottomNav.style.display = ''
old_open_dash = """      const bottomNav = document.getElementById('bottom-tabs');
      if (bottomNav) bottomNav.classList.remove('hidden');"""

new_open_dash = """      const bottomNav = document.getElementById('bottom-tabs');
      if (bottomNav) {
        bottomNav.classList.remove('hidden');
        bottomNav.style.display = '';
      }"""

if old_open_dash in content:
    content = content.replace(old_open_dash, new_open_dash)
    print("SUCCESS: Updated openDashboard with bottomNav display reset")
else:
    print("WARNING: old_open_dash not found exactly")

with open('public_web/vendor/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved all updates to public_web/vendor/index.html")
