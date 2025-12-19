from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import traceback

app = Flask(__name__)
CORS(app)

CACHE = {}
CACHE_TTL = 600
FORECAST_TIMEOUT = 12
GEOCODE_TIMEOUT = 8

def cache_get(key):
    item = CACHE.get(key)
    if not item:
        return None
    if time.time() - item["ts"] > CACHE_TTL:
        del CACHE[key]
        return None
    return item["value"]

def cache_set(key, value):
    CACHE[key] = {"value": value, "ts": time.time()}

TANAMAN_DATA = {
    "Padi": {"curah_hujan":200,"suhu":27,"kelembapan":75,
             "toleransi":{"curah_hujan":50,"suhu":2,"kelembapan":2},
             "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Tanah Lempung","Latosol/Tanah Merah","Grumusol/Tanah Liat Berat"]},
    "Jagung": {"curah_hujan":100,"suhu":25,"kelembapan":65,
               "toleransi":{"curah_hujan":30,"suhu":4,"kelembapan":2},
               "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Tanah Lempung","Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Regosol/Tanah Pasir","Andosol/Tanah Hitam Gunung"]},
    "Kedelai": {"curah_hujan":75,"suhu":25,"kelembapan":65,
                "toleransi":{"curah_hujan":20,"suhu":3,"kelembapan":2},
                "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Tanah Lempung","Alluvial/Tanah Endapan Sungai","Andosol/Tanah Hitam Gunung"]},
    "Kentang": {"curah_hujan":75,"suhu":20,"kelembapan":75,
                "toleransi":{"curah_hujan":20,"suhu":2,"kelembapan":2},
                "jenis_tanah":["Andosol/Tanah Hitam Gunung","Sandy Loam/Tanah Liat Berpasir","Loam/Humus","Latosol/Tanah Merah","Podsolik Merah Kuning","Regosol/Tanah Pasir"]},
    "Pepaya": {"curah_hujan":150,"suhu":27,"kelembapan":75,
               "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
               "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Loam/Humus","Andosol/Tanah Hitam Gunung"]},
    "Mangga": {"curah_hujan":75,"suhu":28,"kelembapan":65,
               "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
               "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Loam/Humus","Andosol/Tanah Hitam Gunung"]},
    "Jeruk": {"curah_hujan":85,"suhu":27,"kelembapan":65,
              "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
              "jenis_tanah":["Loam/Humus","Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Andosol/Tanah Hitam Gunung"]},
    "Apel": {"curah_hujan":65,"suhu":22,"kelembapan":65,
             "toleransi":{"curah_hujan":20,"suhu":2,"kelembapan":2},
             "jenis_tanah":["Loam/Humus","Andosol/Tanah Hitam Gunung","Latosol/Tanah Merah"]},
    "Pisang": {"curah_hujan":200,"suhu":27,"kelembapan":80,
               "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
               "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Loam/Humus","Latosol/Tanah Merah","Andosol/Tanah Hitam Gunung"]},
    "Durian": {"curah_hujan":200,"suhu":27,"kelembapan":80,
               "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
               "jenis_tanah":["Loam/Humus","Latosol/Tanah Merah","Andosol/Tanah Hitam Gunung"]},
    "Cabai": {"curah_hujan":150,"suhu":25,"kelembapan":70,
              "toleransi":{"curah_hujan":30,"suhu":5,"kelembapan":2},
              "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Alluvial/Tanah Endapan Sungai","Andosol/Tanah Hitam Gunung","Loam/Humus"]},
    "Sawi": {"curah_hujan":115,"suhu":23,"kelembapan":75,
             "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Alluvial/Tanah Endapan Sungai","Loam/Humus","Latosol/Tanah Merah"]},
    "Bayam": {"curah_hujan":115,"suhu":23,"kelembapan":70,
              "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
              "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Loam/Humus","Sandy Loam/Tanah Liat Berpasir","Andosol/Tanah Hitam Gunung"]},
    "Kangkung": {"curah_hujan":150,"suhu":25,"kelembapan":75,
                 "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
                 "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Loam/Humus","Sandy Loam/Tanah Liat Berpasir","Latosol/Tanah Merah","Gambut"]},
    "Kopi": {"curah_hujan":150,"suhu":23,"kelembapan":75,
             "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Andosol/Tanah Hitam Gunung","Latosol/Tanah Merah","Grumusol/Tanah Liat Berat","Loam/Humus"]},
    "Teh": {"curah_hujan":200,"suhu":23,"kelembapan":85,
            "toleransi":{"curah_hujan":50,"suhu":2,"kelembapan":2},
            "jenis_tanah":["Andosol/Tanah Hitam Gunung","Latosol/Tanah Merah","Podsolik Merah Kuning"]},
    "Pohon Karet": {"curah_hujan":200,"suhu":27,"kelembapan":75,
                    "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
                    "jenis_tanah":["Latosol/Tanah Merah","Podsolik Merah Kuning","Alluvial/Tanah Endapan Sungai","Tanah Lempung"]},
    "Kelapa": {"curah_hujan":175,"suhu":28,"kelembapan":75,
               "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
               "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Sandy Loam/Tanah Liat Berpasir","Tanah Lempung"]},
    "Nanas": {"curah_hujan":115,"suhu":25,"kelembapan":65,
              "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
              "jenis_tanah":["Regosol/Tanah Pasir","Latosol/Tanah Merah","Podsolik Merah Kuning","Andosol/Tanah Hitam Gunung","Gambut"]},
    "Kelapa Sawit": {"curah_hujan":225,"suhu":28,"kelembapan":80,
                     "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
                     "jenis_tanah":["Latosol/Tanah Merah","Podsolik Merah Kuning","Alluvial/Tanah Endapan Sungai","Tanah Lempung"]}
}

