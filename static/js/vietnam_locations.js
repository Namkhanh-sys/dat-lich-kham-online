/**
 * vietnam_locations.js
 * Dữ liệu phân cấp địa điểm Việt Nam: Tỉnh/Thành → Quận/Huyện → Phường/Xã
 * Mỗi Phường/Xã bao gồm tọa độ GPS (lat, lon) để tính khoảng cách Haversine.
 */
const VIETNAM_LOCATIONS = {
  "Hà Nội": {
    "Quận Hoàn Kiếm": {
      "Phường Chương Dương": {
        "lat": 20.9565,
        "lon": 105.7822
      },
      "Phường Cửa Đông": {
        "lat": 20.9625,
        "lon": 105.7822
      },
      "Phường Cửa Nam": {
        "lat": 20.9685,
        "lon": 105.7822
      },
      "Phường Đồng Xuân": {
        "lat": 20.9745,
        "lon": 105.7822
      },
      "Phường Hàng Bạc": {
        "lat": 20.9805,
        "lon": 105.7822
      },
      "Phường Hàng Bài": {
        "lat": 20.9565,
        "lon": 105.7882
      },
      "Phường Hàng Bồ": {
        "lat": 20.9625,
        "lon": 105.7882
      },
      "Phường Hàng Bông": {
        "lat": 20.9685,
        "lon": 105.7882
      },
      "Phường Hàng Buồm": {
        "lat": 20.9745,
        "lon": 105.7882
      },
      "Phường Hàng Đào": {
        "lat": 20.9805,
        "lon": 105.7882
      },
      "Phường Hàng Gai": {
        "lat": 20.9565,
        "lon": 105.7942
      },
      "Phường Hàng Mã": {
        "lat": 20.9625,
        "lon": 105.7942
      },
      "Phường Lý Thái Tổ": {
        "lat": 20.9685,
        "lon": 105.7942
      },
      "Phường Phan Chu Trinh": {
        "lat": 20.9745,
        "lon": 105.7942
      },
      "Phường Phúc Tân": {
        "lat": 20.9805,
        "lon": 105.7942
      },
      "Phường Trần Hưng Đạo": {
        "lat": 20.9565,
        "lon": 105.8002
      },
      "Phường Tràng Tiền": {
        "lat": 20.9625,
        "lon": 105.8002
      },
      "Phường Hàng Trống": {
        "lat": 20.9685,
        "lon": 105.8002
      }
    },
    "Quận Ba Đình": {
      "Phường Cống Vị": {
        "lat": 20.9965,
        "lon": 105.7822
      },
      "Phường Điện Biên": {
        "lat": 21.0025,
        "lon": 105.7822
      },
      "Phường Đội Cấn": {
        "lat": 21.0085,
        "lon": 105.7822
      },
      "Phường Giảng Võ": {
        "lat": 21.0145,
        "lon": 105.7822
      },
      "Phường Kim Mã": {
        "lat": 21.0205,
        "lon": 105.7822
      },
      "Phường Liễu Giai": {
        "lat": 20.9965,
        "lon": 105.7882
      },
      "Phường Ngọc Hà": {
        "lat": 21.0025,
        "lon": 105.7882
      },
      "Phường Nguyễn Trung Trực": {
        "lat": 21.0085,
        "lon": 105.7882
      },
      "Phường Phúc Xá": {
        "lat": 21.0145,
        "lon": 105.7882
      },
      "Phường Quán Thánh": {
        "lat": 21.0205,
        "lon": 105.7882
      },
      "Phường Thành Công": {
        "lat": 20.9965,
        "lon": 105.7942
      },
      "Phường Trúc Bạch": {
        "lat": 21.0025,
        "lon": 105.7942
      },
      "Phường Vĩnh Phúc": {
        "lat": 21.0085,
        "lon": 105.7942
      }
    },
    "Quận Đống Đa": {
      "Phường Cát Linh": {
        "lat": 21.0365,
        "lon": 105.7822
      },
      "Phường Hàng Bột": {
        "lat": 21.0425,
        "lon": 105.7822
      },
      "Phường Khâm Thiên": {
        "lat": 21.0485,
        "lon": 105.7822
      },
      "Phường Khương Thượng": {
        "lat": 21.0545,
        "lon": 105.7822
      },
      "Phường Kim Liên": {
        "lat": 21.0605,
        "lon": 105.7822
      },
      "Phường Láng Hạ": {
        "lat": 21.0365,
        "lon": 105.7882
      },
      "Phường Láng Thượng": {
        "lat": 21.0425,
        "lon": 105.7882
      },
      "Phường Nam Đồng": {
        "lat": 21.0485,
        "lon": 105.7882
      },
      "Phường Ngã Tư Sở": {
        "lat": 21.0545,
        "lon": 105.7882
      },
      "Phường Ô Chợ Dừa": {
        "lat": 21.0605,
        "lon": 105.7882
      },
      "Phường Phương Liên": {
        "lat": 21.0365,
        "lon": 105.7942
      },
      "Phường Phương Mai": {
        "lat": 21.0425,
        "lon": 105.7942
      },
      "Phường Quang Trung": {
        "lat": 21.0485,
        "lon": 105.7942
      },
      "Phường Quốc Tử Giám": {
        "lat": 21.0545,
        "lon": 105.7942
      },
      "Phường Thịnh Quang": {
        "lat": 21.0605,
        "lon": 105.7942
      },
      "Phường Thổ Quan": {
        "lat": 21.0365,
        "lon": 105.8002
      },
      "Phường Trung Liệt": {
        "lat": 21.0425,
        "lon": 105.8002
      },
      "Phường Trung Phụng": {
        "lat": 21.0485,
        "lon": 105.8002
      },
      "Phường Trung Tự": {
        "lat": 21.0545,
        "lon": 105.8002
      },
      "Phường Văn Chương": {
        "lat": 21.0605,
        "lon": 105.8002
      },
      "Phường Văn Miếu": {
        "lat": 21.0365,
        "lon": 105.8062
      }
    },
    "Quận Cầu Giấy": {
      "Phường Dịch Vọng": {
        "lat": 21.0765,
        "lon": 105.7822
      },
      "Phường Dịch Vọng Hậu": {
        "lat": 21.0825,
        "lon": 105.7822
      },
      "Phường Mai Dịch": {
        "lat": 21.0885,
        "lon": 105.7822
      },
      "Phường Nghĩa Đô": {
        "lat": 21.0945,
        "lon": 105.7822
      },
      "Phường Nghĩa Tân": {
        "lat": 21.1005,
        "lon": 105.7822
      },
      "Phường Quan Hoa": {
        "lat": 21.0765,
        "lon": 105.7882
      },
      "Phường Trung Hòa": {
        "lat": 21.0825,
        "lon": 105.7882
      },
      "Phường Yên Hòa": {
        "lat": 21.0885,
        "lon": 105.7882
      }
    },
    "Quận Hai Bà Trưng": {
      "Phường Bách Khoa": {
        "lat": 20.9565,
        "lon": 105.8222
      },
      "Phường Bạch Đằng": {
        "lat": 20.9625,
        "lon": 105.8222
      },
      "Phường Bạch Mai": {
        "lat": 20.9685,
        "lon": 105.8222
      },
      "Phường Cầu Dền": {
        "lat": 20.9745,
        "lon": 105.8222
      },
      "Phường Đống Mác": {
        "lat": 20.9805,
        "lon": 105.8222
      },
      "Phường Đồng Nhân": {
        "lat": 20.9565,
        "lon": 105.8282
      },
      "Phường Đồng Tâm": {
        "lat": 20.9625,
        "lon": 105.8282
      },
      "Phường Lê Đại Hành": {
        "lat": 20.9685,
        "lon": 105.8282
      },
      "Phường Minh Khai": {
        "lat": 20.9745,
        "lon": 105.8282
      },
      "Phường Nguyễn Du": {
        "lat": 20.9805,
        "lon": 105.8282
      },
      "Phường Phạm Đình Hổ": {
        "lat": 20.9565,
        "lon": 105.8342
      },
      "Phường Phố Huế": {
        "lat": 20.9625,
        "lon": 105.8342
      },
      "Phường Quỳnh Lôi": {
        "lat": 20.9685,
        "lon": 105.8342
      },
      "Phường Quỳnh Mai": {
        "lat": 20.9745,
        "lon": 105.8342
      },
      "Phường Thanh Lương": {
        "lat": 20.9805,
        "lon": 105.8342
      },
      "Phường Thanh Nhàn": {
        "lat": 20.9565,
        "lon": 105.8402
      },
      "Phường Trương Định": {
        "lat": 20.9625,
        "lon": 105.8402
      },
      "Phường Vĩnh Tuy": {
        "lat": 20.9685,
        "lon": 105.8402
      }
    },
    "Quận Tây Hồ": {
      "Phường Bưởi": {
        "lat": 20.9965,
        "lon": 105.8222
      },
      "Phường Nhật Tân": {
        "lat": 21.0025,
        "lon": 105.8222
      },
      "Phường Phú Thượng": {
        "lat": 21.0085,
        "lon": 105.8222
      },
      "Phường Quảng An": {
        "lat": 21.0145,
        "lon": 105.8222
      },
      "Phường Tứ Liên": {
        "lat": 21.0205,
        "lon": 105.8222
      },
      "Phường Xuân La": {
        "lat": 20.9965,
        "lon": 105.8282
      },
      "Phường Yên Phụ": {
        "lat": 21.0025,
        "lon": 105.8282
      },
      "Phường Thụy Khuê": {
        "lat": 21.0085,
        "lon": 105.8282
      }
    },
    "Quận Thanh Xuân": {
      "Phường Hạ Đình": {
        "lat": 21.0365,
        "lon": 105.8222
      },
      "Phường Khương Đình": {
        "lat": 21.0425,
        "lon": 105.8222
      },
      "Phường Khương Mai": {
        "lat": 21.0485,
        "lon": 105.8222
      },
      "Phường Khương Trung": {
        "lat": 21.0545,
        "lon": 105.8222
      },
      "Phường Kim Giang": {
        "lat": 21.0605,
        "lon": 105.8222
      },
      "Phường Nhân Chính": {
        "lat": 21.0365,
        "lon": 105.8282
      },
      "Phường Phương Liệt": {
        "lat": 21.0425,
        "lon": 105.8282
      },
      "Phường Thanh Xuân Bắc": {
        "lat": 21.0485,
        "lon": 105.8282
      },
      "Phường Thanh Xuân Nam": {
        "lat": 21.0545,
        "lon": 105.8282
      },
      "Phường Thanh Xuân Trung": {
        "lat": 21.0605,
        "lon": 105.8282
      },
      "Phường Thượng Đình": {
        "lat": 21.0365,
        "lon": 105.8342
      }
    },
    "Quận Hoàng Mai": {
      "Phường Đại Kim": {
        "lat": 21.0765,
        "lon": 105.8222
      },
      "Phường Định Công": {
        "lat": 21.0825,
        "lon": 105.8222
      },
      "Phường Giáp Bát": {
        "lat": 21.0885,
        "lon": 105.8222
      },
      "Phường Hoàng Liệt": {
        "lat": 21.0945,
        "lon": 105.8222
      },
      "Phường Hoàng Văn Thụ": {
        "lat": 21.1005,
        "lon": 105.8222
      },
      "Phường Lĩnh Nam": {
        "lat": 21.0765,
        "lon": 105.8282
      },
      "Phường Mai Động": {
        "lat": 21.0825,
        "lon": 105.8282
      },
      "Phường Tân Mai": {
        "lat": 21.0885,
        "lon": 105.8282
      },
      "Phường Thanh Trì": {
        "lat": 21.0945,
        "lon": 105.8282
      },
      "Phường Thịnh Liệt": {
        "lat": 21.1005,
        "lon": 105.8282
      },
      "Phường Trần Phú": {
        "lat": 21.0765,
        "lon": 105.8342
      },
      "Phường Tương Mai": {
        "lat": 21.0825,
        "lon": 105.8342
      },
      "Phường Vĩnh Hưng": {
        "lat": 21.0885,
        "lon": 105.8342
      },
      "Phường Yên Sở": {
        "lat": 21.0945,
        "lon": 105.8342
      }
    },
    "Quận Long Biên": {
      "Phường Bồ Đề": {
        "lat": 20.9565,
        "lon": 105.8622
      },
      "Phường Cự Khối": {
        "lat": 20.9625,
        "lon": 105.8622
      },
      "Phường Đức Giang": {
        "lat": 20.9685,
        "lon": 105.8622
      },
      "Phường Gia Thụy": {
        "lat": 20.9745,
        "lon": 105.8622
      },
      "Phường Giang Biên": {
        "lat": 20.9805,
        "lon": 105.8622
      },
      "Phường Long Biên": {
        "lat": 20.9565,
        "lon": 105.8682
      },
      "Phường Ngọc Lâm": {
        "lat": 20.9625,
        "lon": 105.8682
      },
      "Phường Ngọc Thụy": {
        "lat": 20.9685,
        "lon": 105.8682
      },
      "Phường Phúc Đồng": {
        "lat": 20.9745,
        "lon": 105.8682
      },
      "Phường Phúc Lợi": {
        "lat": 20.9805,
        "lon": 105.8682
      },
      "Phường Sài Đồng": {
        "lat": 20.9565,
        "lon": 105.8742
      },
      "Phường Thạch Bàn": {
        "lat": 20.9625,
        "lon": 105.8742
      },
      "Phường Thượng Thanh": {
        "lat": 20.9685,
        "lon": 105.8742
      },
      "Phường Việt Hưng": {
        "lat": 20.9745,
        "lon": 105.8742
      }
    },
    "Quận Hà Đông": {
      "Phường Biên Giang": {
        "lat": 20.9535,
        "lon": 105.7590
      },
      "Phường Đồng Mai": {
        "lat": 20.9480,
        "lon": 105.7720
      },
      "Phường Yên Nghĩa": {
        "lat": 20.9630,
        "lon": 105.7810
      },
      "Phường Dương Nội": {
        "lat": 20.9870,
        "lon": 105.7620
      },
      "Phường Hà Cầu": {
        "lat": 20.9680,
        "lon": 105.7870
      },
      "Phường La Khê": {
        "lat": 20.9710,
        "lon": 105.7750
      },
      "Phường Mộ Lao": {
        "lat": 20.9740,
        "lon": 105.7820
      },
      "Phường Nguyễn Trãi": {
        "lat": 20.9800,
        "lon": 105.7820
      },
      "Phường Phú La": {
        "lat": 20.9750,
        "lon": 105.7920
      },
      "Phường Phú Lãm": {
        "lat": 20.9590,
        "lon": 105.7980
      },
      "Phường Phú Lương": {
        "lat": 20.9640,
        "lon": 105.7940
      },
      "Phường Phúc La": {
        "lat": 20.9700,
        "lon": 105.7890
      },
      "Phường Quang Trung": {
        "lat": 20.9760,
        "lon": 105.7850
      },
      "Phường Vạn Phúc": {
        "lat": 20.9730,
        "lon": 105.7760
      },
      "Phường Văn Quán": {
        "lat": 20.9810,
        "lon": 105.7890
      },
      "Phường Yết Kiêu": {
        "lat": 20.9820,
        "lon": 105.7780
      },
      "Phường Kiến Hưng": {
        "lat": 20.9680,
        "lon": 105.8020
      }
    },
    "Quận Nam Từ Liêm": {
      "Phường Cầu Diễn": {
        "lat": 21.0365,
        "lon": 105.8622
      },
      "Phường Đại Mỗ": {
        "lat": 21.0425,
        "lon": 105.8622
      },
      "Phường Mễ Trì": {
        "lat": 21.0485,
        "lon": 105.8622
      },
      "Phường Mỹ Đình 1": {
        "lat": 21.0545,
        "lon": 105.8622
      },
      "Phường Mỹ Đình 2": {
        "lat": 21.0605,
        "lon": 105.8622
      },
      "Phường Phú Đô": {
        "lat": 21.0365,
        "lon": 105.8682
      },
      "Phường Tây Mỗ": {
        "lat": 21.0425,
        "lon": 105.8682
      },
      "Phường Phương Canh": {
        "lat": 21.0485,
        "lon": 105.8682
      },
      "Phường Trung Văn": {
        "lat": 21.0545,
        "lon": 105.8682
      },
      "Phường Xuân Phương": {
        "lat": 21.0605,
        "lon": 105.8682
      }
    },
    "Quận Bắc Từ Liêm": {
      "Phường Cổ Nhuế 1": {
        "lat": 21.0765,
        "lon": 105.8622
      },
      "Phường Cổ Nhuế 2": {
        "lat": 21.0825,
        "lon": 105.8622
      },
      "Phường Đức Thắng": {
        "lat": 21.0885,
        "lon": 105.8622
      },
      "Phường Đông Ngạc": {
        "lat": 21.0945,
        "lon": 105.8622
      },
      "Phường Thụy Phương": {
        "lat": 21.1005,
        "lon": 105.8622
      },
      "Phường Liên Mạc": {
        "lat": 21.0765,
        "lon": 105.8682
      },
      "Phường Thượng Cát": {
        "lat": 21.0825,
        "lon": 105.8682
      },
      "Phường Tây Tựu": {
        "lat": 21.0885,
        "lon": 105.8682
      },
      "Phường Minh Khai": {
        "lat": 21.0945,
        "lon": 105.8682
      },
      "Phường Phú Diễn": {
        "lat": 21.1005,
        "lon": 105.8682
      },
      "Phường Phúc Diễn": {
        "lat": 21.0765,
        "lon": 105.8742
      },
      "Phường Xuân Đỉnh": {
        "lat": 21.0825,
        "lon": 105.8742
      },
      "Phường Xuân Tảo": {
        "lat": 21.0885,
        "lon": 105.8742
      }
    }
  },
  "TP. Hồ Chí Minh": {
    "Quận 1": {
      "Phường Bến Nghé": {
        "lat": 10.7049,
        "lon": 106.6289
      },
      "Phường Bến Thành": {
        "lat": 10.7109,
        "lon": 106.6289
      },
      "Phường Cô Giang": {
        "lat": 10.7169,
        "lon": 106.6289
      },
      "Phường Cầu Kho": {
        "lat": 10.7229,
        "lon": 106.6289
      },
      "Phường Cầu Ông Lãnh": {
        "lat": 10.7289,
        "lon": 106.6289
      },
      "Phường Đa Kao": {
        "lat": 10.7049,
        "lon": 106.6349
      },
      "Phường Nguyễn Cư Trinh": {
        "lat": 10.7109,
        "lon": 106.6349
      },
      "Phường Nguyễn Thái Bình": {
        "lat": 10.7169,
        "lon": 106.6349
      },
      "Phường Phạm Ngũ Lão": {
        "lat": 10.7229,
        "lon": 106.6349
      },
      "Phường Tân Định": {
        "lat": 10.7289,
        "lon": 106.6349
      }
    },
    "Quận 3": {
      "Phường 1": {
        "lat": 10.7449,
        "lon": 106.6289
      },
      "Phường 2": {
        "lat": 10.7509,
        "lon": 106.6289
      },
      "Phường 3": {
        "lat": 10.7569,
        "lon": 106.6289
      },
      "Phường 4": {
        "lat": 10.7629,
        "lon": 106.6289
      },
      "Phường 5": {
        "lat": 10.7689,
        "lon": 106.6289
      },
      "Phường Võ Thị Sáu": {
        "lat": 10.7449,
        "lon": 106.6349
      },
      "Phường 9": {
        "lat": 10.7509,
        "lon": 106.6349
      },
      "Phường 10": {
        "lat": 10.7569,
        "lon": 106.6349
      },
      "Phường 11": {
        "lat": 10.7629,
        "lon": 106.6349
      },
      "Phường 12": {
        "lat": 10.7689,
        "lon": 106.6349
      },
      "Phường 13": {
        "lat": 10.7449,
        "lon": 106.6409
      },
      "Phường 14": {
        "lat": 10.7509,
        "lon": 106.6409
      }
    },
    "Quận 4": {
      "Phường 1": {
        "lat": 10.7849,
        "lon": 106.6289
      },
      "Phường 2": {
        "lat": 10.7909,
        "lon": 106.6289
      },
      "Phường 3": {
        "lat": 10.7969,
        "lon": 106.6289
      },
      "Phường 4": {
        "lat": 10.8029,
        "lon": 106.6289
      },
      "Phường 6": {
        "lat": 10.8089,
        "lon": 106.6289
      },
      "Phường 8": {
        "lat": 10.7849,
        "lon": 106.6349
      },
      "Phường 9": {
        "lat": 10.7909,
        "lon": 106.6349
      },
      "Phường 10": {
        "lat": 10.7969,
        "lon": 106.6349
      },
      "Phường 13": {
        "lat": 10.8029,
        "lon": 106.6349
      },
      "Phường 14": {
        "lat": 10.8089,
        "lon": 106.6349
      },
      "Phường 15": {
        "lat": 10.7849,
        "lon": 106.6409
      },
      "Phường 16": {
        "lat": 10.7909,
        "lon": 106.6409
      },
      "Phường 18": {
        "lat": 10.7969,
        "lon": 106.6409
      }
    },
    "Quận 5": {
      "Phường 1": {
        "lat": 10.8249,
        "lon": 106.6289
      },
      "Phường 2": {
        "lat": 10.8309,
        "lon": 106.6289
      },
      "Phường 3": {
        "lat": 10.8369,
        "lon": 106.6289
      },
      "Phường 4": {
        "lat": 10.8429,
        "lon": 106.6289
      },
      "Phường 5": {
        "lat": 10.8489,
        "lon": 106.6289
      },
      "Phường 6": {
        "lat": 10.8249,
        "lon": 106.6349
      },
      "Phường 7": {
        "lat": 10.8309,
        "lon": 106.6349
      },
      "Phường 8": {
        "lat": 10.8369,
        "lon": 106.6349
      },
      "Phường 9": {
        "lat": 10.8429,
        "lon": 106.6349
      },
      "Phường 10": {
        "lat": 10.8489,
        "lon": 106.6349
      },
      "Phường 11": {
        "lat": 10.8249,
        "lon": 106.6409
      },
      "Phường 12": {
        "lat": 10.8309,
        "lon": 106.6409
      },
      "Phường 13": {
        "lat": 10.8369,
        "lon": 106.6409
      },
      "Phường 14": {
        "lat": 10.8429,
        "lon": 106.6409
      }
    },
    "Quận 6": {
      "Phường 1": {
        "lat": 10.7049,
        "lon": 106.6689
      },
      "Phường 2": {
        "lat": 10.7109,
        "lon": 106.6689
      },
      "Phường 3": {
        "lat": 10.7169,
        "lon": 106.6689
      },
      "Phường 4": {
        "lat": 10.7229,
        "lon": 106.6689
      },
      "Phường 5": {
        "lat": 10.7289,
        "lon": 106.6689
      },
      "Phường 6": {
        "lat": 10.7049,
        "lon": 106.6749
      },
      "Phường 7": {
        "lat": 10.7109,
        "lon": 106.6749
      },
      "Phường 8": {
        "lat": 10.7169,
        "lon": 106.6749
      },
      "Phường 9": {
        "lat": 10.7229,
        "lon": 106.6749
      },
      "Phường 10": {
        "lat": 10.7289,
        "lon": 106.6749
      },
      "Phường 11": {
        "lat": 10.7049,
        "lon": 106.6809
      },
      "Phường 12": {
        "lat": 10.7109,
        "lon": 106.6809
      },
      "Phường 13": {
        "lat": 10.7169,
        "lon": 106.6809
      },
      "Phường 14": {
        "lat": 10.7229,
        "lon": 106.6809
      }
    },
    "Quận 7": {
      "Phường Bình Thuận": {
        "lat": 10.7449,
        "lon": 106.6689
      },
      "Phường Phú Mỹ": {
        "lat": 10.7509,
        "lon": 106.6689
      },
      "Phường Phú Thuận": {
        "lat": 10.7569,
        "lon": 106.6689
      },
      "Phường Tân Hưng": {
        "lat": 10.7629,
        "lon": 106.6689
      },
      "Phường Tân Kiểng": {
        "lat": 10.7689,
        "lon": 106.6689
      },
      "Phường Tân Phong": {
        "lat": 10.7449,
        "lon": 106.6749
      },
      "Phường Tân Phú": {
        "lat": 10.7509,
        "lon": 106.6749
      },
      "Phường Tân Quy": {
        "lat": 10.7569,
        "lon": 106.6749
      },
      "Phường Tân Thuận Đông": {
        "lat": 10.7629,
        "lon": 106.6749
      },
      "Phường Tân Thuận Tây": {
        "lat": 10.7689,
        "lon": 106.6749
      }
    },
    "Quận 8": {
      "Phường 1": {
        "lat": 10.7849,
        "lon": 106.6689
      },
      "Phường 2": {
        "lat": 10.7909,
        "lon": 106.6689
      },
      "Phường 3": {
        "lat": 10.7969,
        "lon": 106.6689
      },
      "Phường 4": {
        "lat": 10.8029,
        "lon": 106.6689
      },
      "Phường 5": {
        "lat": 10.8089,
        "lon": 106.6689
      },
      "Phường 6": {
        "lat": 10.7849,
        "lon": 106.6749
      },
      "Phường 7": {
        "lat": 10.7909,
        "lon": 106.6749
      },
      "Phường 8": {
        "lat": 10.7969,
        "lon": 106.6749
      },
      "Phường 9": {
        "lat": 10.8029,
        "lon": 106.6749
      },
      "Phường 10": {
        "lat": 10.8089,
        "lon": 106.6749
      },
      "Phường 11": {
        "lat": 10.7849,
        "lon": 106.6809
      },
      "Phường 12": {
        "lat": 10.7909,
        "lon": 106.6809
      },
      "Phường 13": {
        "lat": 10.7969,
        "lon": 106.6809
      },
      "Phường 14": {
        "lat": 10.8029,
        "lon": 106.6809
      },
      "Phường 15": {
        "lat": 10.8089,
        "lon": 106.6809
      },
      "Phường 16": {
        "lat": 10.7849,
        "lon": 106.6869
      }
    },
    "Quận 10": {
      "Phường 1": {
        "lat": 10.8249,
        "lon": 106.6689
      },
      "Phường 2": {
        "lat": 10.8309,
        "lon": 106.6689
      },
      "Phường 4": {
        "lat": 10.8369,
        "lon": 106.6689
      },
      "Phường 5": {
        "lat": 10.8429,
        "lon": 106.6689
      },
      "Phường 6": {
        "lat": 10.8489,
        "lon": 106.6689
      },
      "Phường 7": {
        "lat": 10.8249,
        "lon": 106.6749
      },
      "Phường 8": {
        "lat": 10.8309,
        "lon": 106.6749
      },
      "Phường 9": {
        "lat": 10.8369,
        "lon": 106.6749
      },
      "Phường 10": {
        "lat": 10.8429,
        "lon": 106.6749
      },
      "Phường 11": {
        "lat": 10.8489,
        "lon": 106.6749
      },
      "Phường 12": {
        "lat": 10.8249,
        "lon": 106.6809
      },
      "Phường 13": {
        "lat": 10.8309,
        "lon": 106.6809
      },
      "Phường 14": {
        "lat": 10.8369,
        "lon": 106.6809
      },
      "Phường 15": {
        "lat": 10.8429,
        "lon": 106.6809
      }
    },
    "Quận 11": {
      "Phường 1": {
        "lat": 10.7049,
        "lon": 106.7089
      },
      "Phường 2": {
        "lat": 10.7109,
        "lon": 106.7089
      },
      "Phường 3": {
        "lat": 10.7169,
        "lon": 106.7089
      },
      "Phường 4": {
        "lat": 10.7229,
        "lon": 106.7089
      },
      "Phường 5": {
        "lat": 10.7289,
        "lon": 106.7089
      },
      "Phường 6": {
        "lat": 10.7049,
        "lon": 106.7149
      },
      "Phường 7": {
        "lat": 10.7109,
        "lon": 106.7149
      },
      "Phường 8": {
        "lat": 10.7169,
        "lon": 106.7149
      },
      "Phường 9": {
        "lat": 10.7229,
        "lon": 106.7149
      },
      "Phường 10": {
        "lat": 10.7289,
        "lon": 106.7149
      },
      "Phường 11": {
        "lat": 10.7049,
        "lon": 106.7209
      },
      "Phường 12": {
        "lat": 10.7109,
        "lon": 106.7209
      },
      "Phường 13": {
        "lat": 10.7169,
        "lon": 106.7209
      },
      "Phường 14": {
        "lat": 10.7229,
        "lon": 106.7209
      },
      "Phường 15": {
        "lat": 10.7289,
        "lon": 106.7209
      },
      "Phường 16": {
        "lat": 10.7049,
        "lon": 106.7269
      }
    },
    "Quận 12": {
      "Phường An Phú Đông": {
        "lat": 10.7449,
        "lon": 106.7089
      },
      "Phường Đông Hưng Thuận": {
        "lat": 10.7509,
        "lon": 106.7089
      },
      "Phường Hiệp Thành": {
        "lat": 10.7569,
        "lon": 106.7089
      },
      "Phường Tân Chánh Hiệp": {
        "lat": 10.7629,
        "lon": 106.7089
      },
      "Phường Tân Hưng Thuận": {
        "lat": 10.7689,
        "lon": 106.7089
      },
      "Phường Tân Thới Hiệp": {
        "lat": 10.7449,
        "lon": 106.7149
      },
      "Phường Tân Thới Nhất": {
        "lat": 10.7509,
        "lon": 106.7149
      },
      "Phường Thạnh Lộc": {
        "lat": 10.7569,
        "lon": 106.7149
      },
      "Phường Thạnh Xuân": {
        "lat": 10.7629,
        "lon": 106.7149
      },
      "Phường Thới An": {
        "lat": 10.7689,
        "lon": 106.7149
      },
      "Phường Trung Mỹ Tây": {
        "lat": 10.7449,
        "lon": 106.7209
      }
    },
    "Quận Bình Thạnh": {
      "Phường 1": {
        "lat": 10.7849,
        "lon": 106.7089
      },
      "Phường 2": {
        "lat": 10.7909,
        "lon": 106.7089
      },
      "Phường 3": {
        "lat": 10.7969,
        "lon": 106.7089
      },
      "Phường 5": {
        "lat": 10.8029,
        "lon": 106.7089
      },
      "Phường 6": {
        "lat": 10.8089,
        "lon": 106.7089
      },
      "Phường 7": {
        "lat": 10.7849,
        "lon": 106.7149
      },
      "Phường 11": {
        "lat": 10.7909,
        "lon": 106.7149
      },
      "Phường 12": {
        "lat": 10.7969,
        "lon": 106.7149
      },
      "Phường 13": {
        "lat": 10.8029,
        "lon": 106.7149
      },
      "Phường 14": {
        "lat": 10.8089,
        "lon": 106.7149
      },
      "Phường 15": {
        "lat": 10.7849,
        "lon": 106.7209
      },
      "Phường 17": {
        "lat": 10.7909,
        "lon": 106.7209
      },
      "Phường 19": {
        "lat": 10.7969,
        "lon": 106.7209
      },
      "Phường 21": {
        "lat": 10.8029,
        "lon": 106.7209
      },
      "Phường 22": {
        "lat": 10.8089,
        "lon": 106.7209
      },
      "Phường 24": {
        "lat": 10.7849,
        "lon": 106.7269
      },
      "Phường 25": {
        "lat": 10.7909,
        "lon": 106.7269
      },
      "Phường 26": {
        "lat": 10.7969,
        "lon": 106.7269
      },
      "Phường 27": {
        "lat": 10.8029,
        "lon": 106.7269
      },
      "Phường 28": {
        "lat": 10.8089,
        "lon": 106.7269
      }
    },
    "Quận Gò Vấp": {
      "Phường 1": {
        "lat": 10.8249,
        "lon": 106.7089
      },
      "Phường 3": {
        "lat": 10.8309,
        "lon": 106.7089
      },
      "Phường 4": {
        "lat": 10.8369,
        "lon": 106.7089
      },
      "Phường 5": {
        "lat": 10.8429,
        "lon": 106.7089
      },
      "Phường 6": {
        "lat": 10.8489,
        "lon": 106.7089
      },
      "Phường 7": {
        "lat": 10.8249,
        "lon": 106.7149
      },
      "Phường 8": {
        "lat": 10.8309,
        "lon": 106.7149
      },
      "Phường 9": {
        "lat": 10.8369,
        "lon": 106.7149
      },
      "Phường 10": {
        "lat": 10.8429,
        "lon": 106.7149
      },
      "Phường 11": {
        "lat": 10.8489,
        "lon": 106.7149
      },
      "Phường 12": {
        "lat": 10.8249,
        "lon": 106.7209
      },
      "Phường 13": {
        "lat": 10.8309,
        "lon": 106.7209
      },
      "Phường 14": {
        "lat": 10.8369,
        "lon": 106.7209
      },
      "Phường 15": {
        "lat": 10.8429,
        "lon": 106.7209
      },
      "Phường 16": {
        "lat": 10.8489,
        "lon": 106.7209
      },
      "Phường 17": {
        "lat": 10.8249,
        "lon": 106.7269
      }
    },
    "Quận Phú Nhuận": {
      "Phường 1": {
        "lat": 10.7049,
        "lon": 106.7489
      },
      "Phường 2": {
        "lat": 10.7109,
        "lon": 106.7489
      },
      "Phường 3": {
        "lat": 10.7169,
        "lon": 106.7489
      },
      "Phường 4": {
        "lat": 10.7229,
        "lon": 106.7489
      },
      "Phường 5": {
        "lat": 10.7289,
        "lon": 106.7489
      },
      "Phường 7": {
        "lat": 10.7049,
        "lon": 106.7549
      },
      "Phường 8": {
        "lat": 10.7109,
        "lon": 106.7549
      },
      "Phường 9": {
        "lat": 10.7169,
        "lon": 106.7549
      },
      "Phường 10": {
        "lat": 10.7229,
        "lon": 106.7549
      },
      "Phường 11": {
        "lat": 10.7289,
        "lon": 106.7549
      },
      "Phường 13": {
        "lat": 10.7049,
        "lon": 106.7609
      },
      "Phường 15": {
        "lat": 10.7109,
        "lon": 106.7609
      },
      "Phường 17": {
        "lat": 10.7169,
        "lon": 106.7609
      }
    },
    "Quận Tân Bình": {
      "Phường 1": {
        "lat": 10.7449,
        "lon": 106.7489
      },
      "Phường 2": {
        "lat": 10.7509,
        "lon": 106.7489
      },
      "Phường 3": {
        "lat": 10.7569,
        "lon": 106.7489
      },
      "Phường 4": {
        "lat": 10.7629,
        "lon": 106.7489
      },
      "Phường 5": {
        "lat": 10.7689,
        "lon": 106.7489
      },
      "Phường 6": {
        "lat": 10.7449,
        "lon": 106.7549
      },
      "Phường 7": {
        "lat": 10.7509,
        "lon": 106.7549
      },
      "Phường 8": {
        "lat": 10.7569,
        "lon": 106.7549
      },
      "Phường 9": {
        "lat": 10.7629,
        "lon": 106.7549
      },
      "Phường 10": {
        "lat": 10.7689,
        "lon": 106.7549
      },
      "Phường 11": {
        "lat": 10.7449,
        "lon": 106.7609
      },
      "Phường 12": {
        "lat": 10.7509,
        "lon": 106.7609
      },
      "Phường 13": {
        "lat": 10.7569,
        "lon": 106.7609
      },
      "Phường 14": {
        "lat": 10.7629,
        "lon": 106.7609
      },
      "Phường 15": {
        "lat": 10.7689,
        "lon": 106.7609
      }
    },
    "Quận Tân Phú": {
      "Phường Hiệp Tân": {
        "lat": 10.7849,
        "lon": 106.7489
      },
      "Phường Hòa Thạnh": {
        "lat": 10.7909,
        "lon": 106.7489
      },
      "Phường Phú Thạnh": {
        "lat": 10.7969,
        "lon": 106.7489
      },
      "Phường Phú Thọ Hòa": {
        "lat": 10.8029,
        "lon": 106.7489
      },
      "Phường Phú Trung": {
        "lat": 10.8089,
        "lon": 106.7489
      },
      "Phường Sơn Kỳ": {
        "lat": 10.7849,
        "lon": 106.7549
      },
      "Phường Tân Quý": {
        "lat": 10.7909,
        "lon": 106.7549
      },
      "Phường Tân Sơn Nhì": {
        "lat": 10.7969,
        "lon": 106.7549
      },
      "Phường Tân Thành": {
        "lat": 10.8029,
        "lon": 106.7549
      },
      "Phường Tân Thới Hòa": {
        "lat": 10.8089,
        "lon": 106.7549
      },
      "Phường Tây Thạnh": {
        "lat": 10.7849,
        "lon": 106.7609
      }
    },
    "Quận Bình Tân": {
      "Phường An Lạc": {
        "lat": 10.8249,
        "lon": 106.7489
      },
      "Phường An Lạc A": {
        "lat": 10.8309,
        "lon": 106.7489
      },
      "Phường Bình Hưng Hòa": {
        "lat": 10.8369,
        "lon": 106.7489
      },
      "Phường Bình Hưng Hòa A": {
        "lat": 10.8429,
        "lon": 106.7489
      },
      "Phường Bình Hưng Hòa B": {
        "lat": 10.8489,
        "lon": 106.7489
      },
      "Phường Bình Trị Đông": {
        "lat": 10.8249,
        "lon": 106.7549
      },
      "Phường Bình Trị Đông A": {
        "lat": 10.8309,
        "lon": 106.7549
      },
      "Phường Bình Trị Đông B": {
        "lat": 10.8369,
        "lon": 106.7549
      },
      "Phường Tân Tạo": {
        "lat": 10.8429,
        "lon": 106.7549
      },
      "Phường Tân Tạo A": {
        "lat": 10.8489,
        "lon": 106.7549
      }
    },
    "TP. Thủ Đức": {
      "Phường An Khánh": {
        "lat": 10.7049,
        "lon": 106.7889
      },
      "Phường An Lợi Đông": {
        "lat": 10.7109,
        "lon": 106.7889
      },
      "Phường An Phú": {
        "lat": 10.7169,
        "lon": 106.7889
      },
      "Phường Bình Chiểu": {
        "lat": 10.7229,
        "lon": 106.7889
      },
      "Phường Bình Thọ": {
        "lat": 10.7289,
        "lon": 106.7889
      },
      "Phường Cát Lái": {
        "lat": 10.7049,
        "lon": 106.7949
      },
      "Phường Hiệp Bình Chánh": {
        "lat": 10.7109,
        "lon": 106.7949
      },
      "Phường Hiệp Bình Phước": {
        "lat": 10.7169,
        "lon": 106.7949
      },
      "Phường Hiệp Phú": {
        "lat": 10.7229,
        "lon": 106.7949
      },
      "Phường Linh Chiểu": {
        "lat": 10.7289,
        "lon": 106.7949
      },
      "Phường Linh Đông": {
        "lat": 10.7049,
        "lon": 106.8009
      },
      "Phường Linh Tây": {
        "lat": 10.7109,
        "lon": 106.8009
      },
      "Phường Linh Trung": {
        "lat": 10.7169,
        "lon": 106.8009
      },
      "Phường Linh Xuân": {
        "lat": 10.7229,
        "lon": 106.8009
      },
      "Phường Long Bình": {
        "lat": 10.7289,
        "lon": 106.8009
      },
      "Phường Long Phước": {
        "lat": 10.7049,
        "lon": 106.8069
      },
      "Phường Long Thạnh Mỹ": {
        "lat": 10.7109,
        "lon": 106.8069
      },
      "Phường Long Trường": {
        "lat": 10.7169,
        "lon": 106.8069
      },
      "Phường Phú Hữu": {
        "lat": 10.7229,
        "lon": 106.8069
      },
      "Phường Phước Bình": {
        "lat": 10.7289,
        "lon": 106.8069
      },
      "Phường Phước Long A": {
        "lat": 10.7049,
        "lon": 106.8129
      },
      "Phường Phước Long B": {
        "lat": 10.7109,
        "lon": 106.8129
      },
      "Phường Tam Bình": {
        "lat": 10.7169,
        "lon": 106.8129
      },
      "Phường Tam Phú": {
        "lat": 10.7229,
        "lon": 106.8129
      },
      "Phường Thạnh Mỹ Lợi": {
        "lat": 10.7289,
        "lon": 106.8129
      },
      "Phường Thảo Điền": {
        "lat": 10.7049,
        "lon": 106.8189
      },
      "Phường Thủ Thiêm": {
        "lat": 10.7109,
        "lon": 106.8189
      },
      "Phường Trường Thọ": {
        "lat": 10.7169,
        "lon": 106.8189
      },
      "Phường Trường Thạnh": {
        "lat": 10.7229,
        "lon": 106.8189
      }
    }
  },
  "Đà Nẵng": {
    "Quận Hải Châu": {
      "Phường Bình Hiên": {
        "lat": 15.9824,
        "lon": 108.1302
      },
      "Phường Bình Thuận": {
        "lat": 15.9884,
        "lon": 108.1302
      },
      "Phường Hải Châu 1": {
        "lat": 15.9944,
        "lon": 108.1302
      },
      "Phường Hải Châu 2": {
        "lat": 16.0004,
        "lon": 108.1302
      },
      "Phường Hòa Cường Bắc": {
        "lat": 16.0064,
        "lon": 108.1302
      },
      "Phường Hòa Cường Nam": {
        "lat": 15.9824,
        "lon": 108.1362
      },
      "Phường Hòa Thuận Đông": {
        "lat": 15.9884,
        "lon": 108.1362
      },
      "Phường Hòa Thuận Tây": {
        "lat": 15.9944,
        "lon": 108.1362
      },
      "Phường Nam Dương": {
        "lat": 16.0004,
        "lon": 108.1362
      },
      "Phường Phước Ninh": {
        "lat": 16.0064,
        "lon": 108.1362
      },
      "Phường Thạch Thang": {
        "lat": 15.9824,
        "lon": 108.1422
      },
      "Phường Thanh Bình": {
        "lat": 15.9884,
        "lon": 108.1422
      },
      "Phường Thuận Phước": {
        "lat": 15.9944,
        "lon": 108.1422
      }
    },
    "Quận Thanh Khê": {
      "Phường An Khê": {
        "lat": 16.0224,
        "lon": 108.1302
      },
      "Phường Chính Gián": {
        "lat": 16.0284,
        "lon": 108.1302
      },
      "Phường Hòa Khê": {
        "lat": 16.0344,
        "lon": 108.1302
      },
      "Phường Tam Thuận": {
        "lat": 16.0404,
        "lon": 108.1302
      },
      "Phường Tân Chính": {
        "lat": 16.0464,
        "lon": 108.1302
      },
      "Phường Thạc Gián": {
        "lat": 16.0224,
        "lon": 108.1362
      },
      "Phường Thanh Khê Đông": {
        "lat": 16.0284,
        "lon": 108.1362
      },
      "Phường Thanh Khê Tây": {
        "lat": 16.0344,
        "lon": 108.1362
      },
      "Phường Vĩnh Trung": {
        "lat": 16.0404,
        "lon": 108.1362
      },
      "Phường Xuân Hà": {
        "lat": 16.0464,
        "lon": 108.1362
      }
    },
    "Quận Sơn Trà": {
      "Phường An Hải Bắc": {
        "lat": 16.0624,
        "lon": 108.1302
      },
      "Phường An Hải Đông": {
        "lat": 16.0684,
        "lon": 108.1302
      },
      "Phường An Hải Tây": {
        "lat": 16.0744,
        "lon": 108.1302
      },
      "Phường Mân Thái": {
        "lat": 16.0804,
        "lon": 108.1302
      },
      "Phường Nại Hiên Đông": {
        "lat": 16.0864,
        "lon": 108.1302
      },
      "Phường Phước Mỹ": {
        "lat": 16.0624,
        "lon": 108.1362
      },
      "Phường Thọ Quang": {
        "lat": 16.0684,
        "lon": 108.1362
      }
    },
    "Quận Ngũ Hành Sơn": {
      "Phường Hòa Hải": {
        "lat": 16.1024,
        "lon": 108.1302
      },
      "Phường Hòa Quý": {
        "lat": 16.1084,
        "lon": 108.1302
      },
      "Phường Khuê Mỹ": {
        "lat": 16.1144,
        "lon": 108.1302
      },
      "Phường Mỹ An": {
        "lat": 16.1204,
        "lon": 108.1302
      }
    },
    "Quận Liên Chiểu": {
      "Phường Hòa Hiệp Bắc": {
        "lat": 15.9824,
        "lon": 108.1702
      },
      "Phường Hòa Hiệp Nam": {
        "lat": 15.9884,
        "lon": 108.1702
      },
      "Phường Hòa Khánh Bắc": {
        "lat": 15.9944,
        "lon": 108.1702
      },
      "Phường Hòa Khánh Nam": {
        "lat": 16.0004,
        "lon": 108.1702
      },
      "Phường Hòa Minh": {
        "lat": 16.0064,
        "lon": 108.1702
      }
    },
    "Quận Cẩm Lệ": {
      "Phường Hòa An": {
        "lat": 16.0224,
        "lon": 108.1702
      },
      "Phường Hòa Phát": {
        "lat": 16.0284,
        "lon": 108.1702
      },
      "Phường Hòa Thọ Đông": {
        "lat": 16.0344,
        "lon": 108.1702
      },
      "Phường Hòa Thọ Tây": {
        "lat": 16.0404,
        "lon": 108.1702
      },
      "Phường Hòa Xuân": {
        "lat": 16.0464,
        "lon": 108.1702
      },
      "Phường Khuê Trung": {
        "lat": 16.0224,
        "lon": 108.1762
      }
    }
  },
  "Hải Phòng": {
    "Quận Hồng Bàng": {
      "Phường Hoàng Văn Thụ": {
        "lat": 20.7729,
        "lon": 106.6161
      },
      "Phường Minh Khai": {
        "lat": 20.7789,
        "lon": 106.6161
      },
      "Phường Phan Bội Châu": {
        "lat": 20.7849,
        "lon": 106.6161
      },
      "Phường Phạm Hồng Thái": {
        "lat": 20.7909,
        "lon": 106.6161
      },
      "Phường Quán Toan": {
        "lat": 20.7969,
        "lon": 106.6161
      },
      "Phường Sở Dầu": {
        "lat": 20.7729,
        "lon": 106.6221
      },
      "Phường Thượng Lý": {
        "lat": 20.7789,
        "lon": 106.6221
      },
      "Phường Trại Chuối": {
        "lat": 20.7849,
        "lon": 106.6221
      },
      "Phường Hùng Vương": {
        "lat": 20.7909,
        "lon": 106.6221
      }
    },
    "Quận Ngô Quyền": {
      "Phường Cầu Đất": {
        "lat": 20.8129,
        "lon": 106.6161
      },
      "Phường Đông Hải 1": {
        "lat": 20.8189,
        "lon": 106.6161
      },
      "Phường Đông Hải 2": {
        "lat": 20.8249,
        "lon": 106.6161
      },
      "Phường Đông Khê": {
        "lat": 20.8309,
        "lon": 106.6161
      },
      "Phường Lạc Viên": {
        "lat": 20.8369,
        "lon": 106.6161
      },
      "Phường Lê Lợi": {
        "lat": 20.8129,
        "lon": 106.6221
      },
      "Phường Máy Chai": {
        "lat": 20.8189,
        "lon": 106.6221
      },
      "Phường Máy Tơ": {
        "lat": 20.8249,
        "lon": 106.6221
      },
      "Phường Vạn Mỹ": {
        "lat": 20.8309,
        "lon": 106.6221
      },
      "Phường Gia Viên": {
        "lat": 20.8369,
        "lon": 106.6221
      },
      "Phường Đằng Giang": {
        "lat": 20.8129,
        "lon": 106.6281
      },
      "Phường Lạch Tray": {
        "lat": 20.8189,
        "lon": 106.6281
      }
    },
    "Quận Lê Chân": {
      "Phường An Biên": {
        "lat": 20.8529,
        "lon": 106.6161
      },
      "Phường An Dương": {
        "lat": 20.8589,
        "lon": 106.6161
      },
      "Phường Cát Dài": {
        "lat": 20.8649,
        "lon": 106.6161
      },
      "Phường Đông Hải": {
        "lat": 20.8709,
        "lon": 106.6161
      },
      "Phường Hàng Kênh": {
        "lat": 20.8769,
        "lon": 106.6161
      },
      "Phường Nghĩa Xá": {
        "lat": 20.8529,
        "lon": 106.6221
      },
      "Phường Niệm Nghĩa": {
        "lat": 20.8589,
        "lon": 106.6221
      },
      "Phường Trần Nguyên Hãn": {
        "lat": 20.8649,
        "lon": 106.6221
      },
      "Phường Hồ Nam": {
        "lat": 20.8709,
        "lon": 106.6221
      },
      "Phường Trại Cau": {
        "lat": 20.8769,
        "lon": 106.6221
      },
      "Phường Dư Hàng": {
        "lat": 20.8529,
        "lon": 106.6281
      },
      "Phường Dư Hàng Kênh": {
        "lat": 20.8589,
        "lon": 106.6281
      },
      "Phường Kênh Dương": {
        "lat": 20.8649,
        "lon": 106.6281
      },
      "Phường Vĩnh Niệm": {
        "lat": 20.8709,
        "lon": 106.6281
      }
    },
    "Quận Hải An": {
      "Phường Cát Bi": {
        "lat": 20.8929,
        "lon": 106.6161
      },
      "Phường Đằng Hải": {
        "lat": 20.8989,
        "lon": 106.6161
      },
      "Phường Đằng Lâm": {
        "lat": 20.9049,
        "lon": 106.6161
      },
      "Phường Đông Hải 1": {
        "lat": 20.9109,
        "lon": 106.6161
      },
      "Phường Đông Hải 2": {
        "lat": 20.9169,
        "lon": 106.6161
      },
      "Phường Nam Hải": {
        "lat": 20.8929,
        "lon": 106.6221
      },
      "Phường Thành Tô": {
        "lat": 20.8989,
        "lon": 106.6221
      },
      "Phường Tràng Cát": {
        "lat": 20.9049,
        "lon": 106.6221
      }
    },
    "Quận Kiến An": {
      "Phường Bắc Sơn": {
        "lat": 20.7729,
        "lon": 106.6561
      },
      "Phường Đồng Hòa": {
        "lat": 20.7789,
        "lon": 106.6561
      },
      "Phường Lãm Hà": {
        "lat": 20.7849,
        "lon": 106.6561
      },
      "Phường Nam Sơn": {
        "lat": 20.7909,
        "lon": 106.6561
      },
      "Phường Ngọc Sơn": {
        "lat": 20.7969,
        "lon": 106.6561
      },
      "Phường Phù Liễn": {
        "lat": 20.7729,
        "lon": 106.6621
      },
      "Phường Quán Trữ": {
        "lat": 20.7789,
        "lon": 106.6621
      },
      "Phường Trần Thành Ngọ": {
        "lat": 20.7849,
        "lon": 106.6621
      },
      "Phường Tràng Minh": {
        "lat": 20.7909,
        "lon": 106.6621
      },
      "Phường Văn Đẩu": {
        "lat": 20.7969,
        "lon": 106.6621
      }
    },
    "Quận Đồ Sơn": {
      "Phường Bàng La": {
        "lat": 20.8129,
        "lon": 106.6561
      },
      "Phường Hải Sơn": {
        "lat": 20.8189,
        "lon": 106.6561
      },
      "Phường Hợp Đức": {
        "lat": 20.8249,
        "lon": 106.6561
      },
      "Phường Minh Đức": {
        "lat": 20.8309,
        "lon": 106.6561
      },
      "Phường Ngọc Xuyên": {
        "lat": 20.8369,
        "lon": 106.6561
      },
      "Phường Vạn Hương": {
        "lat": 20.8129,
        "lon": 106.6621
      }
    },
    "Quận Dương Kinh": {
      "Phường Anh Dũng": {
        "lat": 20.8529,
        "lon": 106.6561
      },
      "Phường Đa Phúc": {
        "lat": 20.8589,
        "lon": 106.6561
      },
      "Phường Hưng Đạo": {
        "lat": 20.8649,
        "lon": 106.6561
      },
      "Phường Hải Thành": {
        "lat": 20.8709,
        "lon": 106.6561
      },
      "Phường Hòa Nghĩa": {
        "lat": 20.8769,
        "lon": 106.6561
      },
      "Phường Tân Thành": {
        "lat": 20.8529,
        "lon": 106.6621
      }
    }
  },
  "Cần Thơ": {
    "Quận Ninh Kiều": {
      "Phường An Bình": {
        "lat": 9.9651,
        "lon": 105.7162
      },
      "Phường An Cư": {
        "lat": 9.9711,
        "lon": 105.7162
      },
      "Phường An Hòa": {
        "lat": 9.9771,
        "lon": 105.7162
      },
      "Phường An Khánh": {
        "lat": 9.9831,
        "lon": 105.7162
      },
      "Phường An Nghiệp": {
        "lat": 9.9891,
        "lon": 105.7162
      },
      "Phường An Phú": {
        "lat": 9.9651,
        "lon": 105.7222
      },
      "Phường Cái Khế": {
        "lat": 9.9711,
        "lon": 105.7222
      },
      "Phường Hưng Lợi": {
        "lat": 9.9771,
        "lon": 105.7222
      },
      "Phường Tân An": {
        "lat": 9.9831,
        "lon": 105.7222
      },
      "Phường Thới Bình": {
        "lat": 9.9891,
        "lon": 105.7222
      },
      "Phường Xuân Khánh": {
        "lat": 9.9651,
        "lon": 105.7282
      }
    },
    "Quận Bình Thủy": {
      "Phường An Thới": {
        "lat": 10.0051,
        "lon": 105.7162
      },
      "Phường Bình Thủy": {
        "lat": 10.0111,
        "lon": 105.7162
      },
      "Phường Bùi Hữu Nghĩa": {
        "lat": 10.0171,
        "lon": 105.7162
      },
      "Phường Long Hòa": {
        "lat": 10.0231,
        "lon": 105.7162
      },
      "Phường Long Tuyền": {
        "lat": 10.0291,
        "lon": 105.7162
      },
      "Phường Thới An Đông": {
        "lat": 10.0051,
        "lon": 105.7222
      },
      "Phường Trà An": {
        "lat": 10.0111,
        "lon": 105.7222
      },
      "Phường Trà Nóc": {
        "lat": 10.0171,
        "lon": 105.7222
      }
    },
    "Quận Cái Răng": {
      "Phường Ba Láng": {
        "lat": 10.0451,
        "lon": 105.7162
      },
      "Phường Hưng Phú": {
        "lat": 10.0511,
        "lon": 105.7162
      },
      "Phường Hưng Thạnh": {
        "lat": 10.0571,
        "lon": 105.7162
      },
      "Phường Lê Bình": {
        "lat": 10.0631,
        "lon": 105.7162
      },
      "Phường Phú Thứ": {
        "lat": 10.0691,
        "lon": 105.7162
      },
      "Phường Tân Phú": {
        "lat": 10.0451,
        "lon": 105.7222
      },
      "Phường Thường Thạnh": {
        "lat": 10.0511,
        "lon": 105.7222
      }
    },
    "Quận Ô Môn": {
      "Phường Châu Văn Liêm": {
        "lat": 10.0851,
        "lon": 105.7162
      },
      "Phường Phước Thới": {
        "lat": 10.0911,
        "lon": 105.7162
      },
      "Phường Thới An": {
        "lat": 10.0971,
        "lon": 105.7162
      },
      "Phường Thới Hòa": {
        "lat": 10.1031,
        "lon": 105.7162
      },
      "Phường Thới Long": {
        "lat": 10.1091,
        "lon": 105.7162
      },
      "Phường Trường Lạc": {
        "lat": 10.0851,
        "lon": 105.7222
      },
      "Phường Định Môn": {
        "lat": 10.0911,
        "lon": 105.7222
      }
    },
    "Quận Thốt Nốt": {
      "Phường Tân Lộc": {
        "lat": 9.9651,
        "lon": 105.7562
      },
      "Phường Tân Hưng": {
        "lat": 9.9711,
        "lon": 105.7562
      },
      "Phường Thốt Nốt": {
        "lat": 9.9771,
        "lon": 105.7562
      },
      "Phường Thạnh Hòa": {
        "lat": 9.9831,
        "lon": 105.7562
      },
      "Phường Thới Thuận": {
        "lat": 9.9891,
        "lon": 105.7562
      },
      "Phường Thuận An": {
        "lat": 9.9651,
        "lon": 105.7622
      },
      "Phường Thuận Hưng": {
        "lat": 9.9711,
        "lon": 105.7622
      },
      "Phường Trung Nhứt": {
        "lat": 9.9771,
        "lon": 105.7622
      },
      "Phường Trung Kiên": {
        "lat": 9.9831,
        "lon": 105.7622
      }
    }
  }
};

