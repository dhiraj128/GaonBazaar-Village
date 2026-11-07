import os
import re

CUSTOMER_PATH = "public_web/customer/index.html"
RUNNER_PATH = "public_web/runner/index.html"
API_KEY = "AIzaSyBqHZrBX7WMEw2vt5COVwfK7a4lZpGapMc"

def patch_customer():
    with open(CUSTOMER_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ensure GMAPS_API_KEY is defined at top of script
    if 'var GMAPS_API_KEY =' not in content:
        script_pattern = r'(<script>\s*// -{10,}\s*// QUIET AUDIO HELPERS)'
        replacement = r'<script>\n    var GMAPS_API_KEY = "' + API_KEY + r'";\n    window.GMAPS_API_KEY = GMAPS_API_KEY;\n\n    // ---------------------------------------------------------------------------\n    // QUIET AUDIO HELPERS'
        content = re.sub(script_pattern, replacement, content, count=1)

    # 2. Replace pollRunnerChatMessages, renderCustomerRunnerChat, appendDetectingIndicator, sendCustomerChatMessage, and shareCustomerConfirmedLocationPin
    chat_block_start = content.find("async function pollRunnerChatMessages() {")
    chat_block_end = content.find("function openCustomerDirectionsMap() {", chat_block_start)
    if chat_block_start == -1 or chat_block_end == -1:
        raise Exception("Could not find customer chat block boundaries")

    new_chat_functions = f'''async function pollRunnerChatMessages() {{
      const activeOrderId = localStorage.getItem('gb_active_order_id') || 'GB-8921';
      const container = document.getElementById('chat-messages-container');
      if (!container) return;

      let msgs = [];
      try {{
        const res = await apiRequest(`/api/v1/orders/${{activeOrderId}}/messages`, 'GET');
        if (Array.isArray(res) && res.length > 0) {{
          msgs = res;
          localStorage.setItem('gb_chat_msgs_' + activeOrderId, JSON.stringify(msgs));
        }}
      }} catch (err) {{
        console.debug("Chat sync notice (using local/cached messages):", err);
      }}

      if (msgs.length === 0) {{
        const cached = localStorage.getItem('gb_chat_msgs_' + activeOrderId);
        if (cached) {{
          try {{ msgs = JSON.parse(cached); }} catch(e) {{}}
        }}
      }}

      if (msgs.length === 0 && (!window.customerOrderMessages || window.customerOrderMessages.length === 0)) {{
        msgs = [
          {{
            id: "msg_init_runner",
            sender_role: "runner",
            sender_name: "Delivery Partner",
            message_type: "TEXT",
            content: "Namaste! I have picked up your groceries from Sharma Kirana. I am riding towards your village now.",
            created_at: new Date(Date.now() - 300000).toISOString()
          }}
        ];
      }} else if (window.customerOrderMessages && window.customerOrderMessages.length > 0) {{
        // Merge any locally created messages
        msgs = [...msgs, ...window.customerOrderMessages.filter(lm => !msgs.some(m => m.id === lm.id))];
      }}

      renderCustomerRunnerChat(msgs);
    }}

    function renderCustomerRunnerChat(msgs) {{
      const container = document.getElementById('chat-messages-container');
      if (!container) return;

      const hasDetectingIndicator = !!document.getElementById('chat-gps-detecting-indicator');

      container.innerHTML = '';
      if (!msgs || msgs.length === 0) {{
        container.innerHTML = `
          <div class="p-3 bg-slate-50 rounded-xl text-center text-slate-500 text-xs">
            Start a conversation with your delivery partner. Share directions or landmark tips.
          </div>
        `;
        if (hasDetectingIndicator) appendDetectingIndicator(container);
        return;
      }}

      const currentUserId = localStorage.getItem('gb_customer_id');

      msgs.forEach(m => {{
        const isMe = m.sender_role === 'CUSTOMER' || m.sender_id === currentUserId || m.sender_role === 'customer';
        const timeStr = m.created_at ? new Date(m.created_at).toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }}) : new Date().toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }});

        if (m.message_type === 'LOCATION_PIN') {{
          const lat = Number(m.latitude) || 26.2315;
          const lng = Number(m.longitude) || 85.3610;
          let readableAddress = m.location_title || m.content || 'Near Primary School, Chaturshi';
          if (readableAddress.startsWith('Exact delivery location pin confirmed') || readableAddress.startsWith('Exact delivery location:')) {{
            readableAddress = (activeCustomerAddress && (activeCustomerAddress.landmark || activeCustomerAddress.village))
              ? `${{activeCustomerAddress.landmark ? activeCustomerAddress.landmark + ', ' : ''}}${{activeCustomerAddress.village || 'Chaturshi'}}`
              : 'Near Primary School, Chaturshi';
          }}
          const mapImgUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${{lat}},${{lng}}&zoom=15&size=300x150&markers=color:red%7C${{lat}},${{lng}}&key={API_KEY}`;
          const navUrl = `https://www.google.com/maps/dir/?api=1&destination=${{lat}},${{lng}}&travelmode=driving&dir_action=navigate`;

          const bubble = document.createElement('div');
          bubble.className = `flex ${{isMe ? 'justify-end' : 'justify-start'}} w-full`;
          bubble.innerHTML = `
            <a href="${{navUrl}}" target="_blank" rel="noopener noreferrer" class="block max-w-[85%] ${{isMe ? 'bg-emerald-50 border border-emerald-300 text-emerald-950 rounded-tr-xs' : 'bg-slate-100 border border-slate-200 text-slate-800 rounded-tl-xs'}} p-2.5 rounded-2xl shadow-xs hover:shadow-md transition group no-underline">
              <div class="flex items-center justify-between pb-1.5 mb-1.5 border-b ${{isMe ? 'border-emerald-200' : 'border-slate-200'}}">
                <div class="flex items-center space-x-1.5 text-xs font-bold ${{isMe ? 'text-emerald-900' : 'text-slate-800'}}">
                  <i data-lucide="map-pin" class="w-4 h-4 ${{isMe ? 'text-emerald-600' : 'text-indigo-600'}}"></i>
                  <span>${{isMe ? 'Doorstep Location Shared' : 'Delivery Location'}}</span>
                </div>
                <span class="text-[10px] font-bold ${{isMe ? 'text-emerald-700' : 'text-slate-600'}} flex items-center space-x-0.5">
                  <span>Navigate</span>
                  <i data-lucide="navigation" class="w-2.5 h-2.5 ml-0.5"></i>
                </span>
              </div>
              <div class="relative overflow-hidden rounded-md border border-slate-200/80 mb-2">
                <img src="${{mapImgUrl}}" alt="Google Map Location" class="rounded-md w-full h-auto block object-cover" loading="lazy" />
              </div>
              <p class="text-xs font-semibold ${{isMe ? 'text-emerald-950' : 'text-slate-900'}} leading-tight">${{readableAddress}}</p>
              <div class="flex items-center justify-between pt-1 mt-1 text-[9px] ${{isMe ? 'text-emerald-700' : 'text-slate-400'}}">
                <span class="font-medium">Tap map for turn-by-turn navigation</span>
                <span class="font-mono">${{timeStr}}</span>
              </div>
            </a>
          `;
          container.appendChild(bubble);
        }} else {{
          const bubble = document.createElement('div');
          bubble.className = `flex ${{isMe ? 'justify-end' : 'justify-start'}} w-full`;
          bubble.innerHTML = `
            <div class="max-w-[80%] ${{isMe ? 'bg-emerald-600 text-white rounded-tr-xs' : 'bg-slate-100 text-slate-800 rounded-tl-xs'}} p-2.5 rounded-2xl shadow-2xs text-xs space-y-1">
              <p>${{m.content || ''}}</p>
              <span class="text-[9px] ${{isMe ? 'text-emerald-200' : 'text-slate-400'}} block text-right font-mono">${{timeStr}}</span>
            </div>
          `;
          container.appendChild(bubble);
        }}
      }});

      if (hasDetectingIndicator) appendDetectingIndicator(container);

      container.scrollTo({{ top: container.scrollHeight, behavior: 'smooth' }});
      if (window.lucide && typeof lucide.createIcons === 'function') {{
        lucide.createIcons();
      }}
    }}

    function appendDetectingIndicator(container) {{
      if (!container || document.getElementById('chat-gps-detecting-indicator')) return;
      const ind = document.createElement('div');
      ind.id = 'chat-gps-detecting-indicator';
      ind.className = 'flex justify-end w-full my-1.5';
      ind.innerHTML = `
        <div class="flex items-center space-x-2 bg-emerald-50 border border-emerald-300 text-emerald-800 px-3 py-2 rounded-2xl rounded-tr-xs shadow-xs text-xs font-semibold animate-pulse">
          <svg class="animate-spin h-4 w-4 text-emerald-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Detecting exact location...</span>
        </div>
      `;
      container.appendChild(ind);
      container.scrollTo({{ top: container.scrollHeight, behavior: 'smooth' }});
    }}

    async function sendCustomerChatMessage() {{
      const inp = document.getElementById('chat-input-text');
      const text = inp ? inp.value.trim() : '';
      const activeOrderId = localStorage.getItem('gb_active_order_id') || 'GB-8921';

      if (!text) return;
      inp.value = '';

      const msgObj = {{
        id: "msg_" + Date.now(),
        order_id: activeOrderId,
        sender_role: "CUSTOMER",
        sender_name: "You",
        message_type: "TEXT",
        content: text,
        created_at: new Date().toISOString()
      }};

      window.customerOrderMessages = window.customerOrderMessages || [];
      window.customerOrderMessages.push(msgObj);
      try {{
        const cached = JSON.parse(localStorage.getItem('gb_chat_msgs_' + activeOrderId) || '[]');
        cached.push(msgObj);
        localStorage.setItem('gb_chat_msgs_' + activeOrderId, JSON.stringify(cached));
      }} catch(e) {{}}

      try {{
        await apiRequest(`/api/v1/orders/${{activeOrderId}}/messages`, 'POST', {{
          message_type: 'TEXT',
          content: text
        }});
      }} catch (err) {{
        console.warn("API message send notice:", err);
      }} finally {{
        await pollRunnerChatMessages();
      }}
    }}

    async function shareCustomerConfirmedLocationPin() {{
      const activeOrderId = localStorage.getItem('gb_active_order_id') || 'GB-8921';
      
      const modal = document.getElementById('modal-runner-chat');
      if (modal && modal.classList.contains('hidden')) {{
        openRunnerChatModal();
      }}

      const container = document.getElementById('chat-messages-container');
      if (container) {{
        appendDetectingIndicator(container);
      }}

      let lat = 26.2315;
      let lng = 85.3610;
      if (activeCustomerAddress && activeCustomerAddress.latitude) {{
        lat = activeCustomerAddress.latitude;
        lng = activeCustomerAddress.longitude;
      }} else if (window.detectedLatitude && window.detectedLongitude) {{
        lat = window.detectedLatitude;
        lng = window.detectedLongitude;
      }}

      if (navigator.geolocation) {{
        try {{
          const position = await new Promise((resolve, reject) => {{
            navigator.geolocation.getCurrentPosition(
              resolve,
              reject,
              {{ enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }}
            );
          }});
          if (position && position.coords) {{
            lat = position.coords.latitude;
            lng = position.coords.longitude;
          }}
        }} catch (posErr) {{
          console.warn("GPS detection fallback:", posErr.message || posErr);
        }}
      }}

      let readableAddress = "Near Primary School, Chaturshi";
      if (activeCustomerAddress && (activeCustomerAddress.landmark || activeCustomerAddress.village)) {{
        readableAddress = `${{activeCustomerAddress.landmark ? activeCustomerAddress.landmark + ', ' : ''}}${{activeCustomerAddress.village || 'Chaturshi'}}`;
      }} else if (window.activeCustomerAddress && (window.activeCustomerAddress.landmark || window.activeCustomerAddress.village)) {{
        readableAddress = `${{window.activeCustomerAddress.landmark ? window.activeCustomerAddress.landmark + ', ' : ''}}${{window.activeCustomerAddress.village || 'Chaturshi'}}`;
      }}

      try {{
        const geoResp = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?latlng=${{lat}},${{lng}}&key={API_KEY}`);
        if (geoResp.ok) {{
          const geoData = await geoResp.json();
          if (geoData.results && geoData.results.length > 0) {{
            const formatted = geoData.results[0].formatted_address;
            if (formatted) {{
              const cleaned = formatted.replace(/, India$/, '').replace(/[0-9]{{6}},?/, '').trim();
              if (cleaned.length > 5) readableAddress = cleaned;
            }}
          }}
        }}
      }} catch (geoErr) {{
        console.debug("Geocode network fallback:", geoErr);
      }}

      const locationMsg = {{
        id: "msg_" + Date.now(),
        order_id: activeOrderId,
        sender_role: "CUSTOMER",
        sender_name: "You",
        message_type: "LOCATION_PIN",
        latitude: lat,
        longitude: lng,
        location_title: readableAddress,
        content: `Exact delivery location: ${{readableAddress}}`,
        created_at: new Date().toISOString()
      }};

      window.customerOrderMessages = window.customerOrderMessages || [];
      window.customerOrderMessages.push(locationMsg);
      try {{
        const cached = JSON.parse(localStorage.getItem('gb_chat_msgs_' + activeOrderId) || '[]');
        cached.push(locationMsg);
        localStorage.setItem('gb_chat_msgs_' + activeOrderId, JSON.stringify(cached));
      }} catch(e) {{}}

      try {{
        await apiRequest(`/api/v1/orders/${{activeOrderId}}/messages`, 'POST', {{
          message_type: 'LOCATION_PIN',
          latitude: lat,
          longitude: lng,
          location_title: readableAddress,
          content: `Exact delivery location: ${{readableAddress}}`
        }});

        if (window.BroadcastChannel) {{
          try {{
            const bc = new BroadcastChannel('gaonbazaar_order_sync');
            bc.postMessage({{
              type: 'LOCATION_PIN_SHARED',
              order_id: activeOrderId,
              latitude: lat,
              longitude: lng,
              location_title: readableAddress
            }});
          }} catch(e) {{}}
        }}
        toastSuccess("Exact doorstep location pin shared with delivery partner!");
      }} catch (err) {{
        console.warn("API message send notice:", err);
      }} finally {{
        const ind = document.getElementById('chat-gps-detecting-indicator');
        if (ind) ind.remove();
        await pollRunnerChatMessages();
      }}
    }}

    function shareCustomerLiveLocation() {{
      shareCustomerConfirmedLocationPin();
    }}

    '''

    content = content[:chat_block_start] + new_chat_functions + content[chat_block_end:]

    with open(CUSTOMER_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("Customer app updated.")

if __name__ == "__main__":
    patch_customer()
