"""
DKI Jakarta — 6 wilayah (5 Kota Administrasi + 1 Kabupaten Administrasi)
Sumber: BPS DKI Jakarta 2023, UMP DKI 2024, BPS Kemiskinan Sept 2023
"""
PROVINCE = "DKI Jakarta"
PROV_CODE = "31"

REGIONS = [
    # ── Jakarta Pusat ──
    {"bps": "3171", "name": "Kota Jakarta Pusat", "type": "kota",
     "area": 48.13, "lat": -6.1862, "lng": 106.8340,
     "pop": 911000, "pop_gr": -0.31,
     "pdrb": 511.2, "econ_gr": 5.03, "capita": 561000000,
     "unemp": 6.57, "poverty": 3.46, "umk": 5067381,
     "toll_km": 0.5, "station_km": 1.0, "airport_km": 28, "port_km": 12,
     "infra": 95,
     "land_price": 45000000, "house_price": 4500000000, "prop_gr": 4.1, "afford": 12,
     "school": 520, "univ": 35, "hosp": 42, "fac": 90,
     "industrial": False, "ind_names": None, "kek": False,
     "tourism": True, "edu_hub": True, "tod": True, "strat": 75,
     "prov": PROVINCE, "prov_code": PROV_CODE},

    # ── Jakarta Utara ──
    {"bps": "3172", "name": "Kota Jakarta Utara", "type": "kota",
     "area": 146.66, "lat": -6.1384, "lng": 106.8638,
     "pop": 1775000, "pop_gr": -0.18,
     "pdrb": 295.5, "econ_gr": 4.87, "capita": 166500000,
     "unemp": 7.12, "poverty": 5.12, "umk": 5067381,
     "toll_km": 1.0, "station_km": 5.0, "airport_km": 18, "port_km": 3,
     "infra": 88,
     "land_price": 18000000, "house_price": 1800000000, "prop_gr": 5.2, "afford": 22,
     "school": 780, "univ": 15, "hosp": 25, "fac": 72,
     "industrial": True, "ind_names": "KBN Marunda, Cilincing", "kek": False,
     "tourism": True, "edu_hub": False, "tod": True, "strat": 70,
     "prov": PROVINCE, "prov_code": PROV_CODE},

    # ── Jakarta Barat ──
    {"bps": "3173", "name": "Kota Jakarta Barat", "type": "kota",
     "area": 129.54, "lat": -6.1683, "lng": 106.7635,
     "pop": 2434000, "pop_gr": 0.05,
     "pdrb": 310.1, "econ_gr": 5.12, "capita": 127400000,
     "unemp": 6.89, "poverty": 3.84, "umk": 5067381,
     "toll_km": 1.0, "station_km": 3.0, "airport_km": 15, "port_km": 10,
     "infra": 90,
     "land_price": 20000000, "house_price": 2000000000, "prop_gr": 5.8, "afford": 20,
     "school": 1050, "univ": 18, "hosp": 30, "fac": 78,
     "industrial": True, "ind_names": "Cengkareng, Kapuk", "kek": False,
     "tourism": False, "edu_hub": False, "tod": True, "strat": 60,
     "prov": PROVINCE, "prov_code": PROV_CODE},

    # ── Jakarta Selatan ──
    {"bps": "3174", "name": "Kota Jakarta Selatan", "type": "kota",
     "area": 141.27, "lat": -6.2615, "lng": 106.8106,
     "pop": 2226000, "pop_gr": -0.10,
     "pdrb": 480.3, "econ_gr": 5.35, "capita": 215800000,
     "unemp": 5.98, "poverty": 2.89, "umk": 5067381,
     "toll_km": 0.5, "station_km": 2.0, "airport_km": 30, "port_km": 18,
     "infra": 94,
     "land_price": 35000000, "house_price": 3800000000, "prop_gr": 4.5, "afford": 15,
     "school": 950, "univ": 28, "hosp": 38, "fac": 88,
     "industrial": False, "ind_names": None, "kek": False,
     "tourism": True, "edu_hub": True, "tod": True, "strat": 78,
     "prov": PROVINCE, "prov_code": PROV_CODE},

    # ── Jakarta Timur ──
    {"bps": "3175", "name": "Kota Jakarta Timur", "type": "kota",
     "area": 188.03, "lat": -6.2250, "lng": 106.9004,
     "pop": 2937000, "pop_gr": 0.08,
     "pdrb": 340.6, "econ_gr": 5.21, "capita": 116000000,
     "unemp": 7.35, "poverty": 3.52, "umk": 5067381,
     "toll_km": 1.5, "station_km": 2.5, "airport_km": 22, "port_km": 15,
     "infra": 88,
     "land_price": 15000000, "house_price": 1500000000, "prop_gr": 6.5, "afford": 25,
     "school": 1300, "univ": 20, "hosp": 32, "fac": 75,
     "industrial": True, "ind_names": "Pulogadung, Cakung", "kek": False,
     "tourism": False, "edu_hub": False, "tod": True, "strat": 65,
     "prov": PROVINCE, "prov_code": PROV_CODE},

    # ── Kepulauan Seribu ──
    {"bps": "3101", "name": "Kabupaten Kepulauan Seribu", "type": "kabupaten",
     "area": 8.76, "lat": -5.7200, "lng": 106.5900,
     "pop": 24000, "pop_gr": 0.95,
     "pdrb": 1.2, "econ_gr": 4.10, "capita": 50000000,
     "unemp": 5.20, "poverty": 10.25, "umk": 5067381,
     "toll_km": 999, "station_km": 999, "airport_km": 999, "port_km": 0.5,
     "infra": 15,
     "land_price": 3000000, "house_price": 400000000, "prop_gr": 3.0, "afford": 65,
     "school": 20, "univ": 0, "hosp": 1, "fac": 10,
     "industrial": False, "ind_names": None, "kek": False,
     "tourism": True, "edu_hub": False, "tod": False, "strat": 25,
     "prov": PROVINCE, "prov_code": PROV_CODE},
]
