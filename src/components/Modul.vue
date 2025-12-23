<template>
  <div class="modul-container">
    <div class="header-content">
      <h1 class="modul-title">Daftar Modul</h1>
      <p class="modul-subtitle">Tambahkan dan lihat modul-modul terkait agrikultur di sini</p>
      <p v-if="babId" class="modul-subtitle" style="margin-top:6px;font-weight:600;color:#2e7d32">Bab: {{ babId }}</p>
    </div>

    <div class="modul-grid">
      <div v-for="modul in visibleModuls" :key="modul.id" class="modul-card">
        <div class="modul-header">
          <div class="modul-number">{{ visibleModuls.indexOf(modul) + 1 }}</div>
          <div class="card-menu" v-if="canEditModul(modul) || canDeleteModul(modul)">
            <span v-if="canEditModul(modul)" @click="editModul(modul)"><i class="fas fa-edit"></i></span>
            <span v-if="canDeleteModul(modul)" @click="promptDelete(modul.id)"><i class="fas fa-trash-alt"></i></span>
          </div>
        </div>

        <div class="modul-name">{{ modul.title }}</div>
        <div class="modul-description">{{ modul.description }}</div>
        
        <div class="modul-cta" :class="{ 'draft-btn': modul.status === 'draft', 'pending-btn': modul.status === 'pending', 'rejected-btn': modul.status === 'rejected' }" @click="handleModulClick(modul)">
          {{ getButtonText(modul.status) }}
        </div>
      </div>

      <div v-if="authUser" class="add-modul-card" @click="openCreateForm">
        <div class="add-modul-inner">
          <i class="fas fa-plus-circle fa-2x"></i>
          <span>Buat Modul Baru</span>
        </div>
      </div>
    </div>

    <div v-if="showForm" class="modal-overlay" @click.self="resetForm">
      <div class="modal-content">
        <h2>{{ editMode ? 'Edit Modul' : 'Buat Modul Baru' }}</h2>
        
        <label>Judul Modul</label>
        <input v-model="newModul.title" placeholder="Judul Modul" />
        
        <label>Deskripsi Modul</label>
        <textarea v-model="newModul.description" placeholder="Deskripsi Modul" class="desc-textarea"></textarea>

        <!-- Materi & Video hanya muncul saat edit dengan status approved -->
        <template v-if="editMode && editingModulStatus === 'approved'">
          <label>Materi Lengkap</label>
          <textarea v-model="newModul.material" placeholder="Tulis materi lengkap di sini..." class="material-textarea"></textarea>
          
          <label>Link Video YouTube (opsional)</label>
          <input v-model="newModul.videoLink" placeholder="Masukkan link YouTube" />
        </template>

        <div class="modal-buttons">
          <button class="cancel-btn" @click="resetForm" :disabled="isSaving">Batal</button>
          <button class="save-btn" :disabled="isSaving" @click="saveModul">
            <span v-if="!isSaving">{{ editMode ? 'Update' : 'Simpan' }}</span>
            <span v-else class="saving-text">Menyimpan...</span>
            <span v-if="isSaving" class="spinner" aria-hidden="true"></span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="toast.show" :class="['toast', toast.type, toast.anim]" role="status" aria-live="polite">{{ toast.message }}</div>

    <div v-if="deleteModal.show" class="modal-overlay" @click.self="closeDeleteModal">
      <div class="delete-modal fade-in">
        <p>Yakin ingin menghapus modul?</p>
        <div class="modal-buttons">
          <button class="save-btn" @click="confirmDelete">Setuju</button>
          <button class="cancel-btn" @click="closeDeleteModal">Batal</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from "vue";
import { forbiddenWords } from "@/utils/ForbiddenWords.js";
import { requiredWords } from "@/utils/requiredWords.js";
import { useRoute, useRouter } from "vue-router";
import { db, auth } from "@/firebase.js";
import { collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, where, orderBy, limit, serverTimestamp, getDoc, onSnapshot } from "firebase/firestore";
import { onAuthStateChanged } from "firebase/auth";

