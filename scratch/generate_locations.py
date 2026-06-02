import json
import os

# Base coordinates for major cities
CITY_COORDS = {
    "Hà Nội": {"lat": 21.0285, "lon": 105.8542},
    "TP. Hồ Chí Minh": {"lat": 10.7769, "lon": 106.7009},
    "Đà Nẵng": {"lat": 16.0544, "lon": 108.2022},
    "Hải Phòng": {"lat": 20.8449, "lon": 106.6881},
    "Cần Thơ": {"lat": 10.0371, "lon": 105.7882}
}

# Dictionary of district -> lists of wards
LOCATIONS_DATA = {
    "Hà Nội": {
        "Quận Hoàn Kiếm": [
            "Phường Chương Dương", "Phường Cửa Đông", "Phường Cửa Nam", "Phường Đồng Xuân",
            "Phường Hàng Bạc", "Phường Hàng Bài", "Phường Hàng Bồ", "Phường Hàng Bông",
            "Phường Hàng Buồm", "Phường Hàng Đào", "Phường Hàng Gai", "Phường Hàng Mã",
            "Phường Lý Thái Tổ", "Phường Phan Chu Trinh", "Phường Phúc Tân",
            "Phường Trần Hưng Đạo", "Phường Tràng Tiền", "Phường Hàng Trống"
        ],
        "Quận Ba Đình": [
            "Phường Cống Vị", "Phường Điện Biên", "Phường Đội Cấn", "Phường Giảng Võ",
            "Phường Kim Mã", "Phường Liễu Giai", "Phường Ngọc Hà", "Phường Nguyễn Trung Trực",
            "Phường Phúc Xá", "Phường Quán Thánh", "Phường Thành Công", "Phường Trúc Bạch",
            "Phường Vĩnh Phúc"
        ],
        "Quận Đống Đa": [
            "Phường Cát Linh", "Phường Hàng Bột", "Phường Khâm Thiên", "Phường Khương Thượng",
            "Phường Kim Liên", "Phường Láng Hạ", "Phường Láng Thượng", "Phường Nam Đồng",
            "Phường Ngã Tư Sở", "Phường Ô Chợ Dừa", "Phường Phương Liên", "Phường Phương Mai",
            "Phường Quang Trung", "Phường Quốc Tử Giám", "Phường Thịnh Quang", "Phường Thổ Quan",
            "Phường Trung Liệt", "Phường Trung Phụng", "Phường Trung Tự", "Phường Văn Chương",
            "Phường Văn Miếu"
        ],
        "Quận Cầu Giấy": [
            "Phường Dịch Vọng", "Phường Dịch Vọng Hậu", "Phường Mai Dịch", "Phường Nghĩa Đô",
            "Phường Nghĩa Tân", "Phường Quan Hoa", "Phường Trung Hòa", "Phường Yên Hòa"
        ],
        "Quận Hai Bà Trưng": [
            "Phường Bách Khoa", "Phường Bạch Đằng", "Phường Bạch Mai", "Phường Cầu Dền",
            "Phường Đống Mác", "Phường Đồng Nhân", "Phường Đồng Tâm", "Phường Lê Đại Hành",
            "Phường Minh Khai", "Phường Nguyễn Du", "Phường Phạm Đình Hổ", "Phường Phố Huế",
            "Phường Quỳnh Lôi", "Phường Quỳnh Mai", "Phường Thanh Lương", "Phường Thanh Nhàn",
            "Phường Trương Định", "Phường Vĩnh Tuy"
        ],
        "Quận Tây Hồ": [
            "Phường Bưởi", "Phường Nhật Tân", "Phường Phú Thượng", "Phường Quảng An",
            "Phường Tứ Liên", "Phường Xuân La", "Phường Yên Phụ", "Phường Thụy Khuê"
        ],
        "Quận Thanh Xuân": [
            "Phường Hạ Đình", "Phường Khương Đình", "Phường Khương Mai", "Phường Khương Trung",
            "Phường Kim Giang", "Phường Nhân Chính", "Phường Phương Liệt", "Phường Thanh Xuân Bắc",
            "Phường Thanh Xuân Nam", "Phường Thanh Xuân Trung", "Phường Thượng Đình"
        ],
        "Quận Hoàng Mai": [
            "Phường Đại Kim", "Phường Định Công", "Phường Giáp Bát", "Phường Hoàng Liệt",
            "Phường Hoàng Văn Thụ", "Phường Lĩnh Nam", "Phường Mai Động", "Phường Tân Mai",
            "Phường Thanh Trì", "Phường Thịnh Liệt", "Phường Trần Phú", "Phường Tương Mai",
            "Phường Vĩnh Hưng", "Phường Yên Sở"
        ],
        "Quận Long Biên": [
            "Phường Bồ Đề", "Phường Cự Khối", "Phường Đức Giang", "Phường Gia Thụy",
            "Phường Giang Biên", "Phường Long Biên", "Phường Ngọc Lâm", "Phường Ngọc Thụy",
            "Phường Phúc Đồng", "Phường Phúc Lợi", "Phường Sài Đồng", "Phường Thạch Bàn",
            "Phường Thượng Thanh", "Phường Việt Hưng"
        ],
        "Quận Hà Đông": [
            "Phường Biên Giang", "Phường Đồng Mai", "Phường Yên Nghĩa", "Phường Dương Nội",
            "Phường Hà Cầu", "Phường La Khê", "Phường Mộ Lao", "Phường Nguyễn Trãi",
            "Phường Phú La", "Phường Phú Lãm", "Phường Phú Lương", "Phường Phúc La",
            "Phường Quang Trung", "Phường Vạn Phúc", "Phường Văn Quán", "Phường Yết Kiêu",
            "Phường Kiến Hưng"
        ],
        "Quận Nam Từ Liêm": [
            "Phường Cầu Diễn", "Phường Đại Mỗ", "Phường Mễ Trì", "Phường Mỹ Đình 1",
            "Phường Mỹ Đình 2", "Phường Phú Đô", "Phường Tây Mỗ", "Phường Phương Canh",
            "Phường Trung Văn", "Phường Xuân Phương"
        ],
        "Quận Bắc Từ Liêm": [
            "Phường Cổ Nhuế 1", "Phường Cổ Nhuế 2", "Phường Đức Thắng", "Phường Đông Ngạc",
            "Phường Thụy Phương", "Phường Liên Mạc", "Phường Thượng Cát", "Phường Tây Tựu",
            "Phường Minh Khai", "Phường Phú Diễn", "Phường Phúc Diễn", "Phường Xuân Đỉnh",
            "Phường Xuân Tảo"
        ]
    },
    "TP. Hồ Chí Minh": {
        "Quận 1": [
            "Phường Bến Nghé", "Phường Bến Thành", "Phường Cô Giang", "Phường Cầu Kho",
            "Phường Cầu Ông Lãnh", "Phường Đa Kao", "Phường Nguyễn Cư Trinh",
            "Phường Nguyễn Thái Bình", "Phường Phạm Ngũ Lão", "Phường Tân Định"
        ],
        "Quận 3": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường Võ Thị Sáu", "Phường 9", "Phường 10", "Phường 11",
            "Phường 12", "Phường 13", "Phường 14"
        ],
        "Quận 4": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 6",
            "Phường 8", "Phường 9", "Phường 10", "Phường 13", "Phường 14",
            "Phường 15", "Phường 16", "Phường 18"
        ],
        "Quận 5": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường 6", "Phường 7", "Phường 8", "Phường 9", "Phường 10",
            "Phường 11", "Phường 12", "Phường 13", "Phường 14"
        ],
        "Quận 6": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường 6", "Phường 7", "Phường 8", "Phường 9", "Phường 10",
            "Phường 11", "Phường 12", "Phường 13", "Phường 14"
        ],
        "Quận 7": [
            "Phường Bình Thuận", "Phường Phú Mỹ", "Phường Phú Thuận", "Phường Tân Hưng",
            "Phường Tân Kiểng", "Phường Tân Phong", "Phường Tân Phú", "Phường Tân Quy",
            "Phường Tân Thuận Đông", "Phường Tân Thuận Tây"
        ],
        "Quận 8": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường 6", "Phường 7", "Phường 8", "Phường 9", "Phường 10",
            "Phường 11", "Phường 12", "Phường 13", "Phường 14", "Phường 15",
            "Phường 16"
        ],
        "Quận 10": [
            "Phường 1", "Phường 2", "Phường 4", "Phường 5", "Phường 6",
            "Phường 7", "Phường 8", "Phường 9", "Phường 10", "Phường 11",
            "Phường 12", "Phường 13", "Phường 14", "Phường 15"
        ],
        "Quận 11": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường 6", "Phường 7", "Phường 8", "Phường 9", "Phường 10",
            "Phường 11", "Phường 12", "Phường 13", "Phường 14", "Phường 15",
            "Phường 16"
        ],
        "Quận 12": [
            "Phường An Phú Đông", "Phường Đông Hưng Thuận", "Phường Hiệp Thành",
            "Phường Tân Chánh Hiệp", "Phường Tân Hưng Thuận", "Phường Tân Thới Hiệp",
            "Phường Tân Thới Nhất", "Phường Thạnh Lộc", "Phường Thạnh Xuân",
            "Phường Thới An", "Phường Trung Mỹ Tây"
        ],
        "Quận Bình Thạnh": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 5", "Phường 6",
            "Phường 7", "Phường 11", "Phường 12", "Phường 13", "Phường 14",
            "Phường 15", "Phường 17", "Phường 19", "Phường 21", "Phường 22",
            "Phường 24", "Phường 25", "Phường 26", "Phường 27", "Phường 28"
        ],
        "Quận Gò Vấp": [
            "Phường 1", "Phường 3", "Phường 4", "Phường 5", "Phường 6",
            "Phường 7", "Phường 8", "Phường 9", "Phường 10", "Phường 11",
            "Phường 12", "Phường 13", "Phường 14", "Phường 15", "Phường 16",
            "Phường 17"
        ],
        "Quận Phú Nhuận": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường 7", "Phường 8", "Phường 9", "Phường 10", "Phường 11",
            "Phường 13", "Phường 15", "Phường 17"
        ],
        "Quận Tân Bình": [
            "Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5",
            "Phường 6", "Phường 7", "Phường 8", "Phường 9", "Phường 10",
            "Phường 11", "Phường 12", "Phường 13", "Phường 14", "Phường 15"
        ],
        "Quận Tân Phú": [
            "Phường Hiệp Tân", "Phường Hòa Thạnh", "Phường Phú Thạnh",
            "Phường Phú Thọ Hòa", "Phường Phú Trung", "Phường Sơn Kỳ",
            "Phường Tân Quý", "Phường Tân Sơn Nhì", "Phường Tân Thành",
            "Phường Tân Thới Hòa", "Phường Tây Thạnh"
        ],
        "Quận Bình Tân": [
            "Phường An Lạc", "Phường An Lạc A", "Phường Bình Hưng Hòa",
            "Phường Bình Hưng Hòa A", "Phường Bình Hưng Hòa B", "Phường Bình Trị Đông",
            "Phường Bình Trị Đông A", "Phường Bình Trị Đông B", "Phường Tân Tạo",
            "Phường Tân Tạo A"
        ],
        "TP. Thủ Đức": [
            "Phường An Khánh", "Phường An Lợi Đông", "Phường An Phú", "Phường Bình Chiểu",
            "Phường Bình Thọ", "Phường Cát Lái", "Phường Hiệp Bình Chánh",
            "Phường Hiệp Bình Phước", "Phường Hiệp Phú", "Phường Linh Chiểu",
            "Phường Linh Đông", "Phường Linh Tây", "Phường Linh Trung",
            "Phường Linh Xuân", "Phường Long Bình", "Phường Long Phước",
            "Phường Long Thạnh Mỹ", "Phường Long Trường", "Phường Phú Hữu",
            "Phường Phước Bình", "Phường Phước Long A", "Phường Phước Long B",
            "Phường Tam Bình", "Phường Tam Phú", "Phường Thạnh Mỹ Lợi",
            "Phường Thảo Điền", "Phường Thủ Thiêm", "Phường Trường Thọ",
            "Phường Trường Thạnh"
        ]
    },
    "Đà Nẵng": {
        "Quận Hải Châu": [
            "Phường Bình Hiên", "Phường Bình Thuận", "Phường Hải Châu 1",
            "Phường Hải Châu 2", "Phường Hòa Cường Bắc", "Phường Hòa Cường Nam",
            "Phường Hòa Thuận Đông", "Phường Hòa Thuận Tây", "Phường Nam Dương",
            "Phường Phước Ninh", "Phường Thạch Thang", "Phường Thanh Bình",
            "Phường Thuận Phước"
        ],
        "Quận Thanh Khê": [
            "Phường An Khê", "Phường Chính Gián", "Phường Hòa Khê", "Phường Tam Thuận",
            "Phường Tân Chính", "Phường Thạc Gián", "Phường Thanh Khê Đông",
            "Phường Thanh Khê Tây", "Phường Vĩnh Trung", "Phường Xuân Hà"
        ],
        "Quận Sơn Trà": [
            "Phường An Hải Bắc", "Phường An Hải Đông", "Phường An Hải Tây",
            "Phường Mân Thái", "Phường Nại Hiên Đông", "Phường Phước Mỹ",
            "Phường Thọ Quang"
        ],
        "Quận Ngũ Hành Sơn": [
            "Phường Hòa Hải", "Phường Hòa Quý", "Phường Khuê Mỹ", "Phường Mỹ An"
        ],
        "Quận Liên Chiểu": [
            "Phường Hòa Hiệp Bắc", "Phường Hòa Hiệp Nam", "Phường Hòa Khánh Bắc",
            "Phường Hòa Khánh Nam", "Phường Hòa Minh"
        ],
        "Quận Cẩm Lệ": [
            "Phường Hòa An", "Phường Hòa Phát", "Phường Hòa Thọ Đông",
            "Phường Hòa Thọ Tây", "Phường Hòa Xuân", "Phường Khuê Trung"
        ]
    },
    "Hải Phòng": {
        "Quận Hồng Bàng": [
            "Phường Hoàng Văn Thụ", "Phường Minh Khai", "Phường Phan Bội Châu",
            "Phường Phạm Hồng Thái", "Phường Quán Toan", "Phường Sở Dầu",
            "Phường Thượng Lý", "Phường Trại Chuối", "Phường Hùng Vương"
        ],
        "Quận Ngô Quyền": [
            "Phường Cầu Đất", "Phường Đông Hải 1", "Phường Đông Hải 2",
            "Phường Đông Khê", "Phường Lạc Viên", "Phường Lê Lợi",
            "Phường Máy Chai", "Phường Máy Tơ", "Phường Vạn Mỹ",
            "Phường Gia Viên", "Phường Đằng Giang", "Phường Lạch Tray"
        ],
        "Quận Lê Chân": [
            "Phường An Biên", "Phường An Dương", "Phường Cát Dài",
            "Phường Đông Hải", "Phường Hàng Kênh", "Phường Nghĩa Xá",
            "Phường Niệm Nghĩa", "Phường Trần Nguyên Hãn", "Phường Hồ Nam",
            "Phường Trại Cau", "Phường Dư Hàng", "Phường Dư Hàng Kênh",
            "Phường Kênh Dương", "Phường Vĩnh Niệm"
        ],
        "Quận Hải An": [
            "Phường Cát Bi", "Phường Đằng Hải", "Phường Đằng Lâm",
            "Phường Đông Hải 1", "Phường Đông Hải 2", "Phường Nam Hải",
            "Phường Thành Tô", "Phường Tràng Cát"
        ],
        "Quận Kiến An": [
            "Phường Bắc Sơn", "Phường Đồng Hòa", "Phường Lãm Hà",
            "Phường Nam Sơn", "Phường Ngọc Sơn", "Phường Phù Liễn",
            "Phường Quán Trữ", "Phường Trần Thành Ngọ", "Phường Tràng Minh",
            "Phường Văn Đẩu"
        ],
        "Quận Đồ Sơn": [
            "Phường Bàng La", "Phường Hải Sơn", "Phường Hợp Đức",
            "Phường Minh Đức", "Phường Ngọc Xuyên", "Phường Vạn Hương"
        ],
        "Quận Dương Kinh": [
            "Phường Anh Dũng", "Phường Đa Phúc", "Phường Hưng Đạo",
            "Phường Hải Thành", "Phường Hòa Nghĩa", "Phường Tân Thành"
        ]
    },
    "Cần Thơ": {
        "Quận Ninh Kiều": [
            "Phường An Bình", "Phường An Cư", "Phường An Hòa", "Phường An Khánh",
            "Phường An Nghiệp", "Phường An Phú", "Phường Cái Khế", "Phường Hưng Lợi",
            "Phường Tân An", "Phường Thới Bình", "Phường Xuân Khánh"
        ],
        "Quận Bình Thủy": [
            "Phường An Thới", "Phường Bình Thủy", "Phường Bùi Hữu Nghĩa",
            "Phường Long Hòa", "Phường Long Tuyền", "Phường Thới An Đông",
            "Phường Trà An", "Phường Trà Nóc"
        ],
        "Quận Cái Răng": [
            "Phường Ba Láng", "Phường Hưng Phú", "Phường Hưng Thạnh",
            "Phường Lê Bình", "Phường Phú Thứ", "Phường Tân Phú", "Phường Thường Thạnh"
        ],
        "Quận Ô Môn": [
            "Phường Châu Văn Liêm", "Phường Phước Thới", "Phường Thới An",
            "Phường Thới Hòa", "Phường Thới Long", "Phường Trường Lạc", "Phường Định Môn"
        ],
        "Quận Thốt Nốt": [
            "Phường Tân Lộc", "Phường Tân Hưng", "Phường Thốt Nốt",
            "Phường Thạnh Hòa", "Phường Thới Thuận", "Phường Thuận An",
            "Phường Thuận Hưng", "Phường Trung Nhứt", "Phường Trung Kiên"
        ]
    }
}

