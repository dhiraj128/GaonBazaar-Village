import re

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Google Maps JavaScript API in <head>
gmaps_script = '''  <!-- Google Maps JavaScript API (Rural Hybrid Satellite View) -->
  <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBqHZrBX7WMEw2vt5COVwfK7a4lZpGapMc&libraries=places,geometry&loading=async" async defer></script>'''

if 'maps.googleapis.com/maps/api/js' not in html:
    html = html.replace(
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"',
        gmaps_script + '\n  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"'
    )
    print("1. Added Google Maps JS API script tag to <head>")
else:
    print("1. Google Maps JS API script already present in <head>")

# 2. Update CSS for #location-picker-canvas
old_css_pat = re.compile(r'#location-picker-canvas\s*\{[^}]*\}', re.DOTALL)
new_css = '''#location-picker-canvas {
      min-height: 220px;
      width: 100%;
      background-color: #0f172a;
    }
    #location-picker-canvas img {
      max-width: none !important;
    }'''

if old_css_pat.search(html):
    html = old_css_pat.sub(new_css, html, count=1)
    print("2. Updated CSS for #location-picker-canvas")
else:
    print("2. Warning: #location-picker-canvas CSS pattern not found")

# 3. Update subtitle and container comment in modal markup
old_subtitle = '<p class="text-[10px] text-slate-500">Drag marker or tap map to set doorstep</p>'
new_subtitle = '<p class="text-[10px] text-slate-500">Hybrid Satellite View • Drag pin to your doorstep</p>'
if old_subtitle in html:
    html = html.replace(old_subtitle, new_subtitle)
    print("3. Updated modal subtitle")

# 4. Replace Leaflet location picker functions with Google Maps Hybrid Satellite implementation
old_picker_logic = '''    function openLocationMapPickerModal() {
      openModal('modal-location-map-picker');
      initLocationMapPicker();
      setTimeout(() => { if (locationPickerMap) locationPickerMap.invalidateSize(); }, 50);
      setTimeout(() => { if (locationPickerMap) locationPickerMap.invalidateSize(); }, 150);
      setTimeout(() => { if (locationPickerMap) locationPickerMap.invalidateSize(); }, 350);
    }

    function initLocationMapPicker() {
      const container = document.getElementById('location-picker-canvas');
      if (!container || typeof L === 'undefined') return;

      const initLat = selectedPickerLat || activeCustomerAddress.latitude || window.detectedLatitude || 26.2315;
      const initLng = selectedPickerLng || activeCustomerAddress.longitude || window.detectedLongitude || 85.3610;

      selectedPickerLat = initLat;
      selectedPickerLng = initLng;

      if (!locationPickerMap) {
        locationPickerMap = L.map('location-picker-canvas', {
          zoomControl: true,
          attributionControl: false
        }).setView([initLat, initLng], 15);
        window.locationPickerMap = locationPickerMap;

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19
        }).addTo(locationPickerMap);

        const customPin = L.divIcon({
          className: 'custom-pin-icon',
          html: '<div style="background-color: #059669; color: white; width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.35);">📍</div>',
          iconSize: [34, 34],
          iconAnchor: [17, 34]
        });

        locationPickerMarker = L.marker([initLat, initLng], {
          draggable: true,
          icon: customPin
        }).addTo(locationPickerMap);

        locationPickerMarker.on('dragend', function (e) {
          const pos = e.target.getLatLng();
          selectedPickerLat = pos.lat;
          selectedPickerLng = pos.lng;
          updatePickerGeofence(pos.lat, pos.lng);
        });

        locationPickerMap.on('click', function (e) {
          selectedPickerLat = e.latlng.lat;
          selectedPickerLng = e.latlng.lng;
          locationPickerMarker.setLatLng(e.latlng);
          updatePickerGeofence(e.latlng.lat, e.latlng.lng);
        });
      } else {
        locationPickerMap.invalidateSize();
        locationPickerMap.setView([initLat, initLng], 15);
        if (locationPickerMarker) locationPickerMarker.setLatLng([initLat, initLng]);
      }

      updatePickerGeofence(initLat, initLng);
    }'''

