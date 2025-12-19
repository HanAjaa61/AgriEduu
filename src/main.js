import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { auth } from '@/firebase' 
import { onAuthStateChanged } from 'firebase/auth' 
import { useProfileStore } from '@/stores/profile' 
import '@fortawesome/fontawesome-free/css/all.css'


const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

let isAppMounted = false;

onAuthStateChanged(auth, (user) => {
  const profileStore = useProfileStore();
  
  if (user) {
    const photoURL = user.photoURL || "/src/assets/default.png";
    
    profileStore.setProfilePic(photoURL);

  } else {
    profileStore.setProfilePic("/src/assets/default.png");
  }
  if (!isAppMounted) {
     app.mount('#app');
     isAppMounted = true;
  }
});
