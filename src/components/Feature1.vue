<template>
  <div>
    <!-- NOTIFIKASI -->
    <transition name="toast-slide">
      <div v-if="notification.show" class="toast-notification" :class="`toast-${notification.type}`">
        <span class="toast-icon">⚠️</span>
        <span class="toast-message">{{ notification.message }}</span>
      </div>
    </transition>

    <!-- FORM POPUP -->
    <transition name="fade-scale-form">
      <div v-if="showForm" class="form-overlay">
        <div class="form-card">
          <button class="close-form-btn" @click="closeForm">&times;</button>

          <h2 class="form-title">Prediksi Waktu Tanam Optimal</h2>

          <div class="form-section-group">
            <!-- KATEGORI -->
            <div class="form-group">
              <label>Kategori Tanaman</label>
              <select class="form-input" v-model="selectedCategory">
                <option disabled value="">Pilih Kategori</option>
                <option v-for="(plants, category) in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>

            <!-- TANAMAN -->
            <div class="form-group">
              <label>Tanaman</label>
              <select class="form-input" v-model="selectedTanaman" :disabled="!selectedCategory">
                <option disabled value="">Pilih Tanaman</option>
                <option v-for="tanaman in filteredTanaman" :key="tanaman">
                  {{ tanaman }}
                </option>
              </select>
            </div>

            <!-- PROVINSI -->
            <div class="form-group">
              <label>Provinsi</label>
              <select class="form-input" v-model="selectedProvinsi">
                <option disabled value="">Pilih Provinsi</option>
                <option v-for="provinsi in provinces" :key="provinsi.id" :value="provinsi.id">
                  {{ provinsi.name }}
                </option>
              </select>
            </div>

            <!-- KOTA -->
            <div class="form-group">
              <label>Kabupaten/Kota</label>
              <select class="form-input" v-model="selectedKabupaten" :disabled="!selectedProvinsi">
                <option disabled value="">Pilih Kabupaten/Kota</option>
                <option v-for="kab in filteredKabupaten" :key="kab.id" :value="kab.name">
                  {{ kab.name }}
                </option>
              </select>
            </div>

            <!-- TANGGAL -->
            <div class="form-group">
              <label>Tanggal Prediksi</label>
              <input type="date" class="form-input" v-model="tanggal" />
            </div>
          </div>

          <!-- JENIS TANAH -->
          <div class="form-group soil-group">
            <label>Jenis Tanah</label>
            <select class="form-input" v-model="tanah" :disabled="!selectedTanaman">
              <option disabled value="">Pilih Jenis Tanah</option>
              <option v-for="t in filteredSoil" :key="t">{{ t }}</option>
            </select>

            <div v-if="tanah" class="soil-preview-inline">
              <img :src="soilImages[tanah]" :alt="tanah" class="soil-img" />
              <span class="soil-label">{{ tanah }}</span>
            </div>
          </div>

          <!-- ACTION BUTTON -->
          <div class="form-actions">
            <button class="action-btn" @click="submitForm">Prediksi</button>
            <button class="action-btn reset-btn" @click="resetForm">Reset</button>
          </div>
        </div>
      </div>
    </transition>

    <!-- LOADING -->
    <transition name="fade-scale">
      <div v-if="loading" class="fullscreen-loading">
        <div class="loader"></div>
        <h3 style="color:white; font-weight:700;">Sedang memprediksi...</h3>
      </div>
    </transition>

    <!-- HASIL -->
    <transition name="fade-scale">
      <div v-if="resultData" class="fullscreen-result">
        <div class="result-card">
          <button class="close-result-btn" @click="closeResult">&times;</button>

          <h2 class="result-title">Hasil Prediksi Rencana Waktu Tanam</h2>

          <p><strong>Tanaman:</strong> {{ resultData.tanaman }}</p>
          <p><strong>Lokasi:</strong> {{ resultData.lokasi }}</p>
          <p><strong>Tanggal:</strong> {{ resultData.tanggal || '—' }}</p>

          <div class="summary-score" :class="resultData.score >= 75 ? 'score-good' : 'score-bad'">
            <div>
              <div class="score-value">{{ resultData.score }}%</div>
              <div class="score-label">Kesesuaian</div>
            </div>
            <div class="score-right">
              Semakin mendekati 100%, semakin optimal.
            </div>
          </div>

          <!-- TABEL FAKTOR -->
          <div class="comparison-tables">
            <div class="table-card">
              <h4>Faktor Pertumbuhan</h4>

              <table class="result-table">
                <thead>
                  <tr>
                    <th>Indikator</th>
                    <th>Aktual</th>
                    <th>Ideal</th>
                    <th>Selisih</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="(f, i) in resultData.factors" :key="i">
                    <td>{{ f.label }}</td>
                    <td>{{ f.actual }}</td>
                    <td>{{ Array.isArray(f.ideal) ? f.ideal.join(', ') : f.ideal }}</td>
                    <td>{{ f.diff ?? '-' }}</td>
                    <td :class="f.status=='Optimal' ? 'status-ok' : 'status-bad'">{{ f.status }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- SARAN -->
          <div class="advice-section">
            <h3>Saran Optimasi</h3>
            <ul>
              <li v-for="(s, idx) in resultData.saran" :key="idx">{{ s }}</li>
            </ul>
          </div>

        </div>
      </div>
    </transition>
  </div>
</template>

<script>

import provincesData from "@/assets/provinces.json";
import citiesData from "@/assets/cities_cleaned.json";

/* IMPORT GAMBAR TANAH — pastikan file ada di path yang sama */
import Alluvial from "@/assets/alluvial.png";
import Latosol from "@/assets/latosol.jpg";
import Humus from "@/assets/humus.jpg";
import Regosol from "@/assets/regosol.png";
import Gambut from "@/assets/gambut.jpg";
import Podsolik from "@/assets/podsolik.png";
import Andosol from "@/assets/andosol.jpeg";
import Grumusol from "@/assets/grumusol.jpg";
import Lempung from "@/assets/lempung.jpg";
import Sandyloam from "@/assets/sandyloam.jpg";

const CACHE = {};
const CACHE_TTL = 600 * 1000; // ms
const OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search";
const OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast";

/* TANAMAN_DATA (sama persis dengan Flask) */
const TANAMAN_DATA = {
  "Padi": {"curah_hujan":150,"suhu":27,"kelembapan":75,
           "toleransi":{"curah_hujan":50,"suhu":2,"kelembapan":2},
           "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Tanah Lempung","Latosol/Tanah Merah","Grumusol/Tanah Liat Berat"]},
  "Jagung": {"curah_hujan":100,"suhu":25,"kelembapan":65,
             "toleransi":{"curah_hujan":30,"suhu":4,"kelembapan":2},
             "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Tanah Lempung","Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Regosol/Tanah Pasir","Andosol/Tanah Hitam Gunung"]},
  "Kedelai": {"curah_hujan":100,"suhu":25,"kelembapan":65,
              "toleransi":{"curah_hujan":20,"suhu":3,"kelembapan":2},
              "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Tanah Lempung","Alluvial/Tanah Endapan Sungai","Andosol/Tanah Hitam Gunung"]},
  "Kentang": {"curah_hujan":100,"suhu":20,"kelembapan":75,
              "toleransi":{"curah_hujan":20,"suhu":2,"kelembapan":2},
              "jenis_tanah":["Andosol/Tanah Hitam Gunung","Sandy Loam/Tanah Liat Berpasir","Loam/Humus","Latosol/Tanah Merah","Podsolik Merah Kuning","Regosol/Tanah Pasir"]},
  "Pepaya": {"curah_hujan":150,"suhu":27,"kelembapan":75,
             "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Loam/Humus","Andosol/Tanah Hitam Gunung"]},
  "Mangga": {"curah_hujan":100,"suhu":28,"kelembapan":65,
             "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Loam/Humus","Andosol/Tanah Hitam Gunung"]},
  "Jeruk": {"curah_hujan":100,"suhu":27,"kelembapan":65,
            "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
            "jenis_tanah":["Loam/Humus","Alluvial/Tanah Endapan Sungai","Latosol/Tanah Merah","Andosol/Tanah Hitam Gunung"]},
  "Apel": {"curah_hujan":150,"suhu":22,"kelembapan":65,
           "toleransi":{"curah_hujan":20,"suhu":2, "kelembapan":2},
           "jenis_tanah":["Loam/Humus","Andosol/Tanah Hitam Gunung","Latosol/Tanah Merah"]},
  "Pisang": {"curah_hujan":175,"suhu":27,"kelembapan":80,
             "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Loam/Humus","Latosol/Tanah Merah","Andosol/Tanah Hitam Gunung"]},
  "Durian": {"curah_hujan":175,"suhu":27,"kelembapan":80,
             "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Loam/Humus","Latosol/Tanah Merah","Andosol/Tanah Hitam Gunung"]},
  "Cabai": {"curah_hujan":100,"suhu":25,"kelembapan":70,
            "toleransi":{"curah_hujan":30,"suhu":5, "kelembapan":2},
            "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Alluvial/Tanah Endapan Sungai","Andosol/Tanah Hitam Gunung","Loam/Humus"]},
  "Sawi": {"curah_hujan":115,"suhu":23,"kelembapan":75,
           "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
           "jenis_tanah":["Sandy Loam/Tanah Liat Berpasir","Alluvial/Tanah Endapan Sungai","Loam/Humus","Latosol/Tanah Merah"]},
  "Bayam": {"curah_hujan":100,"suhu":23,"kelembapan":70,
            "toleransi":{"curah_hujan":30,"suhu":3,"kelembapan":2},
            "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Loam/Humus","Sandy Loam/Tanah Liat Berpasir","Andosol/Tanah Hitam Gunung"]},
  "Kangkung": {"curah_hujan":150,"suhu":25,"kelembapan":75,
               "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
               "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Loam/Humus","Sandy Loam/Tanah Liat Berpasir","Latosol/Tanah Merah","Gambut"]},
  "Kopi": {"curah_hujan":150,"suhu":23,"kelembapan":75,
           "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
           "jenis_tanah":["Andosol/Tanah Hitam Gunung","Latosol/Tanah Merah","Grumusol/Tanah Liat Berat","Loam/Humus"]},
  "Teh": {"curah_hujan":200,"suhu":23,"kelembapan":85,
          "toleransi":{"curah_hujan":50,"suhu":2, "kelembapan":2},
          "jenis_tanah":["Andosol/Tanah Hitam Gunung","Latosol/Tanah Merah","Podsolik Merah Kuning"]},
  "Pohon Karet": {"curah_hujan":200,"suhu":27,"kelembapan":75,
                  "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
                  "jenis_tanah":["Latosol/Tanah Merah","Podsolik Merah Kuning","Alluvial/Tanah Endapan Sungai","Tanah Lempung"]},
  "Kelapa": {"curah_hujan":175,"suhu":28,"kelembapan":75,
             "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
             "jenis_tanah":["Alluvial/Tanah Endapan Sungai","Sandy Loam/Tanah Liat Berpasir","Tanah Lempung"]},
  "Nanas": {"curah_hujan":100,"suhu":25,"kelembapan":65,
            "toleransi":{"curah_hujan":30,"suhu":3, "kelembapan":2},
            "jenis_tanah":["Regosol/Tanah Pasir","Latosol/Tanah Merah","Podsolik Merah Kuning","Andosol/Tanah Hitam Gunung","Gambut"]},
  "Kelapa Sawit": {"curah_hujan":200,"suhu":28,"kelembapan":80,
                   "toleransi":{"curah_hujan":50,"suhu":3,"kelembapan":2},
                   "jenis_tanah":["Latosol/Tanah Merah","Podsolik Merah Kuning","Alluvial/Tanah Endapan Sungai","Tanah Lempung"]}
};

