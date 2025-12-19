// src/stores/profile.js
import { defineStore } from "pinia";
import { ref } from "vue";

export const useProfileStore = defineStore("profile", () => {
  const profilePic = ref(null);

  const setProfilePic = (url) => {
    profilePic.value = url;
  };

  return { profilePic, setProfilePic };
});
