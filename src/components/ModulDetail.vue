<template>
  <div class="page-wrapper">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="loader"></div>
        <p class="loading-text">{{ loadingMessage }}</p>
      </div>
    </div>

    <button class="back-btn" @click="goBack">← Kembali</button>

    <div class="detail-card">
      <h1 class="title">{{ modul.title }}</h1>
      <p class="subtitle">{{ modul.description }}</p>

      <!-- CREATOR INPUT -->
      <div v-if="isCreator && modul.status === 'draft'" class="form-card">
        <h2 class="section-title">Isi Materi Modul</h2>

        <div class="input-group">
          <label>Materi Lengkap</label>
          <textarea
            v-model="userMaterial"
            placeholder="Tulis materi lengkap di sini..."
            maxlength="3000"
          ></textarea>
          <small
            class="char-count"
            :class="{
              'char-warning': userMaterial.length < 20,
              'char-max': userMaterial.length >= 3000
            }"
          >
            {{ userMaterial.length }}/3000 karakter
            <span v-if="userMaterial.length < 20"> (minimum 20)</span>
            <span v-if="userMaterial.length >= 3000"> (maksimal tercapai)</span>
          </small>
        </div>

        <div class="input-group">
          <label>Link Video YouTube (opsional)</label>
          <input
            type="text"
            v-model="videoLink"
            placeholder="Masukkan link YouTube"
          />
        </div>

        <button class="save-btn" @click="saveMaterial">
          Simpan Materi
        </button>
      </div>

      <!-- ADMIN PANEL -->
      <div v-if="isAdmin && modul.status === 'pending'" class="admin-section">
        <h2 class="section-title">Panel Verifikasi Admin</h2>

        <div v-if="creatorMaterial" class="materi-card">
          <p class="materi-text">{{ creatorMaterial.text }}</p>

          <!-- EMBED VIDEO (ADMIN VIEW) -->
          <div
            v-if="creatorMaterial.videoLink && getEmbedUrl(creatorMaterial.videoLink)"
            class="video-embed"
          >
            <iframe
              :src="getEmbedUrl(creatorMaterial.videoLink)"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </div>

        <div class="admin-buttons">
          <button class="verify-btn" @click="approveModul">
            ✅ Verifikasi Modul
          </button>
          <button class="reject-btn" @click="showRejectModal = true">
            ❌ Tolak Modul
          </button>
        </div>
      </div>

      <!-- APPROVED MATERIAL -->
      <div
        v-if="allMaterials.length && (modul.status === 'approved' || !modul.status)"
        class="materi-wrapper"
      >
        <h2 class="section-title">Materi Lengkap</h2>

        <div
          v-for="(m, i) in allMaterials"
          :key="i"
          class="materi-card"
        >
          <p class="materi-text">{{ m.text }}</p>

          <!-- EMBED VIDEO (USER VIEW) -->
          <div
            v-if="m.videoLink && getEmbedUrl(m.videoLink)"
            class="video-embed"
          >
            <iframe
              :src="getEmbedUrl(m.videoLink)"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL REJECT -->
    <div
      v-if="showRejectModal"
      class="modal-overlay"
      @click.self="showRejectModal = false"
    >
      <div class="reject-modal">
        <h2 class="modal-title">Pilih Alasan Penolakan</h2>

        <div class="reject-options">
          <label
            v-for="(reason, idx) in rejectReasons"
            :key="idx"
            class="checkbox-label"
          >
            <input
              type="checkbox"
              :value="reason"
              v-model="selectedReasons"
            />
            <span>{{ reason }}</span>
          </label>
        </div>

        <div class="custom-reason-section">
          <label class="custom-label">💬 Catatan Tambahan (Opsional)</label>
          <textarea
            v-model="customReason"
            class="custom-textarea"
            placeholder="Tulis catatan atau alasan tambahan untuk user..."
            maxlength="500"
          ></textarea>
          <small class="char-count">
            {{ customReason.length }}/500 karakter
          </small>
        </div>

        <div class="modal-buttons">
          <button class="cancel-btn" @click="showRejectModal = false">
            Batal
          </button>
          <button class="submit-btn" @click="submitRejection">
            Simpan
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="toast.show"
      :class="['toast', toast.type, toast.anim]"
    >
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { db, auth } from "@/firebase.js";
import {
  doc,
  getDoc,
  collection,
  addDoc,
  query,
  where,
  updateDoc,
  onSnapshot
} from "firebase/firestore";
import { useRoute } from "vue-router";
import { forbiddenWords } from "@/utils/ForbiddenWords.js";
import { requiredWords } from "@/utils/requiredWords.js";
import { onAuthStateChanged } from "firebase/auth";