# Generate location object with offsets from center coords
output_locations = {}
for city, districts in LOCATIONS_DATA.items():
    center = CITY_COORDS[city]
    output_locations[city] = {}
    
    # Calculate a grid of offsets for districts
    dist_list = list(districts.keys())
    for d_idx, district in enumerate(dist_list):
        output_locations[city][district] = {}
        
        # District offset (spread districts out around city center)
        # 1 degree of lat/lon is ~111km. Spread districts within ~5-15km of center
        d_lat_offset = ((d_idx % 4) - 1.5) * 0.04
        d_lon_offset = ((d_idx // 4) - 1.5) * 0.04
        
        d_center_lat = center["lat"] + d_lat_offset
        d_center_lon = center["lon"] + d_lon_offset
        
        wards = districts[district]
        for w_idx, ward in enumerate(wards):
            # Spread wards out within ~2-5km of district center
            w_lat_offset = ((w_idx % 5) - 2) * 0.006
            w_lon_offset = ((w_idx // 5) - 2) * 0.006
            
            w_lat = round(d_center_lat + w_lat_offset, 4)
            w_lon = round(d_center_lon + w_lon_offset, 4)
            
            output_locations[city][district][ward] = {"lat": w_lat, "lon": w_lon}

# Write back to JS format
js_content = f"""/**
 * vietnam_locations.js
 * Dữ liệu phân cấp địa điểm Việt Nam: Tỉnh/Thành → Quận/Huyện → Phường/Xã
 * Mỗi Phường/Xã bao gồm tọa độ GPS (lat, lon) để tính khoảng cách Haversine.
 */
const VIETNAM_LOCATIONS = {json.dumps(output_locations, ensure_ascii=False, indent=2)};

/**
 * Lấy danh sách tỉnh/thành phố
 */
function getProvinces() {{
  return Object.keys(VIETNAM_LOCATIONS).sort();
}}

/**
 * Lấy danh sách quận/huyện theo tỉnh/thành phố
 */
function getDistricts(province) {{
  if (!VIETNAM_LOCATIONS[province]) return [];
  return Object.keys(VIETNAM_LOCATIONS[province]).sort();
}}

/**
 * Lấy danh sách phường/xã theo tỉnh/thành phố và quận/huyện
 */
function getWards(province, district) {{
  if (!VIETNAM_LOCATIONS[province]) return [];
  if (!VIETNAM_LOCATIONS[province][district]) return [];
  return Object.keys(VIETNAM_LOCATIONS[province][district]).sort();
}}

/**
 * Lấy tọa độ GPS của phường/xã
 */
function getWardCoords(province, district, ward) {{
  try {{
    return VIETNAM_LOCATIONS[province][district][ward];
  }} catch (e) {{
    return null;
  }}
}}

/**
 * Tính khoảng cách Haversine giữa hai tọa độ (đơn vị km)
 */
function haversineKm(lat1, lon1, lat2, lon2) {{
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}}

/**
 * Tìm phường/xã gần nhất với tọa độ GPS đầu vào
 * Trả về {{ province, district, ward, lat, lon }}
 */
function findNearestWard(userLat, userLon) {{
  let best = null;
  let bestDist = Infinity;
  for (const [province, districts] of Object.entries(VIETNAM_LOCATIONS)) {{
    for (const [district, wards] of Object.entries(districts)) {{
      for (const [ward, coords] of Object.entries(wards)) {{
        const d = haversineKm(userLat, userLon, coords.lat, coords.lon);
        if (d < bestDist) {{
          bestDist = d;
          best = {{ province, district, ward, lat: coords.lat, lon: coords.lon }};
        }}
      }}
    }}
  }}
  return best;
}}
"""

target_path = r"c:\Users\namkhanh1\.gemini\antigravity-ide\scratch\dat-lich-kham-online\static\js\vietnam_locations.js"
with open(target_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print("Generated location database successfully!")
