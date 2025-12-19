import { initializeApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyBEg1yslk8mDvv2vaLpl6Yfx0tIpS-DRiY",
  authDomain: "agriedu-89f48.firebaseapp.com",
  projectId: "agriedu-89f48",
  storageBucket: "agriedu-89f48.appspot.com",
  messagingSenderId: "708477004136",
  appId: "708477004136:web:aebf93c518c193bf918edd",
  measurementId: "G-6HJBM17K20",
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApps()[0];

const auth = getAuth(app);
const storage = getStorage(app);
const db = getFirestore(app);

export { app, auth, storage, db };
