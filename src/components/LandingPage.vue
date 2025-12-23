<template>
  <div class="landing-page " id="home">
    <div class="content-section">
      <div class="text-content">
        <h3 class="about-heading">ABOUT OUR PLATFORM</h3>
        <h1 class="main-heading">THE PLACE WHERE MODERN FARMER IS BORN</h1>
        <p class="description">
          AgriEdu adalah platform edukasi dan komunitas yang didedikasikan untuk bidang agrikultur. 
          Kami menyediakan sumber daya pendidikan yang lengkap 
          di mana para petani, pelajar, dan siapa pun yang tertarik dapat belajar dan berbagi pengetahuan untuk memajukan pertanian modern.
        </p>
        <div class="button-container" v-if="!isLoggedIn">
          <router-link to="/login" class="btn btn-secondary">Login</router-link>
        </div>
        <div class="dots-container top-dots">
          <span></span><span></span><span></span><span></span>
        </div>
        <div class="dots-container bottom-dots">
          <span></span><span></span><span></span><span></span>
        </div>
      </div>
    </div>
    <div class="image-section">
      <img
        src="@/assets/petani3.jpg"
        alt="Farmer with vegetables"
        class="main-image"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { auth } from "@/firebase";

const isLoggedIn = ref(false);

onMounted(() => {
  // Cek status login saat component dimount
  auth.onAuthStateChanged((user) => {
    isLoggedIn.value = !!user;
  });
});
</script>

<style scoped>
/* Main container for the landing page */
.landing-page {
  display: flex;
  min-height: calc(100vh - 90px); /* Adjust height to fit below the navbar */
  background-color: #e5f6d5; /* Light green background, akan tersembunyi jika kedua sisi full */
  font-family: 'Arial', sans-serif;
}

/* Content Section (left side) */
.content-section {
  position: relative;
  background-color: #166534; /* Dark green background */
  color: #fff;
  padding: 4rem;
  width: 70vw; /* Menggunakan 50% dari lebar viewport */
  min-height: calc(100vh); /* Mengisi tinggi yang tersisa */
  display: flex;
  flex-direction: column;
  justify-content: center; /* Menengahkan konten secara vertikal */
  align-items: flex-start; /* Menengahkan teks secara horizontal ke kiri */
  box-sizing: border-box; /* Penting agar padding tidak menambah lebar */
}

.text-content {
  max-width: 500px; /* Batasi lebar teks agar tidak terlalu panjang */
  margin: 0 auto; /* Tengah teks dalam content-section */
  text-align: left; /* Sesuaikan jika ingin teks tetap rata kiri */
}

.about-heading {
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 2px;
  margin-bottom: 0.5rem;
  color: #d1fae5;
  /* Animasi */
  animation: fadeInSlideUp 0.8s ease-out 0.2s forwards;
  opacity: 0; 
}

.main-heading {
  font-size: 2.5rem;
  font-weight: bold;
  line-height: 1.2;
  margin-bottom: 1rem;
  color: #fff;
  /* Animasi */
  animation: fadeInSlideUp 0.8s ease-out 0.4s forwards;
  opacity: 0;
}

.description {
  font-size: 1rem;
  line-height: 1.6;
  color: #d1fae5;
  margin-bottom: 2rem;
  /* Animasi */
  animation: fadeInSlideUp 0.8s ease-out 0.6s forwards;
  opacity: 0;
}

.button-container {
  display: flex;
  gap: 1.5rem;
  animation: fadeInSlideUp 0.8s ease-out 0.8s forwards;
  opacity: 0;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
  text-decoration: none;
}

.btn-primary {
  background-color: #d1fae5;
  color: #166534;
}

.btn-primary:hover {
  background-color: #fff;
}

.btn-secondary {
  background-color: transparent;
  color: #fff;
  border: 2px solid #fff;
}

.btn-secondary:hover {
  background-color: #fff;
  color: #166534;
}

.dots-container {
  position: absolute;
  display: flex;
  gap: 0.5rem;
}

.dots-container.top-dots {
  top: 1rem;
  right: 1rem;
}

.dots-container.bottom-dots {
  bottom: 1rem;
  left: 1rem;
}

.dots-container span {
  width: 8px;
  height: 8px;
  background-color: #d1fae5;
  border-radius: 50%;
  /* Animasi denyut */
  animation: dotPulse 1.5s infinite ease-in-out alternate;
}

/* Memberikan delay berbeda untuk setiap titik */
.dots-container.top-dots span:nth-child(1) { animation-delay: 0s; }
.dots-container.top-dots span:nth-child(2) { animation-delay: 0.2s; }
.dots-container.top-dots span:nth-child(3) { animation-delay: 0.4s; }
.dots-container.top-dots span:nth-child(4) { animation-delay: 0.6s; }

.dots-container.bottom-dots span:nth-child(1) { animation-delay: 0.8s; }
.dots-container.bottom-dots span:nth-child(2) { animation-delay: 1s; }
.dots-container.bottom-dots span:nth-child(3) { animation-delay: 1.2s; }
.dots-container.bottom-dots span:nth-child(4) { animation-delay: 1.4s; }


.image-section {
  width: 50vw; /* Menggunakan 50% dari lebar viewport */
  min-height: calc(100vh - 80px); /* Mengisi tinggi yang tersisa */
  overflow: hidden;
}

.main-image {
  width: 100%;
  height: 100%; 
  object-fit: cover; 
  display: block;
  object-position: 85% center;
  /* Animasi */
  animation: fadeIn 1s ease-out forwards, imageZoomIn 1s ease-out forwards;
  opacity: 0;
}

/* Keyframes untuk animasi */
@keyframes fadeInSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes imageZoomIn {
  from {
    transform: scale(1.05); /* Sedikit zoom out di awal */
  }
  to {
    transform: scale(1); /* Kembali ke ukuran normal */
  }
}

@keyframes dotPulse {
  0% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
}


/* Responsive adjustments */
@media (max-width: 992px) {
  .landing-page {
    flex-direction: column; /* Kembali ke tata letak kolom */
    min-height: auto; /* Biarkan tinggi menyesuaikan konten */
  }
  .content-section,
  .image-section {
    width: 100vw; /* Setiap bagian mengambil 100% lebar viewport */
    min-height: auto; /* Tinggi menyesuaikan konten */
    box-sizing: border-box; /* Pastikan padding tidak menambah lebar */
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); 
  }
  .content-section .text-content {
      margin: 0; /* Hapus margin auto pada mobile */
      max-width: none; /* Izinkan teks mengambil lebar penuh */
      text-align: center; /* Tengahkan teks di mobile jika diinginkan */
  }
  .button-container {
      justify-content: center; /* Tengahkan tombol di mobile */
  }
}
</style>