new_picker_logic = '''    function openLocationMapPickerModal() {
      openModal('modal-location-map-picker');
      // Delay map initialization until container is attached and visible in DOM
      requestAnimationFrame(() => {
        setTimeout(() => {
          initLocationMapPicker();
        }, 120);
      });
    }

    function initLocationMapPicker() {
      const container = document.getElementById('location-picker-canvas');
      if (!container) return;

      const initLat = Number(selectedPickerLat || (activeCustomerAddress && activeCustomerAddress.latitude) || window.detectedLatitude || 26.2315);
      const initLng = Number(selectedPickerLng || (activeCustomerAddress && activeCustomerAddress.longitude) || window.detectedLongitude || 85.3610);

      selectedPickerLat = initLat;
      selectedPickerLng = initLng;

      if (typeof google === 'undefined' || !google.maps || !google.maps.Map) {
        console.warn("Google Maps SDK loading, waiting for initialization...");
        setTimeout(initLocationMapPicker, 150);
        return;
      }

      const mapOptions = {
        center: { lat: initLat, lng: initLng },
        zoom: 18,
        mapTypeId: google.maps.MapTypeId.HYBRID,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        rotateControl: false,
        scaleControl: true,
        gestureHandling: 'greedy'
      };

      if (!locationPickerMap || typeof locationPickerMap.setCenter !== 'function') {
        locationPickerMap = new google.maps.Map(container, mapOptions);
        window.locationPickerMap = locationPickerMap;

        locationPickerMarker = new google.maps.Marker({
          position: { lat: initLat, lng: initLng },
          map: locationPickerMap,
          draggable: true,
          animation: google.maps.Animation.DROP,
          title: "Drag to pin delivery doorstep"
        });

        locationPickerMarker.addListener('dragend', function (e) {
          const lat = e.latLng.lat();
          const lng = e.latLng.lng();
          selectedPickerLat = lat;
          selectedPickerLng = lng;
          updatePickerGeofence(lat, lng);
        });

        locationPickerMap.addListener('click', function (e) {
          const lat = e.latLng.lat();
          const lng = e.latLng.lng();
          selectedPickerLat = lat;
          selectedPickerLng = lng;
          if (locationPickerMarker) {
            locationPickerMarker.setPosition(e.latLng);
          }
          updatePickerGeofence(lat, lng);
        });

        if (window.ResizeObserver && !window._pickerResizeObs) {
          window._pickerResizeObs = new ResizeObserver(() => {
            if (locationPickerMap && typeof locationPickerMap.setCenter === 'function') {
              google.maps.event.trigger(locationPickerMap, 'resize');
            }
          });
          window._pickerResizeObs.observe(container);
        }
      } else {
        google.maps.event.trigger(locationPickerMap, 'resize');
        locationPickerMap.setCenter({ lat: initLat, lng: initLng });
        locationPickerMap.setZoom(18);
        locationPickerMap.setMapTypeId(google.maps.MapTypeId.HYBRID);
        if (locationPickerMarker) {
          locationPickerMarker.setPosition({ lat: initLat, lng: initLng });
        }
      }

      // Re-trigger resize event and re-center after parent container layout finishes
      requestAnimationFrame(() => {
        if (locationPickerMap && typeof locationPickerMap.setCenter === 'function') {
          google.maps.event.trigger(locationPickerMap, 'resize');
          locationPickerMap.setCenter({ lat: initLat, lng: initLng });
        }
      });
      setTimeout(() => {
        if (locationPickerMap && typeof locationPickerMap.setCenter === 'function') {
          google.maps.event.trigger(locationPickerMap, 'resize');
          locationPickerMap.setCenter({ lat: selectedPickerLat, lng: selectedPickerLng });
        }
      }, 200);

      updatePickerGeofence(initLat, initLng);
    }'''

# Normalize newlines for matching
normalized_html = html.replace('\r\n', '\n')
if old_picker_logic in normalized_html:
    normalized_html = normalized_html.replace(old_picker_logic, new_picker_logic)
    print("4. Replaced Leaflet initLocationMapPicker with Google Maps Hybrid Satellite logic")
else:
    print("4. Warning: old_picker_logic not matched directly")

# 5. Update useCurrentGpsInPicker
old_gps_snip = '''          if (locationPickerMap) {
            locationPickerMap.invalidateSize();
            locationPickerMap.setView([lat, lng], 16);
            if (locationPickerMarker) locationPickerMarker.setLatLng([lat, lng]);
          }'''

new_gps_snip = '''          if (locationPickerMap && typeof locationPickerMap.setCenter === 'function') {
            google.maps.event.trigger(locationPickerMap, 'resize');
            locationPickerMap.setCenter({ lat: lat, lng: lng });
            locationPickerMap.setZoom(18);
            locationPickerMap.setMapTypeId(google.maps.MapTypeId.HYBRID);
            if (locationPickerMarker) locationPickerMarker.setPosition({ lat: lat, lng: lng });
          } else if (locationPickerMap && typeof locationPickerMap.setView === 'function') {
            locationPickerMap.invalidateSize();
            locationPickerMap.setView([lat, lng], 18);
            if (locationPickerMarker) locationPickerMarker.setLatLng([lat, lng]);
          }'''

if old_gps_snip in normalized_html:
    normalized_html = normalized_html.replace(old_gps_snip, new_gps_snip)
    print("5. Updated useCurrentGpsInPicker for Google Maps Hybrid")

# 6. Update clearPickerMarkerPin
old_clear_snip = '''      if (locationPickerMarker && locationPickerMap) {
        locationPickerMarker.setLatLng([defLat, defLng]);
        locationPickerMap.setView([defLat, defLng], 15);
      }'''

new_clear_snip = '''      if (locationPickerMarker && locationPickerMap && typeof locationPickerMap.setCenter === 'function') {
        google.maps.event.trigger(locationPickerMap, 'resize');
        locationPickerMarker.setPosition({ lat: defLat, lng: defLng });
        locationPickerMap.setCenter({ lat: defLat, lng: defLng });
        locationPickerMap.setZoom(18);
        locationPickerMap.setMapTypeId(google.maps.MapTypeId.HYBRID);
      } else if (locationPickerMarker && locationPickerMap && typeof locationPickerMap.setView === 'function') {
        locationPickerMarker.setLatLng([defLat, defLng]);
        locationPickerMap.setView([defLat, defLng], 18);
      }'''

if old_clear_snip in normalized_html:
    normalized_html = normalized_html.replace(old_clear_snip, new_clear_snip)
    print("6. Updated clearPickerMarkerPin for Google Maps Hybrid")

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(normalized_html)

print("Saved public_web/customer/index.html successfully.")
