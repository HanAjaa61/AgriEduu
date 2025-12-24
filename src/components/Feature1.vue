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
import tanamanData from "@/assets/tanaman.json";
import locationMapping from "@/assets/location_mapping.json";

/* IMPORT GAMBAR TANAH */
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
const CACHE_TTL = 600 * 1000; // 10 menit
const OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search";
const OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast";
const OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive";

/* FALLBACK DATA */
const FALLBACK = {
  curah_hujan: 800,
  suhu: 24,
  kelembapan: 70,
  jenis_tanah: [],
  toleransi: {
    curah_hujan: 10,
    suhu: 10,
    kelembapan: 10
  }
};

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
      tanamanDatabase: tanamanData,
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
    /* Ekstrak kategori dari tanamanDatabase */
    categories() {
      const cats = {};
      for (const nama in this.tanamanDatabase) {
        const kategori = this.tanamanDatabase[nama].kategori || "Lainnya";
        if (!cats[kategori]) cats[kategori] = [];
        cats[kategori].push(nama);
      }
      return cats;
    },

    /* Filter tanaman berdasarkan kategori */
    filteredTanaman() {
      return this.selectedCategory ? this.categories[this.selectedCategory] : [];
    },

    /* Filter jenis tanah berdasarkan tanaman */
    filteredSoil() {
      if (!this.selectedTanaman || !this.tanamanDatabase[this.selectedTanaman]) return [];
      return this.tanamanDatabase[this.selectedTanaman].jenis_tanah || [];
    },

    /* Filter kabupaten berdasarkan provinsi */
    filteredKabupaten() {
      if (!this.selectedProvinsi) return [];
      return this.allRegencies.filter(k => Number(k.province_id) === Number(this.selectedProvinsi));
    },
  },

  methods: {
    /* ==================== NOTIFICATION ==================== */
    showNotification(message, type = "error", duration = 3000) {
      clearTimeout(this.notification.timeoutId);
      this.notification.message = message;
      this.notification.type = type;
      this.notification.show = true;
      this.notification.timeoutId = setTimeout(() => {
        this.notification.show = false;
      }, duration);
    },

    /* ==================== FORM CONTROLS ==================== */
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

    /* ==================== CACHE HELPERS ==================== */
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

    /* ==================== DATE HELPERS ==================== */
    getTodayString() {
      // Dapatkan tanggal hari ini dalam format YYYY-MM-DD (lokal timezone)
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    compareDates(dateStr1, dateStr2) {
      // Bandingkan 2 tanggal string YYYY-MM-DD
      // Return: -1 jika date1 < date2, 0 jika sama, 1 jika date1 > date2
      if (dateStr1 < dateStr2) return -1;
      if (dateStr1 > dateStr2) return 1;
      return 0;
    },

    getDaysDifference(dateStr1, dateStr2) {
      // Hitung selisih hari antara 2 tanggal (dateStr1 - dateStr2)
      const date1Parts = dateStr1.split('-').map(Number);
      const date2Parts = dateStr2.split('-').map(Number);
      
      const d1 = new Date(date1Parts[0], date1Parts[1] - 1, date1Parts[2]);
      const d2 = new Date(date2Parts[0], date2Parts[1] - 1, date2Parts[2]);
      
      const diffMs = d1 - d2;
      return Math.floor(diffMs / (1000 * 60 * 60 * 24));
    },

    addDays(dateStr, days) {
      // Tambahkan sejumlah hari ke tanggal string YYYY-MM-DD
      const parts = dateStr.split('-').map(Number);
      const date = new Date(parts[0], parts[1] - 1, parts[2]);
      date.setDate(date.getDate() + days);
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    /* ==================== LOCATION HELPERS ==================== */
    
    normalize_location_name(raw) {
      if (!raw) return raw;
      
      // Step 1: Clean prefix dulu
      let name = String(raw).toLowerCase();
      const prefixes = ["kabupaten administrasi ", "kota administrasi ", "kabupaten ", "kab. ", "kab ", "kota "];
      for (const p of prefixes) {
        if (name.startsWith(p)) {
          name = name.slice(p.length);
          break; // Stop setelah ketemu prefix pertama
        }
      }
      
      // Step 2: Buang koma dan ambil nama pertama
      if (name.includes(",")) {
        name = name.split(",")[0];
      }
      
      // Step 3: Title case
      name = name.trim().replace(/\b\w/g, c => c.toUpperCase());
      
      // Step 4: Cek mapping dari file JSON
      if (locationMapping[name]) {
        console.log(`🔄 Location mapping: "${name}" → "${locationMapping[name]}"`);
        return locationMapping[name];
      }
      
      return name;
    },

    async geocode_location(name) {
      const key = `geo:${String(name).trim().toLowerCase()}`;
      const cached = this.cache_get(key);
      if (cached) return cached;

      const params = new URLSearchParams({ name });
      const url = `${OPEN_METEO_GEOCODE}?${params.toString()}`;
      
      console.log(`🌍 Geocoding: "${name}"`);
      
      const resp = await fetch(url, { method: "GET" });
      
      if (!resp.ok) throw new Error(`Geocoding gagal: ${resp.status}`);
      
      const j = await resp.json();
      const results = j.results;
      
      if (!results || results.length === 0) {
        // ✅ FALLBACK: Coba dengan nama provinsi saja
        console.warn(`⚠️ Lokasi "${name}" tidak ditemukan, mencoba fallback...`);
        
        // Ambil nama provinsi dari selectedProvinsi
        const provinceObj = this.provinces.find(p => Number(p.id) === Number(this.selectedProvinsi));
        if (provinceObj) {
          let provinceName = provinceObj.name;
          console.log(`🔄 Fallback ke provinsi: "${provinceName}"`);
          
          // Normalisasi nama provinsi (buang prefix "Provinsi")
          provinceName = provinceName.replace(/^Provinsi\s+/i, '').trim();
          
          const fallbackParams = new URLSearchParams({ name: provinceName });
          const fallbackUrl = `${OPEN_METEO_GEOCODE}?${fallbackParams.toString()}`;
          const fallbackResp = await fetch(fallbackUrl, { method: "GET" });
          
          if (fallbackResp.ok) {
            const fallbackData = await fallbackResp.json();
            if (fallbackData.results && fallbackData.results.length > 0) {
              const lat = fallbackData.results[0].latitude;
              const lon = fallbackData.results[0].longitude;
              
              console.log(`✅ Fallback berhasil: ${lat}, ${lon}`);
              
              this.showNotification(
                `📍 Lokasi spesifik tidak ditemukan. Menggunakan koordinat provinsi ${provinceName}.`,
                "warning",
                4000
              );
              
              this.cache_set(key, [lat, lon]);
              return [lat, lon];
            }
          }
        }
        
        throw new Error("Lokasi tidak ditemukan");
      }
      
      const lat = results[0].latitude;
      const lon = results[0].longitude;
      
      if (lat == null || lon == null) {
        throw new Error("Geocoding tidak mengembalikan koordinat");
      }
      
      console.log(`✅ Koordinat ditemukan: ${lat}, ${lon}`);
      
      this.cache_set(key, [lat, lon]);
      return [lat, lon];
    },

    /* ==================== WEATHER DATA FETCHERS ==================== */
    async fetch_forecast_open_meteo(lat, lon, days = 16) {
      const key = `fc:${lat}:${lon}:${days}`;
      const cached = this.cache_get(key);
      if (cached) return cached;
      
      const params = new URLSearchParams({
        latitude: String(lat),
        longitude: String(lon),
        daily: "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean",
        timezone: "Asia/Jakarta",
        forecast_days: String(days)
      });
      
      const url = `${OPEN_METEO_FORECAST}?${params.toString()}`;
      const resp = await fetch(url, { method: "GET" });
      
      if (!resp.ok) throw new Error(`Forecast gagal: ${resp.status}`);
      
      const j = await resp.json();
      if (!j.daily) throw new Error("Data forecast tidak tersedia");
      
      this.cache_set(key, j);
      return j;
    },

    async fetch_historical_data(lat, lon, startDate) {
      // Hanya untuk tanggal >16 hari ke depan (referensi tahun lalu)
      const key = `hist:${lat}:${lon}:${startDate}`;
      const cached = this.cache_get(key);
      if (cached) return cached;
      
      // Ambil 16 hari (konsisten dengan forecast)
      const endDate = this.addDays(startDate, 15); // +15 = total 16 hari
      
      const params = new URLSearchParams({
        latitude: String(lat),
        longitude: String(lon),
        start_date: startDate,
        end_date: endDate,
        daily: "temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean",
        timezone: "Asia/Jakarta"
      });
      
      const url = `${OPEN_METEO_ARCHIVE}?${params.toString()}`;
      const resp = await fetch(url, { method: "GET" });
      
      if (!resp.ok) {
        throw new Error(`Historical data gagal: ${resp.status}`);
      }
      
      const j = await resp.json();
      if (!j.daily) throw new Error("Data historis tidak tersedia");
      
      this.cache_set(key, j);
      return j;
    },

    /* ==================== DATA PROCESSING ==================== */
    round2(v) {
      try {
        return Math.round(Number(v) * 100) / 100;
      } catch {
        return v;
      }
    },

    safe_float(v, def = 0.0) {
      const n = Number(v);
      return Number.isFinite(n) ? n : def;
    },

    safe_list(lst, n) {
      if (!Array.isArray(lst)) return Array(n).fill(0.0);
      if (lst.length >= n) return lst.slice(0, n);
      return lst.concat(Array(n - lst.length).fill(0.0));
    },

    evaluate_indicator(actual, ideal, toleransi) {
      try {
        const a = Number(actual);
        const i = Number(ideal);
        const t = Number(toleransi);
        const diff = Math.abs(a - i);
        const status = diff <= t ? "Optimal" : "Kurang Optimal";
        
        return {
          actual: this.round2(a),
          ideal: this.round2(i),
          toleransi: t,
          diff: this.round2(diff),
          status
        };
      } catch (e) {
        console.error("evaluateIndicator error:", e);
        return {
          actual: actual,
          ideal: ideal,
          toleransi: toleransi,
          diff: null,
          status: "Tidak tersedia"
        };
      }
    },

    build_suggestions(ch_obj, suhu_obj, kelembapan_obj, tanah_ok, ideal_tanah_list) {
      const suggestions = [];
      
      // Saran Curah Hujan
      if (ch_obj.status !== "Optimal") {
        const a = this.safe_float(ch_obj.actual);
        const i = this.safe_float(ch_obj.ideal);
        
        if (a === 0) {
          suggestions.push("⚠️ Tidak ada curah hujan terdeteksi. Pastikan sistem irigasi berfungsi optimal.");
        } else if (a < i) {
          suggestions.push(`💧 Curah hujan kurang ~${this.round2(i - a)} mm (16 hari). Tambahkan penyiraman rutin.`);
        } else {
          suggestions.push(`☔ Curah hujan berlebih ~${this.round2(a - i)} mm (16 hari). Perbaiki sistem drainase.`);
        }
      }
      
      // Saran Suhu
      if (suhu_obj.status !== "Optimal") {
        const a = this.safe_float(suhu_obj.actual);
        const i = this.safe_float(suhu_obj.ideal);
        
        if (a === 0) {
          suggestions.push("⚠️ Data suhu tidak tersedia. Monitoring manual diperlukan.");
        } else if (a < i) {
          suggestions.push(`🌡️ Suhu rendah (~${this.round2(i - a)}°C di bawah ideal). Gunakan mulsa gelap atau mini greenhouse.`);
        } else {
          suggestions.push(`🌡️ Suhu tinggi (~${this.round2(a - i)}°C di atas ideal). Gunakan naungan atau penyiraman pendinginan.`);
        }
      }
      
      // Saran Kelembapan
      if (kelembapan_obj.status !== "Optimal") {
        const a = this.safe_float(kelembapan_obj.actual);
        const i = this.safe_float(kelembapan_obj.ideal);
        
        if (a === 0) {
          suggestions.push("⚠️ Data kelembapan tidak tersedia. Pantau kondisi tanah secara manual.");
        } else if (a < i) {
          suggestions.push(`⚠️ Kelembapan rendah (~${this.round2(i - a)}% di bawah ideal). Tingkatkan penyiraman atau gunakan mulsa.`);
        } else {
          suggestions.push(`⚠️ Kelembapan tinggi (~${this.round2(a - i)}% di atas ideal). Perbaiki drainase dan sirkulasi udara.`);
        }
      }
      
      // Saran Tanah
      if (!tanah_ok) {
        if (ideal_tanah_list && ideal_tanah_list.length) {
          suggestions.push(`🌱 Jenis tanah kurang cocok. Disarankan: ${ideal_tanah_list.slice(0, 2).join(', ')}.`);
        } else {
          suggestions.push("🌱 Jenis tanah tidak diketahui. Pertimbangkan analisis laboratorium.");
        }
      }
      
      if (!suggestions.length) {
        suggestions.push("✅ Semua indikator optimal. Pertahankan perawatan standar.");
      }
      
      return suggestions;
    },

    /* ==================== MAIN SUBMIT HANDLER ==================== */
    async submitForm() {
      // Validasi input
      if (!this.selectedCategory || !this.selectedTanaman || 
          !this.selectedProvinsi || !this.selectedKabupaten || !this.tanah) {
        this.showNotification("Harap isi semua kolom data untuk memprediksi.");
        return;
      }

      this.loading = true;
      
      const provinceObj = this.provinces.find(p => Number(p.id) === Number(this.selectedProvinsi));
      const lokasi = `${this.selectedKabupaten}, ${provinceObj ? provinceObj.name : ''}`;

      try {
        // Step 1: Geocoding
        const normalized = this.normalize_location_name(lokasi);
        let lat, lon;
        
        console.log('📍 GEOCODING DEBUG:');
        console.log('  Input lokasi:', lokasi);
        console.log('  Setelah normalisasi:', normalized);
        
        try {
          [lat, lon] = await this.geocode_location(normalized);
        } catch (geoErr) {
          console.error("❌ Geocoding error:", geoErr);
          this.showNotification("Lokasi tidak ditemukan: " + geoErr.message, "error", 4000);
          this.loading = false;
          return;
        }

        // Step 2: Validasi dan Fetch Weather Data
        let fc;
        let dataSource = "Forecast (Real-time)";
        let periodInfo = "";
        const todayStr = this.getTodayString();
        
        console.log('='.repeat(60));
        console.log('🚀 MULAI PROSES PREDIKSI');
        console.log('='.repeat(60));
        
        if (this.tanggal) {
          const compareResult = this.compareDates(this.tanggal, todayStr);
          const diffDays = this.getDaysDifference(this.tanggal, todayStr);
          
          console.log('📅 INFO TANGGAL:');
          console.log({
            tanggalInput: this.tanggal,
            tanggalSekarang: todayStr,
            selisihHari: diffDays,
            status: diffDays === 0 ? 'HARI INI' : diffDays > 0 ? `+${diffDays} hari kedepan` : `${diffDays} hari lalu`
          });
          
          // ❌ TOLAK tanggal masa lalu
          if (compareResult < 0) {
            this.showNotification(
              "⚠️ Pilih tanggal sekarang atau kedepannya", 
              "error", 
              4000
            );
            this.loading = false;
            return;
          }
          
          // ✅ Tanggal HARI INI atau MASA DEPAN
          if (diffDays === 0) {
            // HARI INI
            fc = await this.fetch_forecast_open_meteo(lat, lon, 16);
            dataSource = "Forecast (Hari Ini)";
            
            const endDateStr = this.addDays(todayStr, 15);
            periodInfo = `${this.tanggal} s/d ${endDateStr} (16 hari)`;
            
          } else if (diffDays > 0 && diffDays <= 16) {
            // 1-16 HARI KE DEPAN
            this.showNotification(
              `📅 Menggunakan data forecast untuk ${diffDays} hari ke depan`, 
              "success", 
              3000
            );
            
            fc = await this.fetch_forecast_open_meteo(lat, lon, 16);
            dataSource = `Forecast (+${diffDays} hari)`;
            
            const endDateStr = this.addDays(this.tanggal, 15);
            periodInfo = `${this.tanggal} s/d ${endDateStr}`;
            
            // Filter data: skip hari-hari sebelum tanggal yang dipilih
            if (fc.daily && fc.daily.time) {
              const startIdx = fc.daily.time.findIndex(d => d === this.tanggal);
              if (startIdx >= 0) {
                console.log(`✂️ Memfilter data: skip ${startIdx} hari pertama, mulai dari index ${startIdx}`);
                fc.daily.time = fc.daily.time.slice(startIdx);
                fc.daily.precipitation_sum = fc.daily.precipitation_sum?.slice(startIdx) || [];
                fc.daily.temperature_2m_max = fc.daily.temperature_2m_max?.slice(startIdx) || [];
                fc.daily.temperature_2m_min = fc.daily.temperature_2m_min?.slice(startIdx) || [];
                fc.daily.relative_humidity_2m_mean = fc.daily.relative_humidity_2m_mean?.slice(startIdx) || [];
              }
            }
            
          } else {
            // >16 HARI - gunakan data historis tahun lalu sebagai referensi
            this.showNotification(
              `📅 Tanggal terlalu jauh (${diffDays} hari). Menggunakan data historis periode sama tahun lalu sebagai referensi.`, 
              "warning", 
              5000
            );
            
            try {
              // Hitung tanggal tahun lalu
              const parts = this.tanggal.split('-').map(Number);
              const lastYearDate = `${parts[0] - 1}-${String(parts[1]).padStart(2, '0')}-${String(parts[2]).padStart(2, '0')}`;
              
              console.log(`📆 Mengambil data historis: ${lastYearDate} (tahun lalu)`);
              
              fc = await this.fetch_historical_data(lat, lon, lastYearDate);
              dataSource = "Data Historis (Tahun Lalu)";
              
              const endDateStr = this.addDays(lastYearDate, 15);
              periodInfo = `${lastYearDate} s/d ${endDateStr} (16 hari - Referensi Tahun Lalu)`;
              
              // ⚠️ Warning tambahan untuk data tahun lalu
              setTimeout(() => {
                this.showNotification(
                  `ℹ️ Data cuaca dari tahun lalu digunakan sebagai referensi. Kondisi aktual tahun ini bisa berbeda.`, 
                  "info", 
                  6000
                );
              }, 5500);
            } catch (histErr) {
              console.error("Historical fallback error:", histErr);
              this.showNotification(
                "Data tidak tersedia. Menggunakan forecast terbaru.", 
                "warning", 
                4000
              );
              fc = await this.fetch_forecast_open_meteo(lat, lon, 16);
              dataSource = "Forecast (Fallback)";
              
              const endDateStr = this.addDays(todayStr, 15);
              periodInfo = `${todayStr} s/d ${endDateStr} (16 hari)`;
            }
          }
          
        } else {
          // TIDAK ADA TANGGAL - default hari ini + 16 hari
          fc = await this.fetch_forecast_open_meteo(lat, lon, 16);
          dataSource = "Forecast (Hari Ini)";
          
          const endDateStr = this.addDays(todayStr, 15);
          periodInfo = `Hari ini s/d ${endDateStr} (16 hari)`;
        }

        // Step 3: Process Weather Data
        const daily = fc.daily || {};
        const time_list = daily.time || [];
        const precip_list = daily.precipitation_sum || [];
        const tmax_list = daily.temperature_2m_max || [];
        const tmin_list = daily.temperature_2m_min || [];
        const rh_list = daily.relative_humidity_2m_mean || [];

        const n = Math.max(1, Math.min(
          time_list.length,
          precip_list.length,
          tmax_list.length,
          tmin_list.length,
          rh_list.length
        ));

        console.log('\n' + '='.repeat(60));
        console.log('📊 DATA WEATHER MENTAH (API Response)');
        console.log('='.repeat(60));
        console.log('Data Source:', dataSource);
        console.log('Jumlah Hari:', n);
        console.log('Periode:', time_list.length > 0 ? `${time_list[0]} s/d ${time_list[time_list.length - 1]}` : 'N/A');
        console.log('\nData Harian (5 hari pertama untuk sample):');
        console.log('Tanggal:', time_list.slice(0, 5));
        console.log('Curah Hujan (mm):', precip_list.slice(0, 5).map(v => this.round2(v)));
        console.log('Suhu Max (°C):', tmax_list.slice(0, 5).map(v => this.round2(v)));
        console.log('Suhu Min (°C):', tmin_list.slice(0, 5).map(v => this.round2(v)));
        console.log('Kelembapan (%):', rh_list.slice(0, 5).map(v => this.round2(v)));

        const precip = this.safe_list(precip_list, n).map(x => this.safe_float(x));
        const tmax = this.safe_list(tmax_list, n).map(x => this.safe_float(x));
        const tmin = this.safe_list(tmin_list, n).map(x => this.safe_float(x));
        const rh = this.safe_list(rh_list, n).map(x => this.safe_float(x));

        console.log('\n' + '='.repeat(60));
        console.log('🧮 PERHITUNGAN RATA-RATA (16 HARI)');
        console.log('='.repeat(60));

        // ✅ CURAH HUJAN: TOTAL 16 HARI (bukan per bulan!)
        const total_curah_hujan_16_hari = precip.reduce((a, b) => a + b, 0);
        const avg_daily_precip = total_curah_hujan_16_hari / n;
        
        console.log('\n💧 CURAH HUJAN:');
        console.log('  Data per hari (mm):', precip.map(v => this.round2(v)));
        console.log('  Total 16 hari:', this.round2(total_curah_hujan_16_hari), 'mm');
        console.log('  Rata-rata harian:', this.round2(avg_daily_precip), 'mm/hari');
        console.log('  Rumus: SUM(' + precip.map(v => this.round2(v)).join(' + ') + ') = ' + this.round2(total_curah_hujan_16_hari) + ' mm');
        
        // ✅ SUHU: RATA-RATA 16 HARI
        const avg_tmax = tmax.reduce((a, b) => a + b, 0) / n;
        const avg_tmin = tmin.reduce((a, b) => a + b, 0) / n;
        const suhu_avg = (avg_tmax + avg_tmin) / 2;
        
        console.log('\n🌡️ SUHU:');
        console.log('  Suhu Max per hari (°C):', tmax.map(v => this.round2(v)));
        console.log('  Suhu Min per hari (°C):', tmin.map(v => this.round2(v)));
        console.log('  Rata-rata Tmax:', this.round2(avg_tmax), '°C');
        console.log('  Rata-rata Tmin:', this.round2(avg_tmin), '°C');
        console.log('  Rata-rata Suhu:', this.round2(suhu_avg), '°C');
        console.log('  Rumus: (Avg_Tmax + Avg_Tmin) / 2 = (' + this.round2(avg_tmax) + ' + ' + this.round2(avg_tmin) + ') / 2 = ' + this.round2(suhu_avg) + '°C');
        
        // ✅ KELEMBAPAN: RATA-RATA 16 HARI
        const kelembapan_avg = rh.reduce((a, b) => a + b, 0) / n;
        
        console.log('\n💨 KELEMBAPAN:');
        console.log('  Kelembapan per hari (%):', rh.map(v => this.round2(v)));
        console.log('  Rata-rata Kelembapan:', this.round2(kelembapan_avg), '%');
        console.log('  Rumus: SUM(' + rh.map(v => this.round2(v)).join(' + ') + ') / ' + n + ' = ' + this.round2(kelembapan_avg) + '%');

        // Warning untuk data 0
        const warnings = [];
        if (total_curah_hujan_16_hari === 0) {
          warnings.push("Curah hujan 0mm terdeteksi");
        }
        if (suhu_avg === 0) {
          warnings.push("Data suhu tidak tersedia");
        }
        if (kelembapan_avg === 0) {
          warnings.push("Data kelembapan tidak tersedia");
        }
        
        if (warnings.length > 0) {
          console.warn('\n⚠️ PERINGATAN:', warnings.join(', '));
          this.showNotification(
            `⚠️ ${warnings.join(', ')}. Data mungkin tidak lengkap atau dalam musim ekstrem.`,
            "warning",
            5000
          );
        }

        // Step 4: Get Ideal Values
        const ideal = this.tanamanDatabase[this.selectedTanaman] || FALLBACK;
        const used_fallback = !(this.selectedTanaman in this.tanamanDatabase);
        const toleransi = ideal.toleransi || FALLBACK.toleransi;

        console.log('\n' + '='.repeat(60));
        console.log('🎯 DATA IDEAL TANAMAN');
        console.log('='.repeat(60));
        console.log('Tanaman:', this.selectedTanaman);
        console.log('Curah Hujan Ideal:', ideal.curah_hujan, 'mm (16 hari)');
        console.log('Suhu Ideal:', ideal.suhu, '°C');
        console.log('Kelembapan Ideal:', ideal.kelembapan, '%');
        console.log('Toleransi Curah Hujan:', toleransi.curah_hujan, 'mm');
        console.log('Toleransi Suhu:', toleransi.suhu, '°C');
        console.log('Toleransi Kelembapan:', toleransi.kelembapan, '%');

        // Step 5: Evaluate Indicators
        console.log('\n' + '='.repeat(60));
        console.log('📈 EVALUASI INDIKATOR');
        console.log('='.repeat(60));

        const ch_obj = this.evaluate_indicator(
          total_curah_hujan_16_hari,
          ideal.curah_hujan,
          toleransi.curah_hujan
        );
        
        console.log('\n💧 Evaluasi Curah Hujan:');
        console.log('  Aktual:', ch_obj.actual, 'mm (16 hari)');
        console.log('  Ideal:', ch_obj.ideal, 'mm');
        console.log('  Toleransi:', ch_obj.toleransi, 'mm');
        console.log('  Selisih:', ch_obj.diff, 'mm');
        console.log('  Status:', ch_obj.status);
        console.log('  Logika: |' + ch_obj.actual + ' - ' + ch_obj.ideal + '| = ' + ch_obj.diff + (ch_obj.diff <= ch_obj.toleransi ? ' ≤ ' : ' > ') + ch_obj.toleransi + ' → ' + ch_obj.status);
        
        const suhu_obj = this.evaluate_indicator(
          suhu_avg,
          ideal.suhu,
          toleransi.suhu
        );
        
        console.log('\n🌡️ Evaluasi Suhu:');
        console.log('  Aktual:', suhu_obj.actual, '°C');
        console.log('  Ideal:', suhu_obj.ideal, '°C');
        console.log('  Toleransi:', suhu_obj.toleransi, '°C');
        console.log('  Selisih:', suhu_obj.diff, '°C');
        console.log('  Status:', suhu_obj.status);
        console.log('  Logika: |' + suhu_obj.actual + ' - ' + suhu_obj.ideal + '| = ' + suhu_obj.diff + (suhu_obj.diff <= suhu_obj.toleransi ? ' ≤ ' : ' > ') + suhu_obj.toleransi + ' → ' + suhu_obj.status);
        
        const kelembapan_obj = this.evaluate_indicator(
          kelembapan_avg,
          ideal.kelembapan,
          toleransi.kelembapan
        );
        
        console.log('\n⚠️ Evaluasi Kelembapan:');
        console.log('  Aktual:', kelembapan_obj.actual, '%');
        console.log('  Ideal:', kelembapan_obj.ideal, '%');
        console.log('  Toleransi:', kelembapan_obj.toleransi, '%');
        console.log('  Selisih:', kelembapan_obj.diff, '%');
        console.log('  Status:', kelembapan_obj.status);
        console.log('  Logika: |' + kelembapan_obj.actual + ' - ' + kelembapan_obj.ideal + '| = ' + kelembapan_obj.diff + (kelembapan_obj.diff <= kelembapan_obj.toleransi ? ' ≤ ' : ' > ') + kelembapan_obj.toleransi + ' → ' + kelembapan_obj.status);

        // Step 6: Evaluate Soil
        const ideal_tanah_list = ideal.jenis_tanah || [];
        const tanah_ok = ideal_tanah_list.length ? ideal_tanah_list.includes(this.tanah) : false;
        const tanah_status = tanah_ok ? "Optimal" : (ideal_tanah_list.length ? "Tidak cocok" : "Tidak diketahui");

        console.log('\n🌱 Evaluasi Jenis Tanah:');
        console.log('  Tanah Aktual:', this.tanah);
        console.log('  Tanah Ideal:', ideal_tanah_list.join(', ') || 'Tidak ada data');
        console.log('  Status:', tanah_status);

        // Step 7: Calculate Score
        let score = 0;
        const score_breakdown = {};
        
        if (ch_obj.status === "Optimal") {
          score += 20;
          score_breakdown.curah_hujan = 20;
        } else {
          score_breakdown.curah_hujan = 0;
        }
        
        if (suhu_obj.status === "Optimal") {
          score += 30;
          score_breakdown.suhu = 30;
        } else {
          score_breakdown.suhu = 0;
        }
        
        if (kelembapan_obj.status === "Optimal") {
          score += 15;
          score_breakdown.kelembapan = 15;
        } else {
          score_breakdown.kelembapan = 0;
        }
        
        if (tanah_ok) {
          score += 10;
          score_breakdown.tanah = 10;
        } else {
          score_breakdown.tanah = 0;
        }
        
        const total_suitability = Math.min(Math.max(parseInt(score), 0), 75);

        console.log('\n' + '='.repeat(60));
        console.log('🎯 SKOR KESESUAIAN');
        console.log('='.repeat(60));
        console.log('Breakdown Skor:');
        console.log('  Curah Hujan:', score_breakdown.curah_hujan, '/ 20 poin');
        console.log('  Suhu:', score_breakdown.suhu, '/ 30 poin');
        console.log('  Kelembapan:', score_breakdown.kelembapan, '/ 15 poin');
        console.log('  Jenis Tanah:', score_breakdown.tanah, '/ 10 poin');
        console.log('─'.repeat(40));
        console.log('TOTAL SKOR:', total_suitability, '/ 75 poin');
        console.log('Persentase:', this.round2((total_suitability / 75) * 100) + '%');

        // Step 8: Generate Suggestions
        const suggestions = this.build_suggestions(
          ch_obj,
          suhu_obj,
          kelembapan_obj,
          tanah_ok,
          ideal_tanah_list
        );

        console.log('\n' + '='.repeat(60));
        console.log('💡 SARAN & REKOMENDASI');
        console.log('='.repeat(60));
        suggestions.forEach((s, i) => {
          console.log((i + 1) + '.', s);
        });

        // Step 9: Build Metadata
        const meta = {
          lat,
          lon,
          data_source: dataSource,
          period: periodInfo || `${n} hari data`,
          days_calculated: n,
          cached_geo: Boolean(this.cache_get(`geo:${normalized.toLowerCase()}`)),
          cached_forecast: Boolean(this.cache_get(`fc:${lat}:${lon}:16`))
        };

        console.log('\n' + '='.repeat(60));
        console.log('ℹ️ METADATA');
        console.log('='.repeat(60));
        console.log('Koordinat:', `${lat}, ${lon}`);
        console.log('Sumber Data:', dataSource);
        console.log('Periode:', periodInfo);
        console.log('Jumlah Hari:', n);
        console.log('Cache Geo:', meta.cached_geo ? 'Ya' : 'Tidak');
        console.log('Cache Forecast:', meta.cached_forecast ? 'Ya' : 'Tidak');
        console.log('='.repeat(60));

        // Step 10: Build Result
        this.resultData = {
          tanaman: this.selectedTanaman,
          lokasi,
          lokasi_normalized: normalized,
          tanggal: this.tanggal || "Hari ini",
          score: total_suitability,
          curah_hujan_16_hari: this.round2(total_curah_hujan_16_hari),
          suhu_actual: this.round2(suhu_avg),
          kelembapan_actual: this.round2(kelembapan_avg),
          factors: [
            Object.assign({ label: "Curah Hujan (16 hari)" }, ch_obj),
            Object.assign({ label: "Suhu" }, suhu_obj),
            Object.assign({ label: "Kelembapan" }, kelembapan_obj),
            {
              label: "Jenis Tanah",
              actual: this.tanah,
              ideal: ideal_tanah_list,
              diff: null,
              status: tanah_status
            }
          ],
          saran: suggestions,
          note: used_fallback ? "fallback" : "data_tersedia",
          meta
        };

        // Tampilkan hasil
        this.showForm = false;

        console.log('\n✅ PROSES PREDIKSI SELESAI!');
        console.log('='.repeat(60) + '\n');

      } catch (e) {
        console.error("Submit error:", e);
        this.showNotification(
          "Kesalahan saat memproses prediksi: " + e.message,
          "error",
          4500
        );
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
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  padding: 14px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  font-weight: 600;
  color: white;
  min-width: 300px;
  max-width: 500px;
  transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.toast-error {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
  border: 2px solid #fca5a5;
}

.toast-success {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  border: 2px solid #6ee7b7;
}

.toast-warning {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
  border: 2px solid #fcd34d;
}

.toast-info {
  background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%);
  border: 2px solid #7dd3fc;
}

.toast-icon {
  margin-right: 12px;
  font-size: 1.3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-message {
  flex: 1;
  font-size: 0.95rem;
  line-height: 1.4;
}

.toast-slide-enter-active, .toast-slide-leave-active {
  transition: all 0.4s ease-in-out;
}
.toast-slide-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-40px);
}
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-40px);
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
    .toast-notification {
        min-width: 280px;
        max-width: 90%;
        padding: 12px 18px;
    }
    
    .toast-message {
        font-size: 0.9rem;
    }

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
    .toast-notification {
        top: 15px;
        min-width: 250px;
        padding: 10px 16px;
    }
    
    .toast-icon {
        font-size: 1.1rem;
        margin-right: 10px;
    }
    
    .toast-message {
        font-size: 0.85rem;
    }

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