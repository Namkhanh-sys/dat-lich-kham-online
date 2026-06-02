/**
 * MedBooking — định vị thật: GPS trình duyệt, geocoding qua server, khoảng cách phòng khám thật.
 */
(function () {
    const DEFAULT_CENTER = [21.0285, 105.8542];
    const DEFAULT_ZOOM = 6;
    const CLINIC_ICON = L.divIcon({
        className: 'clinic-map-icon',
        html: '<div style="background:#dc2626;color:#fff;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:14px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.3);">+</div>',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
    });

    let map, marker, accuracyCircle, radiusCircle;
    let clinicMarkers = [];
    let acTimeout = null;

    function el(id) { return document.getElementById(id); }

    function setHint(html, color) {
        const hint = el('location-hint');
        if (!hint) return;
        hint.innerHTML = html;
        hint.style.color = color || 'var(--text-muted)';
        hint.style.fontStyle = 'normal';
    }

    function hasValidCoords() {
        const lat = parseFloat(el('lat')?.value);
        const lon = parseFloat(el('lon')?.value);
        return !isNaN(lat) && !isNaN(lon);
    }

    function saveCoords(lat, lon) {
        if (el('lat')) el('lat').value = lat;
        if (el('lon')) el('lon').value = lon;
    }

    async function apiSearch(query, limit) {
        const r = await fetch(`/api/geocode/search?q=${encodeURIComponent(query)}&limit=${limit || 5}`);
        const data = await r.json();
        if (!data.ok) throw new Error(data.error || 'Geocode failed');
        return data.results || [];
    }

    async function apiReverse(lat, lon) {
        const r = await fetch(`/api/geocode/reverse?lat=${lat}&lon=${lon}`);
        const data = await r.json();
        if (!data.ok) throw new Error(data.error || 'Reverse failed');
        return data.result;
    }

    async function apiNearbyClinics() {
        if (!hasValidCoords()) return [];
        const lat = el('lat').value;
        const lon = el('lon').value;
        syncFormLocationFields();
        const province = el('formProvince')?.value || el('province')?.value || '';
        const r = await fetch(
            `/api/clinics/nearby?lat=${lat}&lon=${lon}&province=${encodeURIComponent(province)}`
        );
        const data = await r.json();
        return data.ok ? (data.clinics || []) : [];
    }

    function initMap() {
        map = L.map('map', { center: DEFAULT_CENTER, zoom: DEFAULT_ZOOM, zoomControl: true });
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap',
        }).addTo(map);

        map.on('click', function (e) {
            applyUserPosition(e.latlng.lat, e.latlng.lng, false);
        });
    }

    function clearClinicMarkers() {
        clinicMarkers.forEach(m => map.removeLayer(m));
        clinicMarkers = [];
    }

    async function showNearbyClinics() {
        clearClinicMarkers();
        if (!hasValidCoords()) return;
        try {
            const clinics = await apiNearbyClinics();
            clinics.slice(0, 10).forEach(c => {
                const m = L.marker([parseFloat(c.lat), parseFloat(c.lon)], { icon: CLINIC_ICON })
                    .addTo(map)
                    .bindPopup(
                        `<strong>${c.name}</strong><br>${c.address}<br><em>Cách bạn ${c.distance_km} km</em>`
                    );
                clinicMarkers.push(m);
            });
        } catch (e) {
            console.warn('Không tải được phòng khám gần:', e);
        }
    }

    function placeMarker(lat, lon, flyTo, popupText, accuracyMeters) {
        if (marker) {
            marker.setLatLng([lat, lon]);
        } else {
            marker = L.marker([lat, lon], { draggable: true }).addTo(map);
            marker.on('dragend', function (e) {
                const pos = e.target.getLatLng();
                applyUserPosition(pos.lat, pos.lng, false);
            });
        }

        if (popupText) {
            marker.bindPopup(popupText).openPopup();
        } else {
            marker.closePopup();
        }

        if (accuracyCircle) {
            map.removeLayer(accuracyCircle);
            accuracyCircle = null;
        }
        if (accuracyMeters && accuracyMeters > 0) {
            accuracyCircle = L.circle([lat, lon], {
                color: '#2563eb',
                fillColor: '#3b82f6',
                fillOpacity: 0.15,
                radius: accuracyMeters,
            }).addTo(map);
        }

        if (radiusCircle) {
            radiusCircle.setLatLng([lat, lon]);
        } else {
            radiusCircle = L.circle([lat, lon], {
                color: '#16a34a',
                fillColor: '#16a34a',
                fillOpacity: 0.08,
                radius: 8000,
            }).addTo(map);
        }

        if (flyTo) {
            const zoom = accuracyMeters && accuracyMeters < 50 ? 16 : Math.max(map.getZoom(), 14);
            map.flyTo([lat, lon], zoom, { duration: 0.8 });
        }

        const overlay = el('map-overlay');
        if (overlay) overlay.classList.add('hidden');
    }

    function normalize(s) {
        if (!s) return '';
        return s.toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[đĐ]/g, 'd')
            .replace(/\s+/g, ' ').trim();
    }

    function matchProvinceFromNominatim(addr) {
        if (!addr) return null;
        const candidates = [
            addr.state, addr.city, addr.town, addr.county, addr.region
        ].filter(Boolean);

        const provinces = typeof getProvinces === 'function' ? getProvinces() : [];
        for (const raw of candidates) {
            const n = normalize(raw);
            for (const p of provinces) {
                const pn = normalize(p);
                if (n.includes(pn) || pn.includes(n)) return p;
            }
        }
        if (normalize(addr.state || '').includes('ha noi')) return 'Hà Nội';
        if (normalize(addr.state || '').includes('ho chi minh')) return 'TP. Hồ Chí Minh';
        if (normalize(addr.city || '').includes('ho chi minh')) return 'TP. Hồ Chí Minh';
        if (normalize(addr.state || '').includes('da nang')) return 'Đà Nẵng';
        if (normalize(addr.state || '').includes('can tho')) return 'Cần Thơ';
        return null;
    }

    function findWardByName(displayName, addressObj) {
        let text = (displayName || '').toLowerCase();
        if (addressObj) text += ' ' + JSON.stringify(addressObj).toLowerCase();

        const cleanStr = (s) => {
            if (!s) return '';
            return normalize(s)
                .replace(/\btp\.?\b/g, '').replace(/\bthanh pho\b/g, '')
                .replace(/\bquan\b/g, '').replace(/\bhuyen\b/g, '')
                .replace(/\bthi xa\b/g, '').replace(/\bphuong\b/g, '')
                .replace(/\bthi tran\b/g, '')
                .replace(/\s+/g, ' ').trim();
        };

        const ct = cleanStr(text);
        for (const prov in VIETNAM_LOCATIONS) {
            if (!ct.includes(cleanStr(prov))) continue;
            for (const dist in VIETNAM_LOCATIONS[prov]) {
                if (!ct.includes(cleanStr(dist))) continue;
                for (const ward in VIETNAM_LOCATIONS[prov][dist]) {
                    if (ct.includes(cleanStr(ward))) return { province: prov, district: dist, ward };
                }
            }
        }
        for (const prov in VIETNAM_LOCATIONS) {
            for (const dist in VIETNAM_LOCATIONS[prov]) {
                if (!ct.includes(cleanStr(dist))) continue;
                for (const ward in VIETNAM_LOCATIONS[prov][dist]) {
                    if (ct.includes(cleanStr(ward))) return { province: prov, district: dist, ward };
                }
            }
        }
        return null;
    }

    function syncFormLocationFields() {
        if (el('formProvince')) el('formProvince').value = el('province')?.value || '';
        if (el('formDistrict')) el('formDistrict').value = el('district')?.value || '';
        if (el('formWard')) el('formWard').value = el('ward')?.value || '';
    }

    function setDropdowns(province, district, ward) {
        const provSel = el('province');
        if (!provSel || !province) return;
        provSel.value = province;
        populateDistricts(province);
        const distSel = el('district');
        if (district && distSel) {
            distSel.value = district;
            populateWards(province, district);
        }
        if (ward) el('ward').value = ward;
        syncFormLocationFields();
    }

    function buildDisplayAddress(addr, displayName) {
        if (!addr) return displayName || '';
        const parts = [];
        if (addr.house_number) parts.push(addr.house_number);
        if (addr.road) parts.push(addr.road);
        if (addr.suburb || addr.quarter) parts.push(addr.suburb || addr.quarter);
        if (addr.city_district || addr.county) parts.push(addr.city_district || addr.county);
        if (addr.city || addr.town) parts.push(addr.city || addr.town);
        if (addr.state) parts.push(addr.state);
        return parts.length ? parts.join(', ') : (displayName || '');
    }

    function showResult(addressText, lat, lon) {
        setHint(`📍 ${addressText}`, 'var(--success)');
        if (el('location-address')) el('location-address').textContent = addressText;
        if (el('location-coords')) {
            el('location-coords').textContent =
                `Tọa độ GPS: ${Number(lat).toFixed(6)}, ${Number(lon).toFixed(6)}`;
        }
        if (el('location-result')) el('location-result').style.display = 'block';
    }

    async function applyNominatimResult(data, lat, lon, accuracyMeters) {
        saveCoords(lat, lon);
        placeMarker(lat, lon, true, null, accuracyMeters);

        const displayAddr = buildDisplayAddress(data.address, data.display_name);
        if (el('addressInput') && data.display_name) {
            el('addressInput').value = displayAddr || data.display_name;
        }

        const matched = findWardByName(data.display_name, data.address);
        if (matched) {
            setDropdowns(matched.province, matched.district, matched.ward);
        } else {
            const prov = matchProvinceFromNominatim(data.address);
            if (prov) {
                setDropdowns(prov, '', '');
            }
        }

        syncFormLocationFields();
        showResult(displayAddr, lat, lon);
        await showNearbyClinics();
    }

    async function applyUserPosition(lat, lon, isGps, accuracyMeters) {
        setHint('🔍 Đang xác định địa chỉ thật...', '#d97706');
        saveCoords(lat, lon);
        placeMarker(lat, lon, true, isGps ? `Vị trí GPS (${accuracyMeters ? '±' + Math.round(accuracyMeters) + 'm' : ''})` : null, accuracyMeters);

        try {
            const data = await apiReverse(lat, lon);
            if (data) {
                await applyNominatimResult(data, lat, lon, accuracyMeters);
            } else {
                showResult(`Tọa độ: ${lat.toFixed(5)}, ${lon.toFixed(5)}`, lat, lon);
                await showNearbyClinics();
            }
        } catch (e) {
            showResult(`Tọa độ: ${lat.toFixed(5)}, ${lon.toFixed(5)}`, lat, lon);
            setHint('⚠️ Không tra được địa chỉ. Tọa độ GPS vẫn được dùng để tính khoảng cách.', '#d97706');
            await showNearbyClinics();
        }
    }

    window.gpsLocate = function gpsLocate() {
        const btn = el('btnGPS');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spin">⏳</span>';
        }
        setHint('⏳ Đang lấy vị trí GPS (cần quyền truy cập vị trí)...', '#d97706');

        const onSuccess = (pos) => {
            if (btn) btn.disabled = false;
            resetGPSBtn(true);
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const acc = pos.coords.accuracy || 0;
            if (acc > 80) {
                setHint(`⚠️ GPS có sai số ~${acc.toFixed(0)}m. Kéo marker trên bản đồ để chỉnh chính xác hơn.`, '#d97706');
            }
            applyUserPosition(lat, lon, true, acc);
        };

        const onFail = (msg) => {
            setHint('📡 GPS thất bại, thử định vị qua IP...', '#d97706');
            fetch('https://ipinfo.io/json')
                .then(r => r.json())
                .then(data => {
                    if (data && data.loc) {
                        const [lat, lon] = data.loc.split(',').map(Number);
                        resetGPSBtn(true);
                        if (btn) btn.disabled = false;
                        applyUserPosition(lat, lon, true, 5000);
                    } else throw new Error('no loc');
                })
                .catch(() => {
                    resetGPSBtn(false);
                    if (btn) btn.disabled = false;
                    setHint(msg + ' Hãy tìm địa chỉ hoặc nhấp bản đồ.', 'var(--danger)');
                });
        };

        if (!navigator.geolocation) {
            onFail('❌ Trình duyệt không hỗ trợ GPS.');
            return;
        }

        navigator.geolocation.getCurrentPosition(
            onSuccess,
            err => {
                if (err.code === 1) {
                    resetGPSBtn(false);
                    if (btn) btn.disabled = false;
                    setHint('🔒 Bạn đã từ chối quyền vị trí. Hãy bật lại trong cài đặt trình duyệt.', 'var(--danger)');
                } else {
                    onFail('❌ Không lấy được GPS.');
                }
            },
            { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
        );
    };

    function resetGPSBtn(success) {
        const btn = el('btnGPS');
        if (!btn) return;
        btn.style.color = success ? 'var(--success)' : 'var(--primary)';
        btn.innerHTML = '<svg width="22" height="22" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/></svg>';
    }

    window.searchAddress = async function searchAddress() {
        const input = el('addressInput');
        const query = input?.value.trim();
        if (!query) return;

        const btn = el('btnSearch');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Đang tìm...';
        }
        setHint('⏳ Đang tìm địa chỉ...', '#d97706');

        try {
            const results = await apiSearch(query, 1);
            if (results.length) {
                const item = results[0];
                await applyNominatimResult(item, parseFloat(item.lat), parseFloat(item.lon), null);
            } else {
                setHint('❌ Không tìm thấy địa chỉ. Thử nhập cụ thể hơn hoặc nhấp bản đồ.', 'var(--danger)');
            }
        } catch (e) {
            setHint('❌ Lỗi tìm kiếm địa chỉ. Thử lại sau.', 'var(--danger)');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/></svg> Tìm';
            }
        }
    };

    window.onAddressInput = function onAddressInput(input) {
        const query = input.value.trim();
        const box = el('suggestions');
        clearTimeout(acTimeout);
        if (query.length < 3) {
            box.style.display = 'none';
            return;
        }
        acTimeout = setTimeout(async () => {
            try {
                const results = await apiSearch(query, 5);
                box.innerHTML = '';
                if (results.length) {
                    results.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'suggestion-item';
                        div.textContent = item.display_name;
                        div.onclick = () => {
                            input.value = item.display_name;
                            box.style.display = 'none';
                            applyNominatimResult(item, parseFloat(item.lat), parseFloat(item.lon), null);
                        };
                        box.appendChild(div);
                    });
                    box.style.display = 'block';
                } else {
                    box.style.display = 'none';
                }
            } catch (e) {
                box.style.display = 'none';
            }
        }, 400);
    };

    window.onProvinceChange = function () {
        populateDistricts(el('province').value);
        syncFormLocationFields();
    };

    window.onDistrictChange = function () {
        populateWards(el('province').value, el('district').value);
        syncFormLocationFields();
    };

    window.onWardChange = async function () {
        const province = el('province').value;
        const district = el('district').value;
        const ward = el('ward').value;
        if (!province || !district || !ward) return;

        syncFormLocationFields();
        setHint('🔍 Đang lấy tọa độ phường/xã...', '#d97706');
        const query = `${ward}, ${district}, ${province}, Việt Nam`;
        try {
            const results = await apiSearch(query, 1);
            if (results.length) {
                const lat = parseFloat(results[0].lat);
                const lon = parseFloat(results[0].lon);
                await applyNominatimResult(results[0], lat, lon, null);
            }
        } catch (e) {
            setHint('❌ Không xác định được tọa độ phường/xã.', 'var(--danger)');
        }
    };

    function populateDistricts(province) {
        const distSel = el('district');
        const wardSel = el('ward');
        distSel.innerHTML = '<option value="" disabled selected>-- Chọn Quận/Huyện --</option>';
        wardSel.innerHTML = '<option value="" disabled selected>-- Chọn Phường/Xã --</option>';
        wardSel.disabled = true;
        if (!province) { distSel.disabled = true; return; }
        getDistricts(province).forEach(d => distSel.add(new Option(d, d)));
        distSel.disabled = false;
    }

    function populateWards(province, district) {
        const wardSel = el('ward');
        wardSel.innerHTML = '<option value="" disabled selected>-- Chọn Phường/Xã --</option>';
        if (!district) { wardSel.disabled = true; return; }
        getWards(province, district).forEach(w => wardSel.add(new Option(w, w)));
        wardSel.disabled = false;
    }

    function initProvinces() {
        const sel = el('province');
        if (!sel) return;
        getProvinces().forEach(p => sel.add(new Option(p, p)));
        const pre = window.MEDBOOKING_PRESELECT || {};
        if (pre.province) {
            sel.value = pre.province;
            populateDistricts(pre.province);
            if (pre.district) {
                el('district').value = pre.district;
                populateWards(pre.province, pre.district);
                if (pre.ward) el('ward').value = pre.ward;
            }
        }
        if (pre.lat && pre.lon) {
            applyUserPosition(parseFloat(pre.lat), parseFloat(pre.lon), false, null);
        }
    }

    function bindSymptomForm() {
        const form = el('symptomSearchForm');
        if (!form) return;
        form.addEventListener('submit', function (e) {
            syncFormLocationFields();
            if (!hasValidCoords()) {
                e.preventDefault();
                setHint('⚠️ Vui lòng xác định vị trí (GPS / tìm địa chỉ / bản đồ) trước khi tìm bác sĩ.', 'var(--danger)');
                el('location-result')?.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    window.goToDisease = function (diseaseId) {
        if (!hasValidCoords()) {
            alert('Vui lòng xác định vị trí của bạn trước (nút GPS hoặc tìm địa chỉ).');
            return;
        }
        syncFormLocationFields();
        const params = new URLSearchParams({
            lat: el('lat').value,
            lon: el('lon').value,
            province: el('province')?.value || el('formProvince')?.value || '',
            district: el('district')?.value || el('formDistrict')?.value || '',
            ward: el('ward')?.value || el('formWard')?.value || '',
        });
        window.location.href = `/disease/${diseaseId}?${params}`;
    };

    document.addEventListener('click', e => {
        const box = el('suggestions');
        const input = el('addressInput');
        if (box && e.target !== box && !box.contains(e.target) && e.target !== input) {
            box.style.display = 'none';
        }
    });

    window.addEventListener('load', function () {
        initMap();
        initProvinces();
        bindSymptomForm();
        setHint('* Bấm 📍 GPS để định vị chính xác như Google Maps (trên điện thoại tốt nhất).', 'var(--text-muted)');
    });
})();
