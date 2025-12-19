<template>
  <nav class="navbar">
    <div class="navbar-container">
      <RouterLink to="/" class="navbar-logo">
        <img src="@/assets/agriedu_logo.png" alt="AgriEdu Logo" class="logo-img" />
        <span class="logo-text">AgriEdu</span>
      </RouterLink>

      <div class="right-section">
        <ul class="nav-links">
          <li><RouterLink to="/">Home</RouterLink></li>
          <Transition name="fade-slide">
            <template v-if="!isSpecialPage">
              <li>
                <a href="#about-us">About</a>
              </li>
            </template>
          </Transition>
          <li><RouterLink to="/education">Education</RouterLink></li>
        </ul>

        <div class="profile-container">
          <RouterLink to="/profile" class="profile-link">
            <img 
            :src="profileStore.profilePic || defaultPic" 
            @error="profileStore.setProfilePic(defaultPic)" 
            class="profile" 
            alt="Profile"/>
          </RouterLink>
        </div>

        <div :class="['hamburger', { 'is-active': isMobileMenuOpen }]" @click="toggleMobileMenu">
          <span class="bar"></span>
          <span class="bar"></span>
          <span class="bar"></span>
        </div>
      </div>
    </div>

    <ul :class="['mobile-menu', { 'is-open': isMobileMenuOpen }]">
      <li><RouterLink to="/" @click="closeMobileMenu">Home</RouterLink></li>
      <Transition name="fade-slide">
        <template v-if="!isSpecialPage">
          <li>
            <a href="#about-us" @click="closeMobileMenu">About</a>
          </li>
        </template>
      </Transition>
      <li><RouterLink to="/education" @click="closeMobileMenu">Education</RouterLink></li>
      <li><RouterLink to="/profile" @click="closeMobileMenu">Profile</RouterLink></li>
    </ul>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import defaultPic from "@/assets/default.png";
import { useProfileStore } from "@/stores/profile";
const profileStore = useProfileStore();
const isMobileMenuOpen = ref(false);
const route = useRoute();

const isSpecialPage = computed(() => {
  return route.path.includes('/education') || route.path.includes('/login') ||
    route.path.includes('/daftar') || route.path.includes('/modul-detail') || route.path.includes('/profile');
});

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

.navbar {
  background-color: #166534;
  padding: 0.7rem 1.1rem;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #fff;
}
.logo-img {
  height: 40px;
  width: 40px;
  margin-right: 0.75rem;
  border-radius: 5px;
}
.logo-text {
  font-size: 1.4rem;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
}

.right-section {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.nav-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 1.5rem;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
}

.nav-links a {
  color: #fff;
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
  position: relative;
  padding: 5px 0;
}
.nav-links a:hover {
  color: #d1fae5;
}
.nav-links a::after {
  content: '';
  position: absolute;
  bottom: 0px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: #d1fae5;
  transition: width 0.3s ease-in-out;
}
.nav-links a:hover::after {
  width: 100%;
}

.profile-container {
  display: flex;
  align-items: center;
  margin-left: 1rem;
}

.profile-link {
    display: block;
}

.profile {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 50%; 
  border: 2px solid #d1fae5;
  transition: transform 0.2s ease-in-out, border-color 0.2s ease;
}

.profile:hover {
    transform: scale(1.05);
    border-color: #a7f3d0;
}


.hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 28px;
  height: 20px;
  cursor: pointer;
  z-index: 1001;
  transition: transform 0.3s ease;
}
.bar {
  display: block;
  width: 100%;
  height: 3px;
  background-color: #fff;
  border-radius: 2px;
  transition: all 0.3s ease-in-out;
}

.hamburger.is-active .bar:nth-child(2) {
  opacity: 0;
}
.hamburger.is-active .bar:nth-child(1) {
  transform: translateY(8px) rotate(45deg);
}
.hamburger.is-active .bar:nth-child(3) {
  transform: translateY(-8px) rotate(-45deg);
}

.mobile-menu {
  list-style: none;
  margin: 0;
  padding: 1rem 0;
  background-color: #14532d;
  display: flex;
  flex-direction: column;
  text-align: center;
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  height: auto;
  transform: translateX(-100%);
  opacity: 0;
  transition: transform 0.4s ease-out, opacity 0.4s ease-out;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
  box-shadow: 0 5px 10px rgba(0,0,0,0.2);
  padding-bottom: 2rem;
}

.mobile-menu.is-open {
  transform: translateX(0);
  opacity: 1;
}

.mobile-menu li {
    margin: 0.5rem 0;
}

.mobile-menu a {
  color: #fff;
  text-decoration: none;
  font-size: 1rem;
  display: block;
  padding: 0.7rem 0;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.mobile-menu a:hover {
  background-color: #1a6d40;
  color: #d1fae5;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease-out;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
  .hamburger {
    display: flex;
  }
  .profile-container {
    display: none; 
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .navbar-container {
        padding: 0.7rem 1.5rem;
    }
    .nav-links {
        gap: 1rem;
    }
    .profile-container {
        margin-left: 0.8rem;
    }
}
</style>