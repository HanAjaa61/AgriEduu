<template>
  <div class="register-container">
    <div class="auth-card fade-in">

      <div class="card-content">
        
        <!-- LEFT SIDE -->
        <div class="card-left">
          <img src="@/assets/agriedu_logo.png" alt="AgriEdu Logo" class="logo" />
          <h1 class="title">Selamat Datang</h1>
          <p class="subtitle">Daftar sekarang untuk memulai perjalanan pertanian Anda.</p>

          <div class="card-footer">
            <p>
              Sudah punya akun?
              <router-link to="/login" class="login-link">Masuk di sini</router-link>
            </p>
          </div>
        </div>

        <!-- RIGHT SIDE — FORM -->
        <form @submit.prevent="handleRegister" class="auth-form">

          <!-- PILIH AVATAR -->
          <div class="form-group center-avatar">
            <img
              :src="selectedAvatar"
              class="avatar-display"
              @click="showAvatarPopup = true"
              @error="handleImageError"
            />
            <p class="avatar-hint">Klik gambar untuk pilih avatar</p>
          </div>

          <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" v-model="username" placeholder="Masukkan username" required />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="email" placeholder="Masukkan email" required />
          </div>

          <div class="form-group password-wrapper">
            <label for="password">Password</label>
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              placeholder="••••••••"
              required
            />
            <span class="toggle-password" @click="showPassword = !showPassword"></span>
          </div>

          <div class="form-group password-wrapper">
            <label for="confirm-password">Konfirmasi Password</label>
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              id="confirm-password"
              v-model="confirmPassword"
              placeholder="••••••••"
              required
            />
            <span class="toggle-password" @click="showConfirmPassword = !showConfirmPassword"></span>
            <transition name="fade">
              <p v-if="passwordMismatch" class="error-message">Password tidak cocok.</p>
            </transition>
          </div>

          <button type="submit" class="btn btn-primary register-btn">Daftar</button>
        </form>

      </div>
    </div>

    <!-- POPUP AVATAR -->
    <div
      v-if="showAvatarPopup"
      class="avatar-popup-overlay"
      @click.self="showAvatarPopup = false"
    >
      <div class="avatar-popup">
        <h3>Pilih Avatar</h3>
        <div class="avatar-options">
          <img
            v-for="(avatar, index) in presetAvatars"
            :key="index"
            :src="avatar"
            :class="{ selected: avatar === selectedAvatar }"
            @click="chooseAvatar(avatar)"
            class="avatar-img"
          />
        </div>
        <button class="btn-cancel" @click="showAvatarPopup = false">Tutup</button>
      </div>
    </div>

    <!-- NOTIFICATION TOAST -->
    <div v-if="showToast" class="toast" :class="toastType">
      <span>{{ toastMessage }}</span>
      <button class="close-btn" @click="showToast = false">&times;</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { auth } from '@/firebase';
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';

// ✅ import semua avatar agar aman deploy Vercel
import defaultAvatar from '@/assets/default.png';
import profile1 from '@/assets/profile1.png';
import profile2 from '@/assets/profil2.png';
import profile3 from '@/assets/profile3.png';
import profile4 from '@/assets/profile4.png';

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

const showPassword = ref(false);
const showConfirmPassword = ref(false);

const showToast = ref(false);
const toastMessage = ref('');
const toastType = ref('success');

const showAvatarPopup = ref(false);

const presetAvatars = [defaultAvatar, profile1, profile2, profile3, profile4];
const selectedAvatar = ref(defaultAvatar);

const showNotification = (message, type = 'success') => {
  toastMessage.value = message;
  toastType.value = type;
  showToast.value = true;
  setTimeout(() => (showToast.value = false), 3000);
};

const handleImageError = () => {
  selectedAvatar.value = defaultAvatar;
};

const chooseAvatar = (avatar) => {
  selectedAvatar.value = avatar;
  showAvatarPopup.value = false;
};

const isPasswordStrong = computed(() => {
  const pwd = password.value;
  const minLength = pwd.length >= 8;
  const hasUpper = /[A-Z]/.test(pwd);
  const hasLower = /[a-z]/.test(pwd);
  const hasNumber = /[0-9]/.test(pwd);
  const hasSymbol = /[^A-Za-z0-9]/.test(pwd);
  return minLength && hasUpper && hasLower && hasNumber && hasSymbol;
});

const passwordMismatch = computed(() => {
  return confirmPassword.value && password.value !== confirmPassword.value;
});

