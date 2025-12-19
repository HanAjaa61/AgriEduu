<template>
  <span class="animated-number" ref="numberRef">{{ displayedNumber.toLocaleString('id-ID') }}</span>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  endValue: {
    type: Number,
    required: true,
  },
  duration: {
    type: Number,
    default: 2000,
  },
});

const numberRef = ref(null);
const displayedNumber = ref(0);
let animationFrameId = null;
let observer = null;

const animateCount = () => {
  const start = 0;
  const end = props.endValue;
  const startTime = performance.now();

  const step = (currentTime) => {
    const elapsedTime = currentTime - startTime;
    const progress = Math.min(elapsedTime / props.duration, 1);
    const value = Math.floor(progress * (end - start) + start);
    
    displayedNumber.value = value;
    
    if (progress < 1) {
      animationFrameId = requestAnimationFrame(step);
    } else {
      displayedNumber.value = end;
    }
  };

  animationFrameId = requestAnimationFrame(step);
};

onMounted(() => {
  if (numberRef.value) {
    observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCount();
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.5,
    });
    
    observer.observe(numberRef.value);
  }
});

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  if (observer) {
    observer.disconnect();
  }
});
</script>

<style scoped>
.animated-number {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  color: #14532d;
  font-size: 2.2rem;
  line-height: 1;
}
</style>