FALLBACK = {"curah_hujan":800,"suhu":24,"kelembapan":70,"jenis_tanah":[],"toleransi":{"curah_hujan":10,"suhu":10,"kelembapan":10}}

def round2(v):
    try: return round(float(v),2)
    except: return v

def safe_float(v, default=0.0):
    try: return float(v)
    except: return default

def normalize_location_name(raw):
    if not raw:
        return raw
    name = raw.lower()
    prefixes = ["kabupaten ","kab ","kab. ","kota ","kota administrasi "]
    for p in prefixes:
        if name.startswith(p):
            name = name[len(p):]
    if "," in name:
        name = name.split(",")[0]
    return name.strip().title()

OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"

def geocode_location(name):
    key = f"geo:{name.strip().lower()}"
    cached = cache_get(key)
    if cached: return cached
    resp = requests.get(OPEN_METEO_GEOCODE, params={"name":name}, timeout=GEOCODE_TIMEOUT)
    resp.raise_for_status()
    j = resp.json()
    results = j.get("results")
    if not results:
        raise ValueError("Lokasi tidak ditemukan")
    lat = results[0].get("latitude")
    lon = results[0].get("longitude")
    if lat is None or lon is None:
        raise RuntimeError("Geocoding tidak mengembalikan koordinat")
    cache_set(key, (lat,lon))
    return lat, lon

def fetch_forecast_open_meteo(lat, lon):
    key = f"fc:{lat}:{lon}"
    cached = cache_get(key)
    if cached: return cached
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean",
        "timezone": "Asia/Jakarta"
    }
    resp = requests.get(OPEN_METEO_FORECAST, params=params, timeout=FORECAST_TIMEOUT)
    resp.raise_for_status()
    j = resp.json()
    if not j.get("daily"):
        raise RuntimeError("Data forecast tidak tersedia")
    cache_set(key,j)
    return j

def evaluate_indicator(actual, ideal, toleransi):
    try:
        a = float(actual)
        i = float(ideal)
        t = float(toleransi)
    except:
        return {"actual":actual,"ideal":ideal,"toleransi":toleransi,"diff":None,"status":"Tidak tersedia"}
    diff = abs(a-i)
    status = "Optimal" if diff <= t else "Kurang Optimal"
    return {"actual":round2(a),"ideal":round2(i),"toleransi":t,"diff":round2(diff),"status":status}

def build_suggestions(ch_obj,suhu_obj,kelembapan_obj,tanah_ok,tanah_user,ideal_tanah_list):
    suggestions=[]
    if ch_obj["status"]!="Optimal":
        a=safe_float(ch_obj["actual"]); i=safe_float(ch_obj["ideal"])
        if a<i: suggestions.append(f"Curah hujan kurang ~{round2(i-a)} mm/bulan. Tambahkan penyiraman.")
        else: suggestions.append(f"Curah hujan berlebih ~{round2(a-i)} mm/bulan. Kurangi irigasi/drainase.")
    if suhu_obj["status"]!="Optimal":
        a=safe_float(suhu_obj["actual"]); i=safe_float(suhu_obj["ideal"])
        if a<i: suggestions.append("Suhu rendah. Gunakan mulsa gelap atau mini greenhouse.")
        else: suggestions.append("Suhu tinggi. Gunakan naungan atau penyiraman pendinginan.")
    if kelembapan_obj["status"]!="Optimal":
        a=safe_float(kelembapan_obj["actual"]); i=safe_float(kelembapan_obj["ideal"])
        if a<i: suggestions.append("Kelembapan rendah. Tingkatkan penyiraman atau gunakan mulsa.")
        else: suggestions.append("Kelembapan tinggi. Perbaiki drainase/sirkulasi.")
    if not tanah_ok:
        if ideal_tanah_list:
            suggestions.append(f"Jenis tanah kurang cocok. Disarankan: {', '.join(ideal_tanah_list)}.")
        else:
            suggestions.append("Jenis tanah tidak diketahui. Pertimbangkan analisis laboratorium.")
    if not suggestions:
        suggestions.append("Semua indikator optimal. Pertahankan perawatan standar.")
    return suggestions

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message":"API Prediksi Tanam Aktif"}),200

