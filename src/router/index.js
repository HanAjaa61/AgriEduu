import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue';
import Bab from '@/components/Bab.vue';
import Modul from '@/components/Modul.vue'; 
import ModulDetail from '@/components/ModulDetail.vue';
import Login from '@/components/Login.vue';
import Daftar from '@/components/Daftar.vue';
import Profile from '@/components/Profile.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'HomePage', 
      component: HomePage,
    },

    {
      path: '/education', 
      name: 'Education', 
      component: Bab, 
    },

    {
      path: '/education/modul/:id',
      name: 'Modul',
      component: Modul,
      props: true, 
    },

    {
      // Rute baru untuk detail spesifik dari sebuah modul
      path: '/modul-detail/:id',
      name: 'ModulDetail',
      component: ModulDetail,
      props: true,
    },

    {
      path: '/login', 
      name: 'Login', 
      component: Login, 
    },

    {
      path: '/daftar', 
      name: 'Daftar', 
      component: Daftar, 
    },

    {
      path: '/profile', 
      name: 'Profil', 
      component: Profile, 
    },

  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.name === 'Education') {
      return { top: 0, behavior: 'smooth' };
    }
    if (savedPosition) {
      return savedPosition;
    } 
    else {
      return { top: 0, behavior: 'smooth' };
    }
  }
})

export default router