<template>
  <section class="testimonials-section" id="testimonials">
    <div class="container">
      <h2 class="section-heading">Apa Kata Mereka?</h2>
      <p class="section-subheading">Cerita sukses dari para pengguna di komunitas AgriEdu.</p>
      
      <div class="testimonials-grid">
        <div class="testimonial-card" ref="testimonial1">
          <div class="avatar-container">
            <img src="@/assets/petani2.jpg" alt="Foto Profil Bpk. Slamet" class="user-avatar" />
          </div>
          <p class="testimonial-text">
            "Sangat membantu! Saya yang tadinya hanya mengandalkan cara lama, sekarang bisa panen lebih banyak berkat tips-tips di AgriEdu."
          </p>
          <div class="user-info">
            <span class="user-name">Bpk. Slamet</span>
            <span class="user-role">Petani Padi, Jawa Tengah</span>
          </div>
        </div>
        
        <div class="testimonial-card" ref="testimonial2">
          <div class="avatar-container">
            <img src="@/assets/mahasiswi.png" alt="Foto Profil Aisyah" class="user-avatar" />
          </div>
          <p class="testimonial-text">
            "Sebagai mahasiswa pertanian, AgriEdu adalah sumber referensi digital yang lengkap. Materinya mudah dipahami dan sangat relevan dengan praktik di lapangan."
          </p>
          <div class="user-info">
            <span class="user-name">Aisyah</span>
            <span class="user-role">Mahasiswa Pertanian, Bogor</span>
          </div>
        </div>
        
        <div class="testimonial-card" ref="testimonial3">
          <div class="avatar-container">
            <img src="@/assets/petani5.jpeg" alt="Foto Profil Ibu Siti" class="user-avatar" />
          </div>
          <p class="testimonial-text">
            "Saya terkesan dengan modul pengelolaan hama terpadu. Ini membantu saya mengurangi penggunaan pestisida kimia secara signifikan dan membuat kebun saya lebih sehat."
          </p>
          <div class="user-info">
            <span class="user-name">Bpk. Darmawan</span>
            <span class="user-role">Petani Organik, Bandung</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';

const testimonial1 = ref(null);
const testimonial2 = ref(null);
const testimonial3 = ref(null);

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
    }
  });
}, {
  threshold: 0.3 // Memicu animasi saat 30% elemen terlihat
});

onMounted(() => {
  if (testimonial1.value) observer.observe(testimonial1.value);
  if (testimonial2.value) observer.observe(testimonial2.value);
  if (testimonial3.value) observer.observe(testimonial3.value);
});

onUnmounted(() => {
  if (testimonial1.value) observer.unobserve(testimonial1.value);
  if (testimonial2.value) observer.unobserve(testimonial2.value);
  if (testimonial3.value) observer.unobserve(testimonial3.value);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

/* --- */

/* Section Utama */
.testimonials-section {
  background-color: #e4f8ea; /* Latar belakang hijau muda */
  padding: 6rem 2rem;
  font-family: 'Poppins', sans-serif;
  color: #334155;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.section-heading {
  font-family: 'Montserrat', sans-serif;
  font-size: 2.5rem;
  font-weight: 700;
  color: #14532d;
  margin-bottom: 0.5rem;
}

.section-subheading {
  font-size: 1rem;
  color: #555;
  margin-bottom: 3rem;
}

/* --- */

/* Grid untuk Testimonial */
.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

/* --- */

/* Kartu Testimonial */
.testimonial-card {
  background-color: #ffffff;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

/* Animasi */
.testimonial-card.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.testimonial-card:nth-child(2) { transition-delay: 0.1s; }
.testimonial-card:nth-child(3) { transition-delay: 0.2s; }

/* --- */

/* Avatar dan Info Pengguna */
.avatar-container {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.testimonial-text {
  font-size: 1.05rem;
  line-height: 1.6;
  color: #555;
  font-style: italic;
  margin-bottom: 1rem;
}

.user-info {
  margin-top: auto; /* Mendorong info ke bawah */
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: #14532d;
}

.user-role {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 400;
}

/* --- */

/* Responsif */
@media (max-width: 768px) {
  .testimonials-grid {
    grid-template-columns: 1fr;
  }
}
</style>