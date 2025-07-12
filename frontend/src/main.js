import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // Import router
import store from './store';   // Import store

// Basic styling
import './assets/main.css';

const app = createApp(App);

app.use(store); // Use Vuex store
app.use(router); // Use Vue Router

// Attempt to initialize authentication state from localStorage when the app starts
// This helps maintain login state across page refreshes.
store.dispatch('auth/initializeAuth').then(() => {
  // Mount the app after auth initialization (or any other async setup) is done
  app.mount('#app');
}).catch(error => {
  console.error("Error during app initialization (auth):", error);
  // Still mount the app even if auth init fails, router guards will handle redirects
  app.mount('#app');
});
