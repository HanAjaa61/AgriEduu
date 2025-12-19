<template>
  <div v-if="showNotif" class="notif" :class="notifType">
    <span>{{ notifMessage }}</span>
    <button class="close-btn" @click="showNotif = false">×</button>
  </div>

  <div class="login-container">
    <div class="login-card">
      <img src="@/assets/agriedu_logo.png" alt="Logo" class="logo" />

      <h2>Login</h2>

      <form @submit.prevent="handleLogin" autocomplete="off">
        <input
          type="text"
          v-model="email"
          placeholder="Email"
          required
          autocomplete="new-email"
        />

        <div class="password-wrapper">
          <input
            :type="passwordInputType"
            v-model="password"
            placeholder="Password"
            required
            autocomplete="new-password"
          />
          <span class="toggle-password" @click="togglePasswordVisibility">
            <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
          </span>
        </div>

        <button type="submit" class="btn-login">Login</button>
      </form>

      <div class="separator">
        <span class="line"></span>
        <span>atau</span>
        <span class="line"></span>
      </div>

      <button type="button" class="btn-google" @click="handleGoogleLogin">
        <img
          src="https://img.icons8.com/color/16/000000/google-logo.png"
          alt="Google Logo"
        />
        Login dengan Google
      </button>

      <div class="register">
        Belum buat akun? <a href="/daftar">Daftar</a>
      </div>
    </div>
  </div>
</template>

<script>
import { auth } from "@/firebase";
import {
  signInWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";
import { useProfileStore } from "@/stores/profile";

export default {
  name: "Login",

  setup() {
    const profileStore = useProfileStore();
    return { profileStore };
  },

  data() {
    return {
      email: "",
      password: "",
      showPassword: false,
      passwordInputType: "text",
      showNotif: false,
      notifMessage: "",
      notifType: "",
    };
  },

  mounted() {
    setTimeout(() => {
      this.passwordInputType = "password";
    }, 100);
    this.loadFontAwesome();
  },

  methods: {
    loadFontAwesome() {
      if (!document.querySelector('link[href*="font-awesome"]')) {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href =
          "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css";
        document.head.appendChild(link);
      }
    },

    showNotification(message, type) {
      this.notifMessage = message;
      this.notifType = type;
      this.showNotif = true;
      setTimeout(() => {
        this.showNotif = false;
      }, 3000);
    },

    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
      this.passwordInputType = this.showPassword ? "text" : "password";
    },

    async handleLogin() {
      if (!this.email || !this.password) {
        this.showNotification("Email dan password wajib diisi!", "error");
        return;
      }

      try {
        const userCredential = await signInWithEmailAndPassword(
          auth,
          this.email,
          this.password
        );

        const user = userCredential.user;

        this.showNotification(
          "✅ Login berhasil! Selamat datang, " +
            (user.displayName || "User"),
          "success"
        );

        setTimeout(() => {
          this.$router.push({ name: "HomePage" });
        }, 800);
      } catch (error) {
        if (error.code === "auth/invalid-email") {
          this.showNotification("Format email tidak valid!", "error");
        } else if (error.code === "auth/user-not-found") {
          this.showNotification("Email tidak ditemukan!", "error");
        } else if (error.code === "auth/wrong-password") {
          this.showNotification("Password salah!", "error");
        } else {
          this.showNotification(
            "❌ Terjadi kesalahan. Silakan coba lagi.",
            "error"
          );
        }
      }
    },

    async handleGoogleLogin() {
      const provider = new GoogleAuthProvider();

      provider.setCustomParameters({
        prompt: "select_account",
      });

      try {
        const result = await signInWithPopup(auth, provider);
        if (!result || !result.user) return;

        const user = result.user;

        this.showNotification(
          "✅ Login berhasil dengan Google! Selamat datang, " +
            (user.displayName || "User"),
          "success"
        );

        setTimeout(() => {
          this.$router.push({ name: "HomePage" });
        }, 800);
      } catch (error) {
        if (
          error.code === "auth/popup-closed-by-user" ||
          error.code === "auth/cancelled-popup-request"
        ) {
          return;
        }

        this.showNotification(
          "❌ Gagal Login dengan Google. Coba lagi.",
          "error"
        );
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #166534; /* Warna hijau gelap untuk background */
  font-family: 'Montserrat', sans-serif;
}

.login-card {
  background: #fff;
  padding: 2rem;
  border-radius: 16px;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  text-align: center;
  animation: fadeIn 0.6s ease-in-out;
}

.logo {
  width: 70px;
  margin-bottom: 1rem;
}

h2 {
  margin-bottom: 1.5rem;
  color: #333;
  font-weight: 700;
}

form input {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  outline: none;
  transition: 0.3s;
  font-family: 'Montserrat', sans-serif;
  font-size: 1rem;
}

form input:focus {
  border-color: #4caf50;
  box-shadow: 0 0 6px rgba(76, 175, 80, 0.5);
}

.password-wrapper {
  position: relative;
  margin-bottom: 1rem; /* Tambahkan margin di wrapper */
}

.password-wrapper input {
  margin-bottom: 0; /* Hapus margin di input dalam wrapper */
}

.toggle-password {
  position: absolute;
  right: 12px;
  /* Sesuaikan agar lebih di tengah vertikal */
  top: 50%;
  transform: translateY(-50%); 
  cursor: pointer;
  font-size: 1.1rem;
  user-select: none;
  color: #777;
  transition: color 0.2s;
}

.toggle-password:hover {
    color: #333;
}

.btn-login {
  width: 100%;
  padding: 0.8rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.3s;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  margin-top: 0.5rem; /* Tambahkan sedikit ruang */
}

.btn-login:hover {
  background: #43a047;
}

/* --- Pemisah "atau" --- */
.separator {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0;
  color: #999;
  font-size: 0.9rem;
}

.separator .line {
  flex-grow: 1;
  height: 1px;
  background-color: #eee;
  margin: 0 10px;
}

/* --- Tombol Login Google --- */
.btn-google {
  width: 100%;
  padding: 0.8rem;
  background: #ffffff; 
  color: #555;
  border: 1px solid #ccc;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: 0.3s;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-google:hover {
  background: #f4f4f4;
  border-color: #aaa;
}

.btn-google img {
    width: 20px;
    height: 20px;
}


.forgot-password {
  text-align: right;
  margin: 0.5rem 0 1rem 0;
}

.forgot-password a {
  font-size: 0.9rem;
  color: #4caf50;
  text-decoration: none;
}

.forgot-password a:hover {
  text-decoration: underline;
}

.register {
  margin-top: 3rem;
  font-size: 0.95rem;
  color: #555;
}

.register a {
  color: #4caf50;
  font-weight: bold;
  text-decoration: none;
}

.register a:hover {
  text-decoration: underline;
}

/* --- Animasi Notifikasi (Fade In Down) --- */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

.notif {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 20px;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  min-width: 260px;
  text-align: center;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-family: 'Montserrat', sans-serif;
  animation: fadeInDown 0.4s ease forwards;
}

/* Warna ketika berhasil */
.success {
  background-color: #16a34a; 
}

/* Warna ketika gagal */
.error {
  background-color: #dc2626; 
}

/* Tombol close */
.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  margin-left: 10px;
  line-height: 1;
}

input[type="password"]::-ms-reveal,
input[type="password"]::-ms-clear {
  display: none;
}

input[type="password"]::-webkit-credentials-auto-fill-button,
input[type="password"]::-webkit-contacts-auto-fill-button {
  display: none !important;
}

/* Animasi login card saat page load */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>