export default {
  name: "ModulList",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const babId = ref(route.params.id || null);
    const modulList = ref([]);
    const newModul = ref({ title: "", description: "", material: "", videoLink: "" });
    const showForm = ref(false);
    const editMode = ref(false);
    const editId = ref(null);
    const editingModulStatus = ref(null);
    const authUser = ref(null);
    const isAdmin = ref(false);
    const isSaving = ref(false);
    const toast = ref({ show: false, message: "", type: "error", anim: "" });
    const deleteModal = ref({ show: false, modulId: null });

    onAuthStateChanged(auth, async (user) => {
      authUser.value = user;
      if (user) await checkAdminStatus(user.uid);
      else isAdmin.value = false;
    });

    const checkAdminStatus = async (uid) => {
      try {
        const adminDoc = await getDoc(doc(db, "admins", uid));
        isAdmin.value = adminDoc.exists() && adminDoc.data().isAdmin === true;
      } catch { isAdmin.value = false; }
    };

    const visibleModuls = computed(() => {
      return modulList.value.filter(modul => {
        const isCreator = authUser.value?.uid === modul.createdBy;
        const status = modul.status || 'approved';
        if (status === 'draft') return isCreator;
        if (status === 'pending') return isCreator || isAdmin.value;
        if (status === 'rejected') return authUser.value !== null;
        if (status === 'approved') return true;
        return false;
      });
    });

    const canEditModul = (modul) => {
      if (!authUser.value) return false;
      const status = modul.status || 'approved';
      if (status === 'pending' || status === 'rejected') return false;
      if (status === 'approved') return modul.createdBy === authUser.value.uid;
      if (status === 'draft') return modul.createdBy === authUser.value.uid;
      return false;
    };

    const canDeleteModul = (modul) => {
      if (!authUser.value) return false;
      const isCreator = modul.createdBy === authUser.value.uid;
      const status = modul.status || 'approved';
      if (isAdmin.value) return true;
      if (status === 'approved') return isCreator;
      if (status === 'rejected') return true;
      if (status === 'pending') return false;
      if (status === 'draft') return isCreator;
      return false;
    };

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

    const showToast = (message, type = "error", duration = 3000) => {
      toast.value = { show: true, message, type, anim: "fade-in" };
      setTimeout(() => (toast.value.anim = "fade-out"), duration - 500);
      setTimeout(() => (toast.value.show = false), duration);
    };

    const fetchModul = async () => {
      try {
        if (!babId.value) { modulList.value = []; return; }
        const q = query(collection(db, "modul"), where("babId", "==", babId.value), orderBy("createdAt", "asc"));
        
        onSnapshot(q, (snapshot) => {
          modulList.value = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
        }, (error) => {
          console.error("Error fetching modul:", error);
          showToast("❌ Gagal mengambil data modul");
        });
      } catch (error) {
        console.error("Error setting up listener:", error);
        showToast("❌ Gagal mengambil data modul");
      }
    };

    const canCreateModul = async () => {
      if (!authUser.value) return false;
      const q = query(collection(db, "modul"), where("createdBy", "==", authUser.value.uid), orderBy("createdAt", "desc"), limit(1));
      const snapshot = await getDocs(q);
      if (!snapshot.empty) {
        const last = snapshot.docs[0].data();
        const diff = Date.now() - last.createdAt?.toMillis();
        return !diff || diff > 60000;
      }
      return true;
    };

    const createModul = async () => {
      try {
        if (!authUser.value) return showToast("⚠️ Lakukan Login Terlebih Dahulu!");
        if (!newModul.value.title.trim()) return showToast("⚠️ Judul wajib diisi");
        
        // Cek kata terlarang di judul
        const titleDetected = checkForbiddenWords(newModul.value.title);
        if (titleDetected.length) {
          return showToast(`⚠️ Judul terdeteksi kata terlarang: ${titleDetected.join(", ")}`);
        }
        
        // Cek kata terlarang di deskripsi
        const descDetected = checkForbiddenWords(newModul.value.description);
        if (descDetected.length) {
          return showToast(`⚠️ Deskripsi terdeteksi kata terlarang: ${descDetected.join(", ")}`);
        }
        
        const allowed = await canCreateModul();
        if (!allowed) return showToast("⚠️ Tunggu beberapa saat sebelum membuat modul baru");
        
        const text = newModul.value.title + " " + newModul.value.description;
        const hasRequiredWord = checkRequiredWords(text);
        
        await addDoc(collection(db, "modul"), {
          title: newModul.value.title.trim(), 
          description: newModul.value.description.trim(), 
          babId: babId.value || null,
          createdBy: authUser.value.uid, 
          createdAt: serverTimestamp(), 
          status: "draft", 
          needsVerification: !hasRequiredWord
        });
        
        showToast("✅ Modul berhasil dibuat", "success");
        resetForm();
        fetchModul();
      } catch (err) { 
        console.error(err);
        showToast("❌ Gagal membuat modul"); 
      }
    };

    const isValidYouTube = (link) => {
      if (!link) return true;
      const regex = /^(https?:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$/;
      return regex.test(link);
    };

    const saveModul = async () => {
      isSaving.value = true;
      try {
        // Validasi judul wajib diisi
        if (!newModul.value.title.trim()) {
          return showToast("⚠️ Judul wajib diisi");
        }
        
        // Cek kata terlarang di judul
        const titleDetected = checkForbiddenWords(newModul.value.title);
        if (titleDetected.length) {
          return showToast(`⚠️ Judul terdeteksi kata terlarang: ${titleDetected.join(", ")}`);
        }
        
        // Cek kata terlarang di deskripsi
        const descDetected = checkForbiddenWords(newModul.value.description);
        if (descDetected.length) {
          return showToast(`⚠️ Deskripsi terdeteksi kata terlarang: ${descDetected.join(", ")}`);
        }

        if (editMode.value) {
          const isApprovedStatus = editingModulStatus.value === 'approved';
          
          if (isApprovedStatus) {
            const materialText = newModul.value.material.trim();
            
            if (materialText.length === 0) {
              return showToast("⚠️ Materi wajib diisi untuk memperbarui modul yang sudah disetujui", "error");
            }
            
            if (materialText.length < 20 || materialText.length > 3000) {
              return showToast("⚠️ Panjang Materi harus 20-3000 karakter", "error");
            }
            
            // Cek kata terlarang di materi
            const materialDetected = checkForbiddenWords(materialText);
            if (materialDetected.length) {
              return showToast(`⚠️ Materi terdeteksi kata terlarang: ${materialDetected.join(", ")}`, "error");
            }
            
            // Cek kata terlarang di video link
            if (newModul.value.videoLink) {
              const videoDetected = checkForbiddenWords(newModul.value.videoLink);
              if (videoDetected.length) {
                return showToast(`⚠️ Link video terdeteksi kata terlarang: ${videoDetected.join(", ")}`, "error");
              }
              
              if (!isValidYouTube(newModul.value.videoLink)) {
                return showToast("⚠️ Link YouTube tidak valid", "error");
              }
            }
            
            try {
              const q = query(collection(db, "modul_progress"), where("modulId", "==", editId.value), where("userId", "==", authUser.value.uid));
              const snapshot = await getDocs(q);
              
              if (!snapshot.empty) {
                await updateDoc(doc(db, "modul_progress", snapshot.docs[0].id), { 
                  text: materialText, 
                  videoLink: newModul.value.videoLink || "", 
                  date: new Date() 
                });
              } else {
                await addDoc(collection(db, "modul_progress"), { 
                  modulId: editId.value, 
                  userId: authUser.value.uid, 
                  text: materialText, 
                  videoLink: newModul.value.videoLink || "", 
                  date: new Date() 
                });
              }

              await updateDoc(doc(db, "modul", editId.value), { 
                title: newModul.value.title.trim(), 
                description: newModul.value.description.trim(), 
                status: "pending", 
                updatedAt: serverTimestamp() 
              });
              
              showToast("✅ Materi berhasil disimpan dan modul menunggu verifikasi admin", "success");
            } catch (err) {
              console.error(err);
              showToast("❌ Gagal menyimpan materi modul", "error");
              return;
            }
          } else {
            try {
              await updateDoc(doc(db, "modul", editId.value), { 
                title: newModul.value.title.trim(), 
                description: newModul.value.description.trim(), 
                updatedAt: serverTimestamp() 
              });
              showToast("✅ Modul berhasil diupdate", "success");
            } catch (err) {
              console.error(err);
              showToast("❌ Gagal mengupdate modul", "error");
              return;
            }
          }
        } else {
          await createModul();
          return;
        }

        resetForm();
        fetchModul();
      } catch (err) {
        console.error(err);
        showToast("❌ Gagal menyimpan modul", "error");
      } finally {
        isSaving.value = false;
      }
    };

    const resetForm = () => {
      newModul.value = { title: "", description: "", material: "", videoLink: "" };
      showForm.value = false;
      editMode.value = false;
      editId.value = null;
      editingModulStatus.value = null;
    };

    const editModul = async (modul) => {
      newModul.value = { title: modul.title, description: modul.description, material: "", videoLink: "" };
      editMode.value = true;
      editId.value = modul.id;
      editingModulStatus.value = modul.status || 'approved';
      
      if ((modul.status || 'approved') === 'approved') {
        try {
          const q = query(collection(db, "modul_progress"), where("modulId", "==", modul.id), where("userId", "==", modul.createdBy));
          const snapshot = await getDocs(q);
          if (!snapshot.empty) {
            const materialData = snapshot.docs[0].data();
            newModul.value.material = materialData.text || "";
            newModul.value.videoLink = materialData.videoLink || "";
          }
        } catch (err) { 
          console.error("Error fetching material:", err); 
        }
      }
      
      showForm.value = true;
    };

    const promptDelete = (id) => { 
      deleteModal.value = { show: true, modulId: id }; 
    };

    const closeDeleteModal = () => { 
      deleteModal.value = { show: false, modulId: null }; 
    };

    const confirmDelete = async () => {
      try {
        const modulId = deleteModal.value.modulId;
        if (!modulId) return;

        const progressQuery = query(collection(db, "modul_progress"), where("modulId", "==", modulId));
        const progressSnapshot = await getDocs(progressQuery);
        for (const docSnap of progressSnapshot.docs) await deleteDoc(doc(db, "modul_progress", docSnap.id));

        const detailQuery = query(collection(db, "modul_detail"), where("modulId", "==", modulId));
        const detailSnapshot = await getDocs(detailQuery);
        for (const docSnap of detailSnapshot.docs) await deleteDoc(doc(db, "modul_detail", docSnap.id));

        await deleteDoc(doc(db, "modul", modulId));
        showToast("✅ Modul dan data terkait berhasil dihapus", "success");
        fetchModul();
      } catch (err) {
        console.error("❌ Error:", err);
        if (err.code === 'permission-denied') showToast("❌ Tidak ada izin untuk menghapus modul ini", "error");
        else showToast(`❌ Gagal menghapus modul: ${err.message}`, "error");
      } finally { 
        closeDeleteModal(); 
      }
    };

    const getButtonText = (status) => {
      const currentStatus = status || 'approved';
      if (currentStatus === "draft") return "Selesaikan Modul";
      if (currentStatus === "pending") return "Menunggu Verifikasi";
      if (currentStatus === "rejected") return "Modul Ditolak";
      return "Lihat Detail";
    };

    const handleModulClick = (modul) => {
      const currentStatus = modul.status || "approved";
      const isCreator = authUser.value?.uid === modul.createdBy;
      if (currentStatus === "draft") { 
        if (isCreator) goToDetail(modul.id); 
        else showToast("❌ Hanya kreator yang dapat mengakses modul draft"); 
        return; 
      }
      if (currentStatus === "pending") { 
        if (isAdmin.value) goToDetail(modul.id); 
        else showToast("❌ Menunggu verifikasi admin"); 
        return; 
      }
      if (currentStatus === "rejected") { 
        showToast("❌ Akses modul ditolak"); 
        return; 
      }
      goToDetail(modul.id);
    };

    const goToDetail = (id) => router.push({ name: "ModulDetail", params: { id } });
    
    const openCreateForm = () => { 
      resetForm(); 
      editMode.value = false;
      showForm.value = true; 
    };

    watch(() => route.params.id, (id) => { 
      babId.value = id; 
      fetchModul(); 
    });

    onMounted(fetchModul);

    return { 
      visibleModuls, 
      newModul, 
      showForm, 
      editMode, 
      authUser, 
      isAdmin, 
      isSaving,
      toast, 
      saveModul, 
      resetForm, 
      editModul, 
      deleteModal, 
      promptDelete, 
      closeDeleteModal, 
      confirmDelete, 
      goToDetail, 
      openCreateForm, 
      babId, 
      getButtonText, 
      handleModulClick, 
      canEditModul, 
      canDeleteModul,
      editingModulStatus
    };
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

@keyframes fadeInSlideUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeIn{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}
@keyframes fadeOut{from{opacity:1;}to{opacity:0;}}
@keyframes toastFadeIn{from{opacity:0;transform:translateX(-50%) translateY(-20px);}to{opacity:1;transform:translateX(-50%) translateY(0);}}
@keyframes toastFadeOut{from{opacity:1;transform:translateX(-50%) translateY(0);}to{opacity:0;transform:translateX(-50%) translateY(-20px);}}

.modul-container{padding:60px 20px;max-width:1280px;margin:auto;font-family:'Poppins',sans-serif;color:#333;background:#f8fcf9;}
.header-content{text-align:center;margin-bottom:50px;animation:fadeInSlideUp 0.8s ease-out forwards;}
.modul-title{font-family:'Montserrat',sans-serif;font-size:clamp(2em,5vw,3em);font-weight:700;color:#1a5e2f;margin-bottom:10px;}
.modul-subtitle{font-size:clamp(1em,2.5vw,1.2em);color:#6c757d;max-width:800px;margin:auto;line-height:1.6;padding:0 15px;}
.modul-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:30px;}
.modul-card{background:#fff;border-radius:16px;padding:30px;box-shadow:0 8px 30px rgba(0,0,0,0.08);transition:all 0.4s;animation:fadeInSlideUp 0.8s ease-out forwards;cursor:pointer;display:flex;flex-direction:column;}
.modul-card:hover{transform:translateY(-8px);box-shadow:0 16px 40px rgba(0,0,0,0.15);}
.modul-header{display:flex;justify-content:flex-start;align-items:center;margin-bottom:15px;position:relative;}
.modul-number{background:#e8f5e9;color:#1a5e2f;font-weight:700;padding:5px 12px;border-radius:50px;font-size:0.9em;}
.modul-name{font-family:'Montserrat',sans-serif;font-size:clamp(1.2em,3vw,1.5em);font-weight:600;color:#2e7d32;margin-bottom:10px;word-wrap:break-word;overflow-wrap:break-word;}
.modul-description{font-size:clamp(0.9em,2vw,1em);color:#777;line-height:1.5;margin-bottom:20px;flex-grow:1;white-space:pre-line;word-wrap:break-word;overflow-wrap:break-word;}
.modul-cta{background:#4CAF50;color:#fff;padding:12px 25px;border-radius:8px;font-size:clamp(0.85em,2vw,0.95em);font-weight:600;text-align:center;transition:all 0.3s;}
.modul-card:hover .modul-cta{background:#388E3C;transform:translateY(-2px);}
.draft-btn{background:#2196F3!important;color:#fff!important;}
.modul-card:hover .draft-btn{background:#1976D2!important;}
.pending-btn{background:#FFC107!important;color:#333!important;}
.modul-card:hover .pending-btn{background:#FFB300!important;}
.rejected-btn{background:#f44336!important;color:#fff!important;}
.modul-card:hover .rejected-btn{background:#d32f2f!important;}
.add-modul-card{display:flex;justify-content:center;align-items:center;color:#4CAF50;font-weight:600;font-size:clamp(1em,2.5vw,1.2em);border:2px dashed #4CAF50;padding:20px;border-radius:16px;transition:all 0.3s;cursor:pointer;min-height:200px;}
.add-modul-card:hover{background:#e8f5e9;transform:translateY(-5px);}
.add-modul-inner{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;}
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);display:flex;justify-content:center;align-items:center;z-index:999;padding:20px;}
.modal-content{background:#fff;padding:30px;border-radius:16px;box-shadow:0 12px 30px rgba(0,0,0,0.12);max-width:500px;width:100%;display:flex;flex-direction:column;gap:15px;animation:fadeInSlideUp 0.5s;max-height:90vh;overflow-y:auto;}
.modal-content h2{margin:0;color:#2e7d32;font-family:'Montserrat',sans-serif;font-size:clamp(1.2em,3vw,1.5em);}
.modal-content label{font-weight:600;margin-bottom:5px;color:#333;font-size:clamp(0.9em,2vw,1em);}
.modal-content input,.modal-content textarea{width:100%;padding:10px 12px;border-radius:12px;border:1px solid #ccc;font-size:clamp(0.85em,2vw,0.95em);transition:all 0.3s;font-family:'Poppins',sans-serif;box-sizing:border-box;}
.modal-content input:focus,.modal-content textarea:focus{border-color:#4CAF50;outline:none;box-shadow:0 0 6px rgba(76,175,80,0.3);}
.modal-content .desc-textarea{min-height:80px;resize:vertical;}
.modal-content .material-textarea{min-height:150px;resize:vertical;}
.modal-buttons{display:flex;justify-content:flex-end;gap:15px;flex-wrap:wrap;}
.save-btn{background:#4CAF50;color:white;border:none;padding:12px 25px;border-radius:12px;cursor:pointer;font-weight:600;transition:all 0.3s;font-size:clamp(0.85em,2vw,0.95em);min-width:100px;}
.save-btn:hover{background:#388E3C;transform:translateY(-2px);}
.cancel-btn{background:#f44336;color:white;border:none;padding:12px 25px;border-radius:12px;cursor:pointer;font-weight:600;transition:all 0.3s;font-size:clamp(0.85em,2vw,0.95em);min-width:100px;}
.cancel-btn:hover{background:#d32f2f;transform:translateY(-2px);}
.card-menu{position:absolute;top:10px;right:10px;display:flex;gap:10px;color:#777;cursor:pointer;font-size:1.1em;}
.card-menu span{transition:all 0.3s;}
.card-menu span:hover{color:#1a5e2f;transform:scale(1.1);}
.toast{position:fixed;top:20px;left:50%;transform:translateX(-50%);padding:12px 24px;border-radius:8px;color:white;font-weight:600;z-index:1000;min-width:220px;text-align:center;pointer-events:none;}
.toast.error{background:#f44336;}
.toast.success{background:#4CAF50;}
.toast.fade-in{animation:toastFadeIn 0.5s forwards;}
.toast.fade-out{animation:toastFadeOut 0.5s forwards;}
.delete-modal{background:#fff;padding:30px;border-radius:16px;max-width:400px;width:90%;text-align:center;box-shadow:0 12px 30px rgba(0,0,0,0.12);animation:fadeIn 0.4s forwards;}
.delete-modal p{font-size:1.1em;color:#333;margin-bottom:20px;}
.delete-modal .modal-buttons{display:flex;justify-content:center;gap:20px;margin-top:20px;}

@media(max-width:992px){.modul-grid{grid-template-columns:repeat(auto-fit,minmax(280px,1fr));}}
@media(max-width:768px){.modul-title{font-size:2em;}.modul-subtitle{font-size:1em;}.modul-grid{grid-template-columns:1fr;}.modul-container{padding:40px 15px;}.delete-modal{padding:20px;}.delete-modal .modal-buttons{flex-direction:column;gap:10px;}.save-btn,.cancel-btn{width:100%;}.toast{padding:10px 16px;min-width:auto;max-width:90%;word-wrap:break-word;font-size:0.9em;}}
</style>