const handleRegister = async () => {
  if (!isPasswordStrong.value) {
    showNotification('❌ Password terlalu lemah!', 'error');
    return;
  }
  if (passwordMismatch.value) {
    showNotification('Konfirmasi password tidak cocok!', 'error');
    return;
  }

  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email.value, password.value);
    const user = userCredential.user;

    await updateProfile(user, {
      displayName: username.value,
      photoURL: selectedAvatar.value
    });

    showNotification('✅ Registrasi berhasil! Anda dapat login sekarang.', 'success');

    setTimeout(() => {
      window.location.href = '/login';
    }, 1500);
  } catch (error) {
    console.error('Firebase Error:', error);
    if (error.code === 'auth/email-already-in-use') showNotification('❌ Email sudah digunakan!', 'error');
    else if (error.code === 'auth/invalid-email') showNotification('❌ Format email tidak valid!', 'error');
    else if (error.code === 'auth/weak-password') showNotification('❌ Password terlalu lemah!', 'error');
    else showNotification('❌ Terjadi kesalahan, coba lagi.', 'error');
  }
};

// Optional: set default avatar saat mount
onMounted(() => {
  selectedAvatar.value = defaultAvatar;
});
</script>

<style scoped>

.password-wrapper {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 65%;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 1.1rem;
  user-select: none;
}

.register-container {
  background-color: #166534;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  font-family: "Segoe UI", Tahoma, sans-serif;
}

/* CARD */
.auth-card {
  background: #fff;
  padding: 3rem 3.5rem;
  border-radius: 20px;
  box-shadow: 0 15px 30px rgba(150, 75, 0, 0.1);
  max-width: 1100px;
  width: 100%;
}

/* ======================================
   DESKTOP LAYOUT (UTAMA)
   ====================================== */
.card-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 4rem;
}

/* LEFT SIDE */
.card-left {
  width: 42%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding-top: 90px;
}

.logo {
  width: 90px;
  margin-bottom: 1rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #38761d;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #555;
  font-size: 1.05rem;
  line-height: 1.5;
  margin-bottom: 1.2rem;
}

.card-footer {
  margin-top: 1rem;
  font-size: 1rem;
  color: #444;
}

.login-link {
  color: #38761d;
  font-weight: bold;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}

/* RIGHT SIDE: FORM */
.auth-form {
  width: 58%;
  display: flex;
  flex-direction: column;
}

/* FORM GROUP: VERTIKAL */
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.3rem;
}

.form-group label {
  font-size: 1rem;
  font-weight: 600;
  color: #222;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  border: 2px solid #ddd;
  font-size: 1rem;
  transition: 0.2s;
}

.form-group input:focus {
  border-color: #38761d;
  box-shadow: 0 0 0 4px rgba(56,118,29,0.15);
  outline: none;
}

/* BUTTON */
.register-btn {
  margin-top: 0.5rem;
  width: 20%;
  height: 45px;
  padding: 1rem;
  background: #4caf50;
  border: none;
  color: #fff;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.25s;
  text-align: center;
}

.register-btn:hover {
  background: #2f621b;
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(56, 118, 29, 0.3);
}

/* Fade in untuk card */
@keyframes fadeIn {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 0.8s ease-out forwards; }

.toast {
  position: fixed;
  top: 100px;
  left: 50%;             /* tengah horizontal */
  transform: translate(-50%, -20px); /* center + slide dari atas */
  padding: 1rem 1.5rem;
  border-radius: 12px;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  opacity: 0;
  animation: fadeInToast 0.5s forwards, fadeOutToast 0.5s 2.5s forwards;
  z-index: 999;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 400px;
  width: 90%;
}

/* Variasi warna */
.toast.success { background-color: #38761d; }
.toast.error { background-color: #c0392b; }

/* Tombol close */
.toast .close-btn {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  margin-left: 0.8rem;
}

@media (max-width: 700px) { 
  .auth-card { padding: 2rem 1.5rem; } /* Force vertical layout */ 
  .card-content { display: flex; flex-direction: column !important; align-items: center; text-align: center; gap: 2rem; } 
  .card-left { width: 100%; padding-top: 0; } 
  .auth-form { width: 100%; } 
  .title { font-size: 1.6rem; } 
  .subtitle { font-size: 1rem; } 
  .form-group label { text-align: left; } 
  .register-btn { margin-top: 1rem; width: 40%; margin-left: 100px; } }

/* Animasi fade in / out */
@keyframes fadeInToast {
  0% { opacity: 0; transform: translate(-50%, -20px); }
  100% { opacity: 1; transform: translate(-50%, 0); }
}
@keyframes fadeOutToast {
  0% { opacity: 1; transform: translate(-50%, 0); }
  100% { opacity: 0; transform: translate(-50%, -20px); }
}

/* Mobile tetap responsif */
@media (max-width: 700px) {
  .toast { width: 90%; left: 50%; transform: translate(-50%, -20px); }
}
</style>