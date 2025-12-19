<template>
  <div class="bab-container">
    <h1 class="page-title">
      <i class="fas fa-leaf page-icon"></i> Edukasi Pertanian
    </h1>
    <p class="subtitle">Jelajahi setiap bab untuk memperdalam pengetahuan pertanian Anda.</p>
    <div class="chapters-grid">
      <router-link
  v-for="(chapter, index) in chapters"
  :key="chapter.id"
  :to="{ name: 'Modul', params: { id: chapter.id } }"
  class="chapter-card"
  :style="{ 'animation-delay': `${index * 0.1}s` }"
>
        <div class="card-icon-wrapper">
          <span class="chapter-icon">{{ chapter.icon }}</span>
        </div>
        <h2 class="chapter-title">{{ chapter.title }}</h2>
        <p class="chapter-description">{{ chapter.description }}</p>
        <div class="read-more-btn">Mulai Belajar</div>
      </router-link>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Bab',
  setup() {
    const chapters = ref([
      { 
        id: 'dasar', 
        title: 'Dasar Pertanian', 
        icon: '🌱', 
        description: 'Pelajari prinsip dan pondasi ilmu pertanian modern.' 
      },
      { 
        id: 'tanah', 
        title: 'Tanah & Media Tanam', 
        icon: '🪴', 
        description: 'Mengenal karakteristik dan cara mengelola media tanam yang subur.' 
      },
      { 
        id: 'air', 
        title: 'Pengairan & Pemupukan', 
        icon: '💧', 
        description: 'Pahami teknik irigasi dan cara memberikan nutrisi yang tepat bagi tanaman.' 
      },
      { 
        id: 'budidaya', 
        title: 'Budidaya Tanaman', 
        icon: '🌿', 
        description: 'Panduan lengkap dari pemilihan bibit hingga panen.' 
      },
      { 
        id: 'hama', 
        title: 'Hama & Penyakit', 
        icon: '🐛', 
        description: 'Identifikasi, cegah, dan kendalikan hama serta penyakit tanaman.' 
      },
      { 
        id: 'teknologi', 
        title: 'Teknologi Pertanian', 
        icon: '🚜', 
        description: 'Manfaatkan inovasi dan teknologi untuk meningkatkan hasil panen.' 
      },
      { 
        id: 'berkelanjutan', 
        title: 'Pertanian Berkelanjutan', 
        icon: '♻️', 
        description: 'Terapkan metode ramah lingkungan untuk pertanian masa depan.' 
      },
      { 
        id: 'ekonomi', 
        title: 'Ekonomi & Kewirausahaan', 
        icon: '💰', 
        description: 'Kelola bisnis pertanian Anda dari produksi hingga pemasaran.' 
      },
    ]);
    return { chapters };
  },
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap'); 

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

@keyframes pulseIcon {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* --- General Styling --- */
.bab-container {
  padding: 60px 20px;
  text-align: center;
  font-family: 'Poppins', sans-serif;
  max-width: 1280px; /* Lebih lebar sedikit */
  margin: auto;
  background-color: #f8fcf9; /* Latar belakang yang lebih terang */
  color: #333;
}

.page-title {
  color: #1a5e2f; /* Hijau yang lebih dalam */
  font-family: 'Montserrat', sans-serif;
  font-size: 3em; /* Lebih besar */
  font-weight: 700;
  margin-bottom: 0.5em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.page-icon {
    color: #4CAF50; /* Warna ikon */
    font-size: 1.1em;
}

.subtitle {
  color: #6c757d; /* Abu-abu yang lebih lembut */
  font-size: 1.3em;
  margin-bottom: 4em;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Ukuran kartu sedikit lebih besar */
  gap: 30px; /* Jarak antar kartu lebih besar */
  margin-top: 20px;
}

/* --- Chapter Card Styling --- */
.chapter-card {
  background-color: #ffffff;
  border: none;
  border-radius: 16px; /* Sudut lebih membulat */
  padding: 30px; /* Padding lebih banyak */
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: #333;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08); /* Bayangan yang lebih menonjol */
  transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  animation: fadeInSlideUp 0.8s ease-out forwards; /* Animasi saat muncul */
  opacity: 0; /* Mulai dengan opacity 0 agar animasi terlihat */
  transform: translateY(20px); /* Mulai sedikit ke bawah */
}

.chapter-card:hover {
  transform: translateY(-8px); /* Efek melayang lebih tinggi */
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.15); /* Bayangan lebih kuat saat hover */
  background-color: #f0fdf4; /* Warna latar belakang sedikit berubah */
}

.card-icon-wrapper {
  background-color: #e8f5e9; /* Latar belakang ikon */
  border-radius: 50%; /* Bentuk lingkaran */
  width: 90px;
  height: 90px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: background-color 0.3s ease;
}

.chapter-card:hover .card-icon-wrapper {
  background-color: #dcedc8; /* Warna latar belakang ikon saat hover */
  animation: pulseIcon 1s ease-in-out infinite; /* Animasi denyutan */
}


.chapter-icon {
  font-size: 4.5em; /* Ukuran ikon lebih besar */
  line-height: 1; /* Pastikan ikon di tengah */
}

.chapter-title {
  font-family: 'Montserrat', sans-serif;
  font-size: 1.5em; /* Ukuran judul lebih besar */
  font-weight: 600;
  color: #2e7d32; /* Hijau yang sama dengan judul utama */
  margin-bottom: 10px;
  text-align: center;
}

.chapter-description {
    font-size: 1em;
    color: #777;
    margin-bottom: 20px;
    line-height: 1.5;
}

.read-more-btn {
    background-color: #4CAF50;
    color: white;
    padding: 12px 25px;
    border-radius: 8px;
    font-size: 0.95em;
    font-weight: 600;
    transition: background-color 0.3s ease, transform 0.2s ease;
    cursor: pointer;
    margin-top: auto;
}

.chapter-card:hover .read-more-btn {
    background-color: #388E3C;
    transform: translateY(-2px);
}
/* --- Responsive Adjustments --- */
@media (max-width: 992px) {
  .page-title {
    font-size: 2.5em;
  }
  .subtitle {
    font-size: 1.1em;
    margin-bottom: 3em;
  }
  .chapters-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 25px;
  }
  .chapter-card {
    padding: 25px;
  }
  .chapter-icon {
    font-size: 4em;
  }
  .card-icon-wrapper {
    width: 80px;
    height: 80px;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 2em;
    gap: 10px;
  }
  .subtitle {
    font-size: 1em;
    margin-bottom: 2.5em;
  }
  .chapters-grid {
    grid-template-columns: 1fr; /* Satu kolom untuk mobile */
    gap: 20px;
  }
  .bab-container {
    padding: 40px 15px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.8em;
  }
  .subtitle {
    font-size: 0.9em;
    margin-bottom: 2em;
  }
  .chapter-icon {
    font-size: 3.5em;
  }
  .card-icon-wrapper {
    width: 70px;
    height: 70px;
  }
  .chapter-title {
    font-size: 1.3em;
  }
  .read-more-btn {
    padding: 10px 20px;
    font-size: 0.9em;
  }
}
</style>