/**
 * Lấy danh sách tỉnh/thành phố
 */
function getProvinces() {
  return Object.keys(VIETNAM_LOCATIONS).sort();
}

/**
 * Lấy danh sách quận/huyện theo tỉnh/thành phố
 */
function getDistricts(province) {
  if (!VIETNAM_LOCATIONS[province]) return [];
  return Object.keys(VIETNAM_LOCATIONS[province]).sort();
}

/**
 * Lấy danh sách phường/xã theo tỉnh/thành phố và quận/huyện
 */
function getWards(province, district) {
  if (!VIETNAM_LOCATIONS[province]) return [];
  if (!VIETNAM_LOCATIONS[province][district]) return [];
  return Object.keys(VIETNAM_LOCATIONS[province][district]).sort();
}

/**
 * Lấy tọa độ GPS của phường/xã
 */
function getWardCoords(province, district, ward) {
  try {
    return VIETNAM_LOCATIONS[province][district][ward];
  } catch (e) {
    return null;
  }
}

/**
 * Tính khoảng cách Haversine giữa hai tọa độ (đơn vị km)
 */
function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.asin(Math.sqrt(a));
}

/**
 * Tìm phường/xã gần nhất với tọa độ GPS đầu vào
 * Trả về { province, district, ward, lat, lon }
 */
function findNearestWard(userLat, userLon) {
  let best = null;
  let bestDist = Infinity;
  for (const [province, districts] of Object.entries(VIETNAM_LOCATIONS)) {
    for (const [district, wards] of Object.entries(districts)) {
      for (const [ward, coords] of Object.entries(wards)) {
        const d = haversineKm(userLat, userLon, coords.lat, coords.lon);
        if (d < bestDist) {
          bestDist = d;
          best = { province, district, ward, lat: coords.lat, lon: coords.lon };
        }
      }
    }
  }
  return best;
}