/* FALLBACK sama persis */
const FALLBACK = {"curah_hujan":800,"suhu":24,"kelembapan":70,"jenis_tanah":[],"toleransi":{"curah_hujan":10,"suhu":10,"kelembapan":10}};

export default {
  name: "Feature1",

  data() {
    return {
      showForm: true,
      selectedCategory: "",
      selectedTanaman: "",
      selectedProvinsi: "",
      selectedKabupaten: "",
      provinces: provincesData,
      allRegencies: citiesData,
      tanah: "",
      tanggal: "",
      loading: false,
      resultData: null,
      notification: {
        show: false,
        message: "",
        type: "error",
        timeoutId: null,
      },
      categories: {
        "Buah-buahan": ["Pepaya", "Mangga", "Jeruk", "Apel", "Pisang", "Durian", "Nanas"],
        "Pertanian & Perkebunan": [
          "Padi",
          "Jagung",
          "Kedelai",
          "Kentang",
          "Cabai",
          "Sawi",
          "Bayam",
          "Kangkung",
          "Kopi",
          "Teh",
          "Pohon Karet",
          "Kelapa",
          "Kelapa Sawit",
        ],
      },
      soilMapping: {
        "Pepaya": ["Alluvial/Tanah Endapan Sungai", "Latosol/Tanah Merah", "Loam/Humus", "Andosol/Tanah Hitam Gunung"],
        "Mangga": ["Alluvial/Tanah Endapan Sungai", "Latosol/Tanah Merah", "Loam/Humus", "Andosol/Tanah Hitam Gunung"],
        "Jeruk": ["Loam/Humus", "Alluvial/Tanah Endapan Sungai", "Latosol/Tanah Merah", "Andosol/Tanah Hitam Gunung"],
        "Apel": ["Loam/Humus", "Andosol/Tanah Hitam Gunung", "Latosol/Tanah Merah"],
        "Pisang": ["Alluvial/Tanah Endapan Sungai", "Loam/Humus", "Latosol/Tanah Merah", "Andosol/Tanah Hitam Gunung"],
        "Durian": ["Loam/Humus", "Latosol/Tanah Merah", "Andosol/Tanah Hitam Gunung"],
        "Nanas": ["Regosol/Tanah Pasir", "Latosol/Tanah Merah", "Podsolik Merah Kuning", "Andosol/Tanah Hitam Gunung", "Gambut"],
        "Padi": ["Alluvial/Tanah Endapan Sungai", "Tanah Lempung", "Latosol/Tanah Merah", "Grumusol/Tanah Liat Berat"],
        "Jagung": [
          "Sandy Loam/Tanah Liat Berpasir",
          "Tanah Lempung",
          "Alluvial/Tanah Endapan Sungai",
          "Latosol/Tanah Merah",
          "Regosol/Tanah Pasir",
          "Andosol/Tanah Hitam Gunung",
        ],
        "Kedelai": [
          "Sandy Loam/Tanah Liat Berpasir",
          "Tanah Lempung",
          "Alluvial/Tanah Endapan Sungai",
          "Andosol/Tanah Hitam Gunung",
        ],
        "Kentang": [
          "Andosol/Tanah Hitam Gunung",
          "Sandy Loam/Tanah Liat Berpasir",
          "Loam/Humus",
          "Latosol/Tanah Merah",
          "Podsolik Merah Kuning",
          "Regosol/Tanah Pasir",
        ],
        "Cabai": ["Sandy Loam/Tanah Liat Berpasir", "Alluvial/Tanah Endapan Sungai", "Andosol/Tanah Hitam Gunung", "Loam/Humus"],
        "Sawi": ["Sandy Loam/Tanah Liat Berpasir", "Alluvial/Tanah Endapan Sungai", "Loam/Humus", "Latosol/Tanah Merah"],
        "Bayam": ["Alluvial/Tanah Endapan Sungai", "Loam/Humus", "Sandy Loam/Tanah Liat Berpasir", "Andosol/Tanah Hitam Gunung"],
        "Kangkung": [
          "Alluvial/Tanah Endapan Sungai",
          "Loam/Humus",
          "Sandy Loam/Tanah Liat Berpasir",
          "Latosol/Tanah Merah",
          "Gambut",
        ],
        "Kopi": ["Andosol/Tanah Hitam Gunung", "Latosol/Tanah Merah", "Grumusol/Tanah Liat Berat", "Loam/Humus"],
        "Teh": ["Andosol/Tanah Hitam Gunung", "Latosol/Tanah Merah", "Podsolik Merah Kuning"],
        "Pohon Karet": ["Latosol/Tanah Merah", "Podsolik Merah Kuning", "Alluvial/Tanah Endapan Sungai", "Tanah Lempung"],
        "Kelapa": ["Alluvial/Tanah Endapan Sungai", "Sandy Loam/Tanah Liat Berpasir", "Tanah Lempung"],
        "Kelapa Sawit": ["Latosol/Tanah Merah", "Podsolik Merah Kuning", "Alluvial/Tanah Endapan Sungai", "Tanah Lempung"],
      },
      soilImages: {
        "Alluvial/Tanah Endapan Sungai": Alluvial,
        "Latosol/Tanah Merah": Latosol,
        "Loam/Humus": Humus,
        "Regosol/Tanah Pasir": Regosol,
        "Gambut": Gambut,
        "Podsolik Merah Kuning": Podsolik,
        "Andosol/Tanah Hitam Gunung": Andosol,
        "Tanah Lempung": Lempung,
        "Sandy Loam/Tanah Liat Berpasir": Sandyloam,
        "Grumusol/Tanah Liat Berat": Grumusol,
      }
    };
  },

  computed: {
    filteredTanaman() {
      return this.selectedCategory ? this.categories[this.selectedCategory] : [];
    },

    filteredSoil() {
      return this.selectedTanaman ? this.soilMapping[this.selectedTanaman] : [];
    },

    filteredKabupaten() {
      if (!this.selectedProvinsi) return [];
      return this.allRegencies.filter(k => Number(k.province_id) === Number(this.selectedProvinsi));
    },
  },

  methods: {
    showNotification(message, type = "error", duration = 3000) {
      clearTimeout(this.notification.timeoutId);
      this.notification.message = message;
      this.notification.type = type;
      this.notification.show = true;
      this.notification.timeoutId = setTimeout(() => {
        this.notification.show = false;
      }, duration);
    },

    resetForm() {
      this.selectedCategory = "";
      this.selectedTanaman = "";
      this.selectedProvinsi = "";
      this.selectedKabupaten = "";
      this.tanah = "";
      this.tanggal = "";
      this.resultData = null;
    },

    closeForm() {
      this.showForm = false;
      this.$emit("closeFeature");
    },

    closeResult() {
      this.resultData = null;
      this.showForm = true;
    },

    /* ----------------- CACHE HELPERS ----------------- */
    cache_get(key) {
      const item = CACHE[key];
      if (!item) return null;
      if (Date.now() - item.ts > CACHE_TTL) {
        delete CACHE[key];
        return null;
      }
      return item.value;
    },

    cache_set(key, value) {
      CACHE[key] = { value, ts: Date.now() };
    },

    /* ----------------- NORMALIZE LOCATION ----------------- */
    normalize_location_name(raw) {
      if (!raw) return raw;
      let name = String(raw).toLowerCase();
      const prefixes = ["kabupaten ", "kab ", "kab. ", "kota ", "kota administrasi "];
      for (const p of prefixes) {
        if (name.startsWith(p)) name = name.slice(p.length);
      }
      if (name.includes(",")) name = name.split(",")[0];
      return name.trim().replace(/\b\w/g, c => c.toUpperCase());
    },

    /* ----------------- GEOCODING ----------------- */
    async geocode_location(name) {
      const key = `geo:${String(name).trim().toLowerCase()}`;
      const cached = this.cache_get(key);
      if (cached) return cached;
      const params = new URLSearchParams({ name });
      const url = `${OPEN_METEO_GEOCODE}?${params.toString()}`;
      const resp = await fetch(url, { method: "GET" });
      if (!resp.ok) throw new Error(`Geocoding gagal: ${resp.status}`);
      const j = await resp.json();
      const results = j.results;
      if (!results || results.length === 0) throw new Error("Lokasi tidak ditemukan");
      const lat = results[0].latitude;
      const lon = results[0].longitude;
      if (lat == null || lon == null) throw new Error("Geocoding tidak mengembalikan koordinat");
      this.cache_set(key, [lat, lon]);
      return [lat, lon];
    },

    /* ----------------- FORECAST ----------------- */
    async fetch_forecast_open_meteo(lat, lon) {
      const key = `fc:${lat}:${lon}`;
      const cached = this.cache_get(key);
      if (cached) return cached;
      const params = new URLSearchParams({
        latitude: String(lat),
        longitude: String(lon),
        daily: "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean",
        timezone: "Asia/Jakarta"
      });
      const url = `${OPEN_METEO_FORECAST}?${params.toString()}`;
      const resp = await fetch(url, { method: "GET" });
      if (!resp.ok) throw new Error(`Forecast gagal: ${resp.status}`);
      const j = await resp.json();
      if (!j.daily) throw new Error("Data forecast tidak tersedia");
      this.cache_set(key, j);
      return j;
    },

    /* ----------------- UTILS ----------------- */
    round2(v) {
      try { return Math.round(Number(v) * 100) / 100; }
      catch { return v; }
    },

    safe_float(v, def=0.0) {
      const n = Number(v);
      return Number.isFinite(n) ? n : def;
    },

    evaluate_indicator(actual, ideal, toleransi) {
      try {
        const a = Number(actual);
        const i = Number(ideal);
        const t = Number(toleransi);
        const diff = Math.abs(a - i);
        const status = diff <= t ? "Optimal" : "Kurang Optimal";
        return { actual: this.round2(a), ideal: this.round2(i), toleransi: t, diff: this.round2(diff), status };
      } catch (e) {
        console.error("evaluateIndicator error:", e);
        return { actual: actual, ideal: ideal, toleransi: toleransi, diff: null, status: "Tidak tersedia" };
      }
    },

    build_suggestions(ch_obj, suhu_obj, kelembapan_obj, tanah_ok, tanah_user, ideal_tanah_list) {
      const suggestions = [];
      if (ch_obj.status !== "Optimal") {
        const a = this.safe_float(ch_obj.actual), i = this.safe_float(ch_obj.ideal);
        if (a < i) suggestions.push(`Curah hujan kurang ~${this.round2(i - a)} mm/bulan. Tambahkan penyiraman.`);
        else suggestions.push(`Curah hujan berlebih ~${this.round2(a - i)} mm/bulan. Kurangi irigasi/drainase.`);
      }
      if (suhu_obj.status !== "Optimal") {
        const a = this.safe_float(suhu_obj.actual), i = this.safe_float(suhu_obj.ideal);
        if (a < i) suggestions.push("Suhu rendah. Gunakan mulsa gelap atau mini greenhouse.");
        else suggestions.push("Suhu tinggi. Gunakan naungan atau penyiraman pendinginan.");
      }
      if (kelembapan_obj.status !== "Optimal") {
        const a = this.safe_float(kelembapan_obj.actual), i = this.safe_float(kelembapan_obj.ideal);
        if (a < i) suggestions.push("Kelembapan rendah. Tingkatkan penyiraman atau gunakan mulsa.");
        else suggestions.push("Kelembapan tinggi. Perbaiki drainase/sirkulasi.");
      }
      if (!tanah_ok) {
        if (ideal_tanah_list && ideal_tanah_list.length) suggestions.push(`Jenis tanah kurang cocok. Disarankan: ${ideal_tanah_list.join(', ')}.`);
        else suggestions.push("Jenis tanah tidak diketahui. Pertimbangkan analisis laboratorium.");
      }
      if (!suggestions.length) suggestions.push("Semua indikator optimal. Pertahankan perawatan standar.");
      return suggestions;
    },

    /* ----------------- SUBMIT (client-side replacement) ----------------- */
    async submitForm() {
      if (!this.selectedCategory || !this.selectedTanaman || !this.selectedProvinsi || !this.selectedKabupaten || !this.tanah) {
        this.showNotification("Harap isi semua kolom data untuk memprediksi.");
        return;
      }

      this.loading = true;
      const lokasi = `${this.selectedKabupaten}, ${this.provinces.find(p => Number(p.id) === Number(this.selectedProvinsi)).name}`;

      try {
        const normalized = this.normalize_location_name(lokasi);
        let lat, lon;
        try {
          [lat, lon] = await this.geocode_location(normalized);
        } catch (geoErr) {
          console.error("Geocoding error:", geoErr);
          this.showNotification("Kota/Lokasi tidak ditemukan.", "error", 4000);
          this.loading = false;
          return;
        }

        let fc;
        try {
          fc = await this.fetch_forecast_open_meteo(lat, lon);
        } catch (fcErr) {
          console.error(fcErr);
          this.showNotification("Gagal mengambil data cuaca.", "error", 4000);
          this.loading = false;
          return;
        }

        // ambil data daily
        const daily = fc.daily || {};
        const time_list = daily.time || [];
        const precip_list = daily.precipitation_sum || [];
        const tmax_list = daily.temperature_2m_max || [];
        const tmin_list = daily.temperature_2m_min || [];
        const rh_list = daily.relative_humidity_2m_mean || [];

        const n = Math.max(1, Math.min(time_list.length, precip_list.length, tmax_list.length, tmin_list.length, rh_list.length));

        const safe_list = (lst, n) => {
          if (!Array.isArray(lst)) return Array(n).fill(0.0);
          if (lst.length >= n) return lst.slice(0, n);
          return lst.concat(Array(n - lst.length).fill(0.0));
        };

        const precip = safe_list(precip_list, n).map(x => this.safe_float(x));
        const tmax = safe_list(tmax_list, n).map(x => this.safe_float(x));
        const tmin = safe_list(tmin_list, n).map(x => this.safe_float(x));
        const rh = safe_list(rh_list, n).map(x => this.safe_float(x));

        const avg_daily_precip = precip.reduce((a,b)=>a+b,0)/n;
        const curah_hujan_bulanan = avg_daily_precip * 30;
        const suhu_avg = (tmax.reduce((a,b)=>a+b,0) + tmin.reduce((a,b)=>a+b,0)) / (2*n);
        const kelembapan_avg = rh.reduce((a,b)=>a+b,0)/n;

        const ideal = TANAMAN_DATA[this.selectedTanaman] || FALLBACK;
        const used_fallback = !(this.selectedTanaman in TANAMAN_DATA);
        const toleransi = ideal.toleransi || (FALLBACK.toleransi);

        const ch_obj = this.evaluate_indicator(curah_hujan_bulanan, ideal.curah_hujan, toleransi.curah_hujan);
        const suhu_obj = this.evaluate_indicator(suhu_avg, ideal.suhu, toleransi.suhu);
        const kelembapan_obj = this.evaluate_indicator(kelembapan_avg, ideal.kelembapan, toleransi.kelembapan);

        const ideal_tanah_list = ideal.jenis_tanah || [];
        const tanah_ok = ideal_tanah_list.length ? (ideal_tanah_list.includes(this.tanah)) : false;
        const tanah_status = tanah_ok ? "Optimal" : (ideal_tanah_list.length ? "Tidak cocok" : "Tidak diketahui");

        // scoring (sama seperti Flask)
        let score = 0;
        score += ch_obj.status === "Optimal" ? 20 : 0;
        score += suhu_obj.status === "Optimal" ? 30 : 0;
        score += kelembapan_obj.status === "Optimal" ? 15 : 0;
        score += tanah_ok ? 10 : 0;
        const total_suitability = Math.min(Math.max(parseInt(score), 0), 75);

        const suggestions = this.build_suggestions(ch_obj, suhu_obj, kelembapan_obj, tanah_ok, this.tanah, ideal_tanah_list);

        const meta = {
          lat, lon,
          cached_geo: Boolean(this.cache_get(`geo:${normalized.toLowerCase()}`)),
          cached_forecast: Boolean(this.cache_get(`fc:${lat}:${lon}`))
        };

        // bentuk response compatible dengan template
        this.resultData = {
          tanaman: this.selectedTanaman,
          lokasi,
          lokasi_normalized: normalized,
          tanggal: this.tanggal,
          score: total_suitability,
          curah_hujan_bulanan: this.round2(curah_hujan_bulanan),
          suhu_actual: this.round2(suhu_avg),
          kelembapan_actual: this.round2(kelembapan_avg),
          factors: [
            Object.assign({ label: "Curah Hujan" }, ch_obj),
            Object.assign({ label: "Suhu" }, suhu_obj),
            Object.assign({ label: "Kelembapan" }, kelembapan_obj),
            { label: "Jenis Tanah", actual: this.tanah, ideal: ideal_tanah_list, diff: null, status: tanah_status }
          ],
          saran: suggestions,
          note: used_fallback ? "fallback" : "data_tersedia",
          meta
        };

        // tampilkan hasil
        this.showForm = false;

      } catch (e) {
        console.error(e);
        this.showNotification("Kesalahan saat memproses prediksi.", "error", 4500);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* --- Notifikasi Toast --- */
.toast-notification {
  position: fixed;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3000;
  padding: 12px 20px;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
  display: flex;
  align-items: center;
  font-weight: 600;
  color: white;
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.toast-error {
  background-color: #ef4444; /* Merah */
}

.toast-icon {
  margin-right: 10px;
  font-size: 1.2rem;
}

.toast-slide-enter-active, .toast-slide-leave-active {
  transition: all 0.4s ease-in-out;
}
.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-30px);
}
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-30px);
}

/* --- Transisi Utama Form/Overlay --- */
.fade-scale-form-enter-active, .fade-scale-form-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}
.fade-scale-form-enter-from {
  opacity: 0;
}
.fade-scale-form-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.fade-scale-enter-active, .fade-scale-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-scale-enter-from, .fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* --- Form & Result Styles (Tanpa Perubahan dari versi sebelumnya) --- */
.form-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(21, 128, 61, 0.9);
  backdrop-filter: blur(2px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
  box-sizing: border-box;
}

