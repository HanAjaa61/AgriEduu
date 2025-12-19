<template>
  <div class="profile-page">
    <div class="profile-container">
      <h1 class="title">Profile</h1>

      <!-- Toast -->
      <div v-if="showToast" class="toast" :class="toastType">
        <span>{{ toastMessage }}</span>
        <button class="close-btn" @click="showToast=false">&times;</button>
      </div>

      <!-- FORM UTAMA -->
      <form @submit.prevent="saveProfile" class="profile-form">

        <div class="form-group center-avatar">
          <img
            :src="selectedAvatar"
            class="avatar-display"
            @click="showAvatarPopup = true"
            @error="handleImageError"
          />
          <p class="avatar-hint">Klik gambar untuk ganti foto profil</p>
        </div>

        <div class="form-group">
          <label class="label">Username</label>
          <input type="text" v-model="username" required />
        </div>

        <div class="form-group">
          <label class="label">Email</label>
          <input type="email" v-model="email" readonly class="input-disabled" />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-save">Simpan</button>
        </div>
      </form>

      <!-- POPUP AVATAR -->
      <div
        v-if="showAvatarPopup"
        class="avatar-popup-overlay"
        @click.self="showAvatarPopup=false"
      >
        <div class="avatar-popup">
          <h3>Pilih Foto Profil</h3>

          <div class="avatar-options">
            <img
              v-for="(url, index) in presetAvatars"
              :key="index"
              :src="url"
              :class="{ selected: url === selectedAvatar }"
              @click="chooseAvatar(url)"
              @error="handleImageError"
              class="avatar-img"
            />
          </div>

          <button class="btn-cancel" @click="showAvatarPopup=false">
            Tutup
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { auth } from "@/firebase.js";
import { updateProfile } from "firebase/auth";
import { useProfileStore } from "@/stores/profile";

const profileStore = useProfileStore();

const username = ref("");
const email = ref("");
const showToast = ref(false);
const toastMessage = ref("");
const toastType = ref("success");
const showAvatarPopup = ref(false);

// =====================
// Semua avatar pakai folder public/avatars
// =====================
const presetAvatars = [
  "/avatars/default.png",
  "/avatars/profile1.png",
  "/avatars/profil2.png",
  "/avatars/profile3.png",
  "/avatars/profile4.png"
];

const selectedAvatar = ref("/avatars/default.png");

// =====================
// Notification
// =====================
const showNotification = (msg, type = "success") => {
  toastMessage.value = msg;
  toastType.value = type;
  showToast.value = true;
  setTimeout(() => (showToast.value = false), 3000);
};

// =====================
// Fallback avatar
// =====================
const handleImageError = () => {
  selectedAvatar.value = "/avatars/default.png";
  profileStore.setProfilePic("/avatars/default.png");
};

// =====================
// Pilih avatar manual
// =====================
const chooseAvatar = (url) => {
  selectedAvatar.value = url;
  profileStore.setProfilePic(url);
  showAvatarPopup.value = false;
};

// =====================
// Simpan profile
// =====================
const saveProfile = async () => {
  const user = auth.currentUser;
  if (!user) return;

  try {
    await updateProfile(user, {
      displayName: username.value,
      photoURL: selectedAvatar.value
    });
    showNotification("✅ Data berhasil disimpan!");
  } catch (err) {
    showNotification(`❌ Error: ${err.message}`, "error");
  }
};

// =====================
// Load user info saat mount
// =====================
onMounted(() => {
  const user = auth.currentUser;
  if (!user) return;

  username.value = user.displayName || "";
  email.value = user.email || "";

  const photo = user.photoURL;

  if (photo && (photo.startsWith("http://") || photo.startsWith("https://"))) {
    selectedAvatar.value = photo;
    profileStore.setProfilePic(photo);
  } else if (presetAvatars.includes(photo)) {
    selectedAvatar.value = photo;
    profileStore.setProfilePic(photo);
  } else {
    selectedAvatar.value = "/avatars/default.png";
    profileStore.setProfilePic("/avatars/default.png");
  }
});
</script>

<style scoped>
/* ************************************************* */
/* 🚀 STYLE DENGAN MONTSERRAT & ANIMASI TOAST        */
/* ************************************************* */

.profile-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem 1rem;
  background-color: #166534;
  font-family: 'Montserrat', sans-serif;
}

.profile-container {
  max-width: 500px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.6s ease-in-out;
  position: relative;
}

@keyframes toast-fade-in {
  from { opacity: 0; transform: translate(-50%, -20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  background-color: #4caf50;
  color: #fff;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 999;
  font-weight: 600;
  font-family: 'Montserrat', sans-serif;
  animation: toast-fade-in 0.3s forwards;
}

.toast.error {
  background-color: #c0392b;
}

.toast .close-btn {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  margin-left: 10px;
}

.title {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.6rem;
  font-weight: 700;
  color: #166534;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

input[type="text"],
input[type="email"] {
  padding: 0.8rem 1rem;
  border: 2px solid #d1d5db;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-family: 'Montserrat', sans-serif;
}

input:focus {
  border-color: #166534;
  outline: none;
  box-shadow: 0 0 6px rgba(22, 101, 52, 0.3);
}

.input-disabled {
  background-color: #e5e7eb;
  color: #6b7280;
  cursor: not-allowed;
  border: 2px solid #cbd5e1;
}

.form-actions {
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-save,
.btn-cancel {
  color: #fff;
  border: none;
  padding: 0.9rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  font-family: 'Montserrat', sans-serif;
}

.btn-save {
  background: #4caf50;
}

.btn-save:hover {
  background: #14532d;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(22, 101, 52, 0.3);
}

.btn-cancel {
  background: #c0392b;
}

.btn-cancel:hover {
  background: #922b21;
  transform: translateY(-2px);
}

.center-avatar {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}

.avatar-display {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  border: 3px solid #166534;
  cursor: pointer;
  transition: 0.2s;
  object-fit: cover;
}

.avatar-display:hover {
  transform: scale(1.07);
}

.avatar-hint {
  font-size: 0.9rem;
  color: #555;
  margin-top: 5px;
}

.avatar-popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
}

.avatar-popup {
  width: 90%;
  max-width: 350px;
  background: white;
  padding: 1.5rem;
  border-radius: 14px;
  animation: fadeIn 0.3s ease;
  text-align: center;
}

.avatar-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin: 1rem 0;
}

.avatar-img {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  border: 2px solid #166534;
  cursor: pointer;
  transition: 0.2s;
  object-fit: cover;
}

.avatar-img:hover {
  transform: scale(1.1);
}

.avatar-img.selected {
  border: 3px solid #4caf50;
  transform: scale(1.15);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 600px) {
  .profile-container {
    padding: 1.5rem;
  }

  .title {
    font-size: 1.3rem;
  }

  .avatar-display {
    width: 110px;
    height: 110px;
  }

  .avatar-img {
    width: 60px;
    height: 60px;
  }

  .avatar-popup {
    padding: 1.2rem;
  }

  .form-actions {
    flex-direction: column;
    gap: 0.75rem;
  }

  .btn-save,
  .btn-cancel {
    width: 100%;
  }
}
</style>
