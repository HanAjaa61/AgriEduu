<template>
  <div class="bot-wrapper">
    
    <div 
      @click="toggleBot" 
      :class="['agribot-icon-wrapper', { 'is-pulsing': !botOpen }]"
    >
      <div class="agribot-icon-inner">
        <img :src="AgriBotIcon" alt="AgriBot Icon" class="agribot-icon-img"/>
      </div>
    </div>

    <transition name="panel-switch" mode="out-in">
      
      <div 
        v-if="botOpen && !featureSelected" 
        key="feature-panel" 
        class="feature-panel"
      >
        <h3 class="feature-panel-title">AgriBot</h3>

        <ul class="feature-list">
          <li 
            v-for="f in features" 
            :key="f.id" 
            @click="selectFeature(f.id)" 
            class="feature-item"
          >
            <span class="feature-emoji">{{ f.emoji }}</span>
            {{ f.name }}
          </li>
        </ul>
      </div>

      <component 
        v-else-if="featureSelected && currentFeatureComponent"
        :is="currentFeatureComponent"
        @closeFeature="resetFeature"
        key="feature-component"
      />
      
    </transition>

  </div>
</template>

<script>
import AgriBotIcon from '@/assets/agribot.gif';

import Feature1 from './Feature1.vue';
export default {
  name: 'Bot',

  components: {
    Feature1
  },

  data() {
    return {
      AgriBotIcon,
      botOpen: false,
      featureSelected: null,

      features: [
        { id: 1, name: 'Prediksi Waktu Tanam', emoji: '📅', component: 'Feature1' }
      ]
    };
  },

  computed: {
    currentFeatureComponent() {
      const f = this.features.find(x => x.id === this.featureSelected);
      // Mengembalikan nama komponen (string) untuk props 'is'
      return f ? f.component : null; 
    }
  },

  methods: {
    toggleBot() {
      this.botOpen = !this.botOpen;
      if (!this.botOpen) this.featureSelected = null;
    },
    selectFeature(id) {
      this.featureSelected = id;
    },
    resetFeature() {
      this.featureSelected = null;
    }
  }
};
</script>

<style scoped>
/* semua CSS kamu tetap, tidak diubah */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

.bot-wrapper{position:relative;font-family:'Montserrat',sans-serif;}
.agribot-icon-wrapper{position:fixed;bottom:30px;right:30px;cursor:pointer;border-radius:50%;padding:6px;box-shadow:0 4px 12px rgba(0,0,0,0.2);background:white;z-index:500;transition:all 0.3s;}
.agribot-icon-inner{width:64px;height:64px;border-radius:50%;overflow:hidden;border:4px solid white;transition:transform 0.5s;}
.agribot-icon-inner:hover{transform:scale(1.1);}
.agribot-icon-img{width:100%;height:100%;object-fit:cover;display:block;}
@keyframes pulse-green{0%{box-shadow:0 0 0 0 rgba(16,185,129,0.7);}70%{box-shadow:0 0 0 16px rgba(16,185,129,0);}100%{box-shadow:0 0 0 0 rgba(16,185,129,0);} }
.is-pulsing{animation:pulse-green 2s infinite ease-out;}

.feature-panel{position:fixed;bottom:110px;right:30px;width:280px;background:white;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,0.25);padding:16px;z-index:600;border:1px solid #e0f2f1;}
.feature-panel-title{font-size:1.15rem;font-weight:700;color:#047857;margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid #a7f3d0;}
.feature-list{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:8px;}
.feature-item{padding:10px 12px;background:#f0fdf4;border-radius:8px;cursor:pointer;transition:0.2s;font-size:0.95rem;color:#374151;font-weight:500;display:flex;align-items:center;}
.feature-item:hover{background:#d1fae5;transform:translateY(-2px);box-shadow:0 2px 5px rgba(0,0,0,0.1);}
.feature-emoji{margin-right:8px;font-size:1.2rem;}

/* Peningkatan Transisi Panel */
.panel-switch-enter-active, 
.panel-switch-leave-active {
  transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1); /* Kurva yang lebih smooth */
}

.panel-switch-enter-from {
  opacity: 0;
  transform: translateY(15px); 
}

.panel-switch-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>