.result-title {
  padding-bottom: 20px;
  color:#064e3b;
}

.form-card {
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  background: white;
  border-radius: 16px;
  box-shadow: 0 15px 40px rgba(0,0,0,0.3);
  padding: 30px;
  position: relative;
  border-top: 5px solid #059669;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  box-sizing: border-box;
}

.close-form-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 2rem;
  font-weight: bold;
  color: #9ca3af;
  background: none;
  border: none;
  cursor: pointer;
  transition: 0.3s;
}
.close-form-btn:hover {
  color: #ef4444;
  transform: rotate(90deg);
}

.form-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #047857;
  margin-bottom: 25px;
  padding-top: 10px;
  padding-bottom: 20px;
  border-bottom: 1px solid #d1fae5;
  margin-top: 20px;
}

.form-section-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background: #f9fafb;
  transition: 0.3s;
}
.form-input:focus {
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5,150,105,0.2);
  outline: none;
  background: white;
}

.soil-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.soil-preview-inline {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 12px;
  padding: 12px;
  width: 100%;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.soil-preview-inline .soil-img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 8px;
}

.soil-preview-inline .soil-label {
  font-weight: 700;
  color: #065f46;
  text-align: center;
  font-size: 1.05rem;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
  margin-top: 20px;
  width: 100%;
  box-sizing: border-box;
}