export default {
  name: "ModulDetail",
  setup() {
    const route = useRoute();
    const modulId = route.params.id;

    const modul = ref({});
    const authUser = ref(null);
    const isAdmin = ref(false);

    const userMaterial = ref("");
    const videoLink = ref("");

    const allMaterials = ref([]);
    const toast = ref({ show: false, message: "", type: "", anim: "" });

    const showRejectModal = ref(false);
    const selectedReasons = ref([]);
    const customReason = ref("");

    const isLoading = ref(false);
    const loadingMessage = ref("Memuat Materi");

    const rejectReasons = [
      "❌ Judul modul tidak relevan",
      "❌ Deskripsi modul tidak relevan",
      "❌ Materi modul tidak relevan",
      "❌ Modul tidak dapat diverifikasi kebenarannya",
      "❌ Link video tidak relevan",
      "❌ Modul dibuat pada bab yang tidak relevan"
    ];

    onAuthStateChanged(auth, async (user) => {
      authUser.value = user;
      if (user) await checkAdminStatus(user.uid);
      else isAdmin.value = false;
    });

    const checkAdminStatus = async (uid) => {
      try {
        const adminDoc = await getDoc(doc(db, "admins", uid));
        isAdmin.value = adminDoc.exists() && adminDoc.data().isAdmin === true;
      } catch { 
        isAdmin.value = false; 
      }
    };

    const fetchModul = async () => {
      const docRef = doc(db, "modul", modulId);
      onSnapshot(docRef, (snap) => {
        if (snap.exists()) modul.value = snap.data();
      });
    };

    const fetchMaterials = async () => {
      const q = query(
        collection(db, "modul_progress"),
        where("modulId", "==", modulId)
      );
      onSnapshot(q, (snap) => {
        allMaterials.value = snap.docs.map((d) => ({
          id: d.id,
          ...d.data()
        }));
      });
    };

    const isCreator = computed(
      () => authUser.value && modul.value.createdBy === authUser.value.uid
    );

    const creatorMaterial = computed(() =>
      allMaterials.value.find(
        (m) => m.userId === modul.value.createdBy
      )
    );

    /* ================= YOUTUBE EMBED ================= */

    const getYouTubeId = (url) => {
      if (!url) return null;
      const regex =
        /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
      const match = url.match(regex);
      return match ? match[1] : null;
    };

    const getEmbedUrl = (link) => {
      const id = getYouTubeId(link);
      return id ? `https://www.youtube.com/embed/${id}` : null;
    };

    /* ================= NORMALISASI & FILTERING (KONSISTEN DENGAN MODULLIST) ================= */

    // Normalisasi text: hapus karakter khusus, ubah leet speak, lowercase
    const normalizeText = (text) => {
      if (!text) return "";
      let normalized = text.toLowerCase();
      
      // Leet speak mapping yang lebih lengkap
      const leetMap = { 
        "0": "o", "1": "i", "2": "z", "3": "e", "4": "a", 
        "5": "s", "6": "g", "7": "t", "8": "b", "9": "g",
        "@": "a", "$": "s", "!": "i", "|": "i", "€": "e"
      };
      
      // Replace leet speak
      normalized = normalized.split("").map(c => leetMap[c] || c).join("");
      
      // Hapus semua karakter non-alfabet dan spasi
      normalized = normalized.replace(/[^a-z\s]/g, "");
      
      // Hapus multiple spaces jadi single space
      normalized = normalized.replace(/\s+/g, " ").trim();
      
      return normalized;
    };

    // Cek kata terlarang dengan word boundary (per kata)
    const checkForbiddenWords = (text) => {
      if (!text) return [];
      
      const normalized = normalizeText(text);
      const detectedWords = [];
      
      forbiddenWords.forEach((badWord) => {
        const badNormalized = normalizeText(badWord);
        
        // Cek dengan word boundary - kata harus berdiri sendiri
        const regex = new RegExp(`\\b${badNormalized}\\b`, 'gi');
        
        if (regex.test(normalized)) {
          detectedWords.push(badWord);
        }
      });
      
      // Hapus duplikat
      const uniqueWords = [...new Set(detectedWords)];
      
      // Debug log untuk development
      if (uniqueWords.length > 0) {
        console.log("🚫 Kata terlarang terdeteksi:", uniqueWords);
        console.log("📝 Teks yang dinormalisasi:", normalized);
      }
      
      return uniqueWords;
    };

    const checkRequiredWords = (text) => {
      if (!text) return false;
      const normalized = normalizeText(text);
      
      return requiredWords.some((word) => {
        const wordNormalized = normalizeText(word);
        const regex = new RegExp(`\\b${wordNormalized}\\b`, 'gi');
        return regex.test(normalized);
      });
    };

    /* ================================================= */

    const isValidYouTube = (link) => {
      if (!link) return true;
      return /^(https?:\/\/)?(www\.youtube\.com|youtu\.be)\//.test(link);
    };

    const showToast = (msg, type = "error", dur = 3000) => {
      toast.value = { show: true, message: msg, type, anim: "fade-in" };
      setTimeout(() => (toast.value.anim = "fade-out"), dur - 500);
      setTimeout(() => (toast.value.show = false), dur);
    };

    const saveMaterial = async () => {
      // Validasi panjang materi
      if (userMaterial.value.length < 20) {
        return showToast("⚠️ Materi minimal 20 karakter");
      }

      // Cek kata terlarang di materi
      const materialDetected = checkForbiddenWords(userMaterial.value);
      if (materialDetected.length) {
        return showToast(`⚠️ Materi terdeteksi kata terlarang: ${materialDetected.join(", ")}`);
      }

      // Validasi video link
      if (videoLink.value && !isValidYouTube(videoLink.value)) {
        return showToast("⚠️ Link YouTube tidak valid");
      }

      // Cek kata terlarang di video link
      if (videoLink.value) {
        const videoDetected = checkForbiddenWords(videoLink.value);
        if (videoDetected.length) {
          return showToast(`⚠️ Link video terdeteksi kata terlarang: ${videoDetected.join(", ")}`);
        }
      }

      isLoading.value = true;
      loadingMessage.value = "Menyimpan Materi";

      try {
        const hasRequired = checkRequiredWords(userMaterial.value);

        await addDoc(collection(db, "modul_progress"), {
          modulId,
          userId: authUser.value.uid,
          text: userMaterial.value.trim(),
          videoLink: videoLink.value.trim(),
          date: new Date()
        });

        await updateDoc(doc(db, "modul", modulId), {
          status: "pending",
          needsVerification: !hasRequired,
          updatedAt: new Date()
        });

        showToast("✅ Materi berhasil disimpan", "success", 2000);
        setTimeout(() => window.history.back(), 2000);
      } catch (err) {
        console.error("Error saving material:", err);
        isLoading.value = false;
        showToast("❌ Gagal menyimpan materi");
      }
    };

    const approveModul = async () => {
      isLoading.value = true;
      loadingMessage.value = "Memverifikasi Modul";

      try {
        await updateDoc(doc(db, "modul", modulId), {
          status: "approved",
          verifiedBy: authUser.value.uid,
          verifiedAt: new Date()
        });

        showToast("✅ Modul diverifikasi", "success", 2000);
        setTimeout(() => window.history.back(), 2000);
      } catch (err) {
        console.error("Error approving modul:", err);
        isLoading.value = false;
        showToast("❌ Gagal memverifikasi modul");
      }
    };

    const submitRejection = async () => {
      if (!selectedReasons.value.length && !customReason.value.trim()) {
        return showToast("⚠️ Pilih alasan atau isi catatan");
      }

      // Cek kata terlarang di custom reason
      if (customReason.value.trim()) {
        const customDetected = checkForbiddenWords(customReason.value);
        if (customDetected.length) {
          return showToast(`⚠️ Catatan terdeteksi kata terlarang: ${customDetected.join(", ")}`);
        }
      }

      isLoading.value = true;
      showRejectModal.value = false;

      try {
        await updateDoc(doc(db, "modul", modulId), {
          status: "rejected",
          description: [...selectedReasons.value, customReason.value.trim()]
            .filter(Boolean)
            .join("\n"),
          rejectedBy: authUser.value.uid,
          rejectedAt: new Date()
        });

        showToast("✅ Modul ditolak", "success", 2000);
        setTimeout(() => window.history.back(), 2000);
      } catch (err) {
        console.error("Error rejecting modul:", err);
        isLoading.value = false;
        showToast("❌ Gagal menolak modul");
      }
    };

    const goBack = () => window.history.back();

    onMounted(() => {
      fetchModul();
      fetchMaterials();
    });

    return {
      modul,
      userMaterial,
      videoLink,
      allMaterials,
      creatorMaterial,
      isCreator,
      isAdmin,
      toast,
      saveMaterial,
      approveModul,
      submitRejection,
      goBack,
      showRejectModal,
      rejectReasons,
      selectedReasons,
      customReason,
      isLoading,
      loadingMessage,
      getEmbedUrl
    };
  }
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap");
@import url("https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap");

*{-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none;touch-action:manipulation;}
input,textarea,select,button{font-size:16px!important;}

@keyframes fadeIn{from{opacity:0;transform:translateY(-5px);}to{opacity:1;transform:translateY(0);}}
@keyframes toastFadeIn{from{opacity:0;transform:translate(-50%,-20px);}to{opacity:1;transform:translate(-50%,0);}}
@keyframes toastFadeOut{from{opacity:1;transform:translate(-50%,0);}to{opacity:0;transform:translate(-50%,-20px);}}
@keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
@keyframes loadingFadeIn{from{opacity:0;}to{opacity:1;}}
@keyframes materiFadeIn{from{opacity:0;transform:translateY(15px);}to{opacity:1;transform:translateY(0);}}
@keyframes videoFadeIn{from{opacity:0;transform:scale(0.95);}to{opacity:1;transform:scale(1);}}

.loading-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:#4caf50;display:flex;justify-content:center;align-items:center;z-index:9999;animation:loadingFadeIn 0.3s ease-out;}
.loading-content{display:flex;flex-direction:column;align-items:center;gap:20px;}
.loader{width:70px;height:70px;border:6px solid rgba(255,255,255,0.2);border-top:6px solid white;border-right:6px solid rgba(255,255,255,0.8);border-radius:50%;animation:spin 0.6s linear infinite;}
.loading-text{color:white;font-size:clamp(1.1rem,3vw,1.4rem);font-weight:600;font-family:'Montserrat',sans-serif;letter-spacing:0.5px;text-shadow:0 2px 4px rgba(0,0,0,0.1);}
.page-wrapper{background:#eef7ec;min-height:100vh;padding:20px 15px;display:flex;flex-direction:column;align-items:center;font-family:"Montserrat",sans-serif;}
.back-btn{align-self:flex-start;background:#d8ead7;color:#2e6d3b;border:none;padding:10px 20px;border-radius:50px;font-weight:600;cursor:pointer;margin:10px 0 20px 0;transition:0.3s;font-size:clamp(0.85rem,2vw,0.95rem);}
.back-btn:hover{background:#cbe3c9;transform:translateX(-3px);}
.detail-card{width:100%;max-width:860px;background:white;padding:clamp(25px,4vw,35px) clamp(18px,3.5vw,30px);border-radius:22px;box-shadow:0 10px 30px rgba(0,0,0,0.08);word-wrap:break-word;overflow-wrap:break-word;box-sizing:border-box;}
.title{font-size:clamp(1.5rem,4vw,2.2rem);font-weight:700;color:#255d35;margin-bottom:5px;line-height:1.3;word-wrap:break-word;overflow-wrap:break-word;}
.subtitle{color:#666;font-size:clamp(0.9rem,2vw,1rem);margin-bottom:30px;white-space:pre-line;line-height:1.6;word-wrap:break-word;overflow-wrap:break-word;}
.form-card,.admin-section{background:#f7fbf6;padding:clamp(20px,3vw,25px) clamp(15px,2.5vw,20px);border-radius:18px;box-shadow:0 6px 18px rgba(0,0,0,0.05);margin-bottom:30px;animation:fadeIn 0.5s;word-wrap:break-word;overflow-wrap:break-word;box-sizing:border-box;}
.admin-section .materi-card{animation:materiFadeIn 0.5s ease-out forwards;animation-delay:0.2s;opacity:0;}
.admin-section .video-link-box{animation:videoFadeIn 0.4s ease-out forwards;animation-delay:0.4s;opacity:0;}
.section-title{font-size:clamp(1.1rem,2.5vw,1.3rem);font-weight:600;color:#2e6d3b;margin-bottom:15px;padding-left:12px;border-left:4px solid #a6d8a3;word-wrap:break-word;}
.input-group{display:flex;flex-direction:column;gap:6px;margin-bottom:15px;}
.input-group label{font-weight:600;color:#333;font-size:clamp(0.85rem,2vw,0.95rem);}
.input-group input,.input-group textarea{padding:12px;border-radius:12px;border:1px solid #cbd5c4;font-size:clamp(0.85rem,2vw,0.95rem);transition:0.3s;font-family:'Poppins',sans-serif;width:100%;box-sizing:border-box;}
.input-group input:focus,.input-group textarea:focus{border-color:#4caf50;box-shadow:0 0 6px rgba(76,175,80,0.25);outline:none;}
textarea{min-height:130px;resize:vertical;}
.save-btn{width:100%;padding:13px;background:#4caf50;color:white;border:none;border-radius:14px;font-weight:600;cursor:pointer;transition:0.3s;font-size:clamp(0.9rem,2vw,1rem);}
.save-btn:hover{background:#3f8f43;transform:translateY(-2px);}
.admin-buttons{display:flex;gap:15px;margin-top:20px;flex-wrap:wrap;}
.verify-btn,.reject-btn{flex:1;min-width:150px;padding:13px 20px;border:none;border-radius:14px;font-weight:600;cursor:pointer;transition:0.3s;font-size:clamp(0.85rem,2vw,0.95rem);color:white;word-wrap:break-word;}
.verify-btn{background:#4caf50;}
.verify-btn:hover{background:#3f8f43;transform:translateY(-2px);}
.reject-btn{background:#f44336;}
.reject-btn:hover{background:#d32f2f;transform:translateY(-2px);}
.materi-wrapper{margin-top:30px;}
.materi-card{background:#f1f8f2;padding:18px 20px;border-radius:14px;margin-bottom:15px;box-shadow:0 4px 14px rgba(0,0,0,0.05);word-wrap:break-word;overflow-wrap:break-word;animation:materiFadeIn 0.6s ease-out forwards;opacity:0;}
.materi-card:nth-child(1){animation-delay:0.1s;}
.materi-card:nth-child(2){animation-delay:0.2s;}
.materi-card:nth-child(3){animation-delay:0.3s;}
.materi-card:nth-child(4){animation-delay:0.4s;}
.materi-card:nth-child(5){animation-delay:0.5s;}
.materi-card:nth-child(n+6){animation-delay:0.6s;}
.materi-text{white-space:pre-line;margin-bottom:10px;color:#333;font-family:'Poppins',sans-serif;line-height:1.7;font-size:clamp(0.85rem,2vw,0.95rem);word-wrap:break-word;overflow-wrap:break-word;}
.video-link-box{display:inline-block;padding:6px 10px;background:#d8ead7;color:#2e6d3b;border-radius:8px;font-size:clamp(0.75rem,1.8vw,0.85rem);word-break:break-all;max-width:100%;animation:videoFadeIn 0.5s ease-out forwards;animation-delay:0.3s;opacity:0;}
.video-link-box a{color:#2e6d3b;text-decoration:none;font-weight:600;word-break:break-all;}
.video-link-box a:hover{text-decoration:underline;}
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);display:flex;justify-content:center;align-items:center;z-index:999;padding:20px;}

/* Modal Rejection - Optimized & Compact */
.reject-modal{background:white;padding:clamp(18px,3vw,24px);border-radius:16px;max-width:420px;width:95%;max-height:85vh;overflow-y:auto;box-shadow:0 12px 30px rgba(0,0,0,0.12);animation:fadeIn 0.4s;}
.modal-title{font-size:clamp(1rem,2.2vw,1.2rem);font-weight:600;color:#2e6d3b;margin-bottom:15px;padding-left:10px;border-left:3px solid #a6d8a3;}
.reject-options{display:flex;flex-direction:column;gap:8px;margin:12px 0;}
.checkbox-label{display:flex;align-items:flex-start;gap:8px;padding:10px;background:#f7fbf6;border-radius:8px;cursor:pointer;transition:0.3s;}
.checkbox-label:hover{background:#e8f5e9;}
.checkbox-label input[type="checkbox"]{width:16px;height:16px;cursor:pointer;margin-top:2px;flex-shrink:0;}
.checkbox-label span{flex:1;font-size:clamp(0.8rem,1.8vw,0.88rem);color:#333;line-height:1.4;}

/* Custom Reason Section - Compact */
.custom-reason-section{margin:12px 0;padding:12px;background:#f7fbf6;border-radius:10px;border:1px solid #e0e0e0;}
.custom-label{display:block;font-weight:600;color:#2e6d3b;margin-bottom:6px;font-size:clamp(0.82rem,1.9vw,0.9rem);}
.custom-textarea{width:100%;min-height:70px;padding:10px;border-radius:8px;border:1px solid #cbd5c4;font-size:clamp(0.8rem,1.8vw,0.88rem);font-family:'Poppins',sans-serif;resize:vertical;transition:0.3s;box-sizing:border-box;}
.custom-textarea:focus{border-color:#4caf50;box-shadow:0 0 5px rgba(76,175,80,0.25);outline:none;}
.char-count-modal{display:block;text-align:right;color:#666;font-size:clamp(0.72rem,1.6vw,0.78rem);margin-top:4px;}

/* Modal Buttons - Compact */
.modal-buttons{display:flex;gap:10px;justify-content:flex-end;margin-top:15px;flex-wrap:wrap;}
.cancel-btn,.submit-btn{padding:10px 20px;border:none;border-radius:10px;font-weight:600;cursor:pointer;transition:0.3s;font-size:clamp(0.82rem,1.9vw,0.9rem);color:white;flex:1;min-width:90px;}
.cancel-btn{background:#f44336;}
.cancel-btn:hover{background:#d32f2f;transform:translateY(-2px);}
.submit-btn{background:#4caf50;}
.submit-btn:hover{background:#3f8f43;transform:translateY(-2px);}

/* Toast Notification */
.toast{position:fixed;top:20px;left:50%;transform:translateX(-50%);padding:13px 25px;border-radius:14px;font-weight:600;z-index:2000;max-width:90%;text-align:center;box-shadow:0 8px 20px rgba(0,0,0,0.15);font-size:clamp(0.85rem,2vw,0.95rem);color:white;word-wrap:break-word;}
.toast.error{background:#f44336;}
.toast.success{background:#4caf50;}
.toast.fade-in{animation:toastFadeIn 0.5s ease-out forwards;}
.toast.fade-out{animation:toastFadeOut 0.5s ease-out forwards;}

/* Character Counter with Visual Feedback */
.char-count{display:block;text-align:right;color:#666;font-size:clamp(0.75rem,1.8vw,0.82rem);margin-top:5px;transition:color 0.3s;}
.input-group .char-count{margin-top:5px;}
.char-count.char-warning{color:#f44336;font-weight:600;}
.char-count.char-max{color:#ff9800;font-weight:600;}
.video-embed {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
  margin-top: 12px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
}

.video-embed iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* Responsive Design */
@media(max-width:768px){
  .admin-buttons{flex-direction:column;}
  .verify-btn,.reject-btn{min-width:100%;}
  .loader{width:60px;height:60px;border-width:5px;}
}

@media(max-width:480px){
  .loader{width:55px;height:55px;border-width:4px;}
  .toast{padding:10px 16px;font-size:0.8rem;}
  
  /* Modal Responsive untuk Mobile */
  .reject-modal{padding:15px;max-width:100%;width:92%;}
  .modal-title{font-size:1rem;margin-bottom:12px;}
  .reject-options{gap:6px;margin:10px 0;}
  .checkbox-label{padding:8px;gap:6px;}
  .checkbox-label span{font-size:0.8rem;}
  .custom-reason-section{padding:10px;margin:10px 0;}
  .custom-textarea{min-height:60px;padding:8px;}
  .modal-buttons{flex-direction:column;gap:8px;margin-top:12px;}
  .cancel-btn,.submit-btn{width:100%;min-width:100%;}
}
</style>