@app.route("/prediksi_tanam", methods=["POST"])
def prediksi_tanam():
    try:
        payload=request.get_json() or {}
        tanaman=payload.get("tanaman")
        lokasi=payload.get("lokasi")
        tanah_user=payload.get("tanah")
        tanggal=payload.get("tanggal")

        if not tanaman or not lokasi or not tanah_user:
            return jsonify({"error":"Data tidak lengkap. Diperlukan: tanaman, lokasi, tanah"}),400

        normalized=normalize_location_name(lokasi)

        try:
            lat,lon=geocode_location(normalized)
        except ValueError as ve:
            return jsonify({"error":"Lokasi tidak ditemukan","detail":str(ve)}),400
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error":"Gagal geocoding","detail":str(e)}),500

        try:
            fc=fetch_forecast_open_meteo(lat,lon)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error":"Gagal fetch forecast","detail":str(e)}),500

        daily=fc.get("daily",{})
        time_list=daily.get("time",[])
        precip_list=daily.get("precipitation_sum",[])
        tmax_list=daily.get("temperature_2m_max",[])
        tmin_list=daily.get("temperature_2m_min",[])
        rh_list=daily.get("relative_humidity_2m_mean",[])

        n=max(1,min(len(time_list),len(precip_list),len(tmax_list),len(tmin_list),len(rh_list)))

        def safe_list(lst,n):
            if not isinstance(lst,list): return [0.0]*n
            if len(lst)>=n: return lst[:n]
            return lst+[0.0]*(n-len(lst))

        precip=safe_list(precip_list,n)
        tmax=safe_list(tmax_list,n)
        tmin=safe_list(tmin_list,n)
        rh=safe_list(rh_list,n)

        avg_daily_precip=sum(safe_float(x) for x in precip)/n
        curah_hujan_bulanan=avg_daily_precip*30
        suhu_avg=(sum(safe_float(x) for x in tmax)+sum(safe_float(x) for x in tmin))/(2*n)
        kelembapan_avg=sum(safe_float(x) for x in rh)/n

        ideal=TANAMAN_DATA.get(tanaman,FALLBACK)
        used_fallback=tanaman not in TANAMAN_DATA
        toleransi=ideal.get("toleransi")

        ch_obj=evaluate_indicator(curah_hujan_bulanan,ideal.get("curah_hujan"),toleransi.get("curah_hujan"))
        suhu_obj=evaluate_indicator(suhu_avg,ideal.get("suhu"),toleransi.get("suhu"))
        kelembapan_obj=evaluate_indicator(kelembapan_avg,ideal.get("kelembapan"),toleransi.get("kelembapan"))

        ideal_tanah_list=ideal.get("jenis_tanah",[])
        tanah_ok=tanah_user in ideal_tanah_list if ideal_tanah_list else False
        tanah_status="Optimal" if tanah_ok else ("Tidak cocok" if ideal_tanah_list else "Tidak diketahui")
        soil_score=25 if tanah_ok else 0

        score = 0
        score += 20 if ch_obj["status"] == "Optimal" else 0
        score += 30 if suhu_obj["status"] == "Optimal" else 0
        score += 15 if kelembapan_obj["status"] == "Optimal" else 0
        score += 10 if tanah_ok else 0

        total_suitability = min(max(int(score), 0), 75)

        suggestions=build_suggestions(
            ch_obj,suhu_obj,kelembapan_obj,tanah_ok,tanah_user,ideal_tanah_list
        )

        meta={
            "lat":lat,
            "lon":lon,
            "cached_geo":bool(cache_get(f"geo:{normalized.lower()}")),
            "cached_forecast":bool(cache_get(f"fc:{lat}:{lon}"))
        }

        response={
            "tanaman":tanaman,
            "lokasi":lokasi,
            "lokasi_normalized":normalized,
            "tanggal":tanggal,
            "score":total_suitability,
            "curah_hujan_bulanan":round2(curah_hujan_bulanan),
            "suhu_actual":round2(suhu_avg),
            "kelembapan_actual":round2(kelembapan_avg),
            "factors":[
                {"label":"Curah Hujan",**ch_obj},
                {"label":"Suhu",**suhu_obj},
                {"label":"Kelembapan",**kelembapan_obj},
                {"label":"Jenis Tanah","actual":tanah_user,"ideal":ideal_tanah_list,"diff":None,"status":tanah_status}
            ],
            "saran":suggestions,
            "note":"fallback" if used_fallback else "data_tersedia",
            "meta":meta
        }

        return jsonify(response),200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error":"Kesalahan server","detail":str(e)}),500

if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")