.action-btn {
  flex: 1 1 140px;
  max-width: 160px;
  padding: 10px 0;
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: 0.3s;
  text-align: center;
}

.action-btn:hover {
  background: #047857;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(5,150,105,0.4);
}

.reset-btn {
  background: #ef4444;
}
.reset-btn:hover {
  background: #dc2626;
}

.fullscreen-loading {
  position: fixed;
  inset: 0;
  background: #1e7f38;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.loader {
  width: 64px;
  height: 64px;
  border: 6px solid #d1fae5;
  border-top-color: #059669;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
  margin-bottom: 14px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.fullscreen-result {
  position: fixed;
  inset: 0;
  background: #1e7f38;
  z-index: 2000;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 25px;
  overflow-y: auto;
  box-sizing: border-box;
}

.result-card {
  background: white;
  width: 95%;
  max-width: 900px;
  border-radius: 20px;
  padding: 30px;
  margin-top: 50px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.25);
  position: relative;
  color: #222;
  overflow-x: hidden;
}

.close-result-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 28px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #333;
}

.note-fallback {
  margin: 10px 0;
  padding: 10px;
  background: #fff7ed;
  border: 1px solid #fde68a;
  border-radius: 8px;
}

.summary-score {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 10px;
  margin-top: 10px;
}

