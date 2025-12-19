<script setup>
import { RouterView } from 'vue-router';
import Navbar from '@/components/Navbar.vue';
import Footer from '@/components/Footer.vue';
import Bot from '@/components/Bot.vue';
</script>

<template>
  <div id="app-container">
    <Navbar />
    <main class="main-content">
      <RouterView />
    </main>
    <Footer />
    <Bot />
  </div>
</template>
<style>

#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1; 
}
</style>