.score-good { background: linear-gradient(90deg,#ecfdf5,#ecfeee); border: 1px solid #bbf7d0; }
.score-bad { background: linear-gradient(90deg,#fff1f2,#fff4f6); border: 1px solid #fecaca; }
.score-value { font-size: 28px; font-weight: 900; color: #065f46; }
.score-label { font-size: 14px; font-weight: 700; color: #065f46; margin-top: 6px; }
.score-right { font-size: 13px; color: #475569; }

.comparison-tables {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.table-card {
  flex: 1 1 320px;
  background: #ffffff;
  border-radius: 10px;
  padding: 12px;
  border: 1px solid #e6eef0;
  box-shadow: 0 6px 18px rgba(2,6,23,0.04);
  overflow-x: auto;
}

.table-card table {
  width: 100%;
  min-width: 500px;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.result-table th, .result-table td {
  padding: 10px;
  border-bottom: 1px solid #eef2f2;
  text-align: left;
}

.result-table thead th {
  font-weight: 700;
  color: #0f172a;
  background: #f0fdf4;
  border-bottom: 2px solid #d1fae5;
}

.status-ok { color: #16a34a; font-weight: 700; }
.status-bad { color: #dc2626; font-weight: 700; }

.advice-section {
  margin-top: 18px;
  background: #f8fafc;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #e6eef0;
}

.advice-section h3 { margin: 0 0 8px 0; color: #064e3b; }

.advice-section ul { margin: 0; padding-left: 18px; }

.advice-section li { margin-bottom: 8px; color: #374151; }

@media (max-width:900px) {
    .soil-preview-inline { max-width: 280px; padding: 10px; }
    .soil-preview-inline .soil-img { height: 160px; }
    .soil-preview-inline .soil-label { font-size: 1rem; }

    .form-actions { 
        flex-wrap: wrap; 
        justify-content: center; 
        gap: 15px; 
    }
    .action-btn { 
        max-width: 160px; 
        width: 45%; 
        font-size: 0.9rem; 
        padding: 6px 12px; 
    }

    .table-card table { min-width: 450px; }
}

@media (max-width: 500px) {
    .form-section-group {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }

    .form-card {
        padding: 20px 15px;
    }
    
    .form-group {
        width: 100%;
    }

    .form-input {
        width: 100%;
        box-sizing: border-box;
        padding: 8px 10px;
        font-size: 0.95rem;
    }
    
    .form-actions { 
        flex-direction: row; 
        justify-content: center; 
        gap: 15px; 
    }
    .action-btn { 
        width: 45%; 
        max-width: 140px; 
        font-size: 0.9rem; 
        padding: 8px 10px; 
    }
}
</style>
