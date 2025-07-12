<template>
  <div id="app-container" :dir="$store.state.auth.userRole === 'superadmin' || $store.state.auth.userRole === 'admin' ? 'rtl' : 'ltr'">
    <header class="app-header">
      <div class="header-content">
        <h1>پنل مدیریت VPN</h1>
        <nav v-if="isAuthenticated">
          <span v-if="currentUser" class="user-greeting">خوش آمدید، {{ currentUser.username }} ({{ userRole }})</span>
          <button @click="handleLogout" class="logout-button">خروج</button>
        </nav>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>&copy; ۲۰۲۳ VPN Masters</p>
    </footer>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'App',
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'currentUser', 'userRole'])
  },
  methods: {
    ...mapActions('auth', ['logout']),
    async handleLogout() {
      try {
        const loggedOutUserType = await this.logout();
        // Redirect to the appropriate login page after logout
        if (loggedOutUserType === 'superadmin' || this.$route.path.includes('superadmin')) {
          this.$router.push({ name: 'SuperAdminLogin' });
        } else if (loggedOutUserType === 'admin' || this.$route.path.includes('admin')) {
          // this.$router.push({ name: 'AdminLogin' }); // Future
          this.$router.push({ name: 'SuperAdminLogin' }); // Fallback for now
        } else {
          this.$router.push('/'); // Default fallback
        }
      } catch (error) {
        console.error("Logout failed:", error);
        // Fallback redirect even if logout action has issues
        this.$router.push('/');
      }
    }
  },
  watch: {
    '$store.state.auth.userRole'(newRole) {
      // This dynamically sets the dir attribute on the root HTML element
      // which is generally preferred for full page RTL.
      // However, for simplicity within Vue's scope, setting it on #app-container is also an option.
      document.documentElement.dir = (newRole === 'superadmin' || newRole === 'admin') ? 'rtl' : 'ltr';
    }
  },
  mounted() {
    // Set initial direction based on stored role
    document.documentElement.dir = (this.userRole === 'superadmin' || this.userRole === 'admin') ? 'rtl' : 'ltr';
  }
}
</script>

<style>
/* Global styles from main.css will apply. These are specific to App.vue layout */
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: 'Tahoma', 'Vazir', sans-serif; /* Added Vazir as a common Persian font */
}

.app-header {
  background-color: #34495e; /* Dark blue-grey */
  color: white;
  padding: 15px 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-content h1 {
  font-size: 1.8em;
  margin: 0;
}

.app-header nav {
  display: flex;
  align-items: center;
}

.user-greeting {
  margin-left: 20px; /* RTL: use margin-right if LTR */
  font-size: 0.9em;
}

.logout-button {
  background-color: #e74c3c; /* Red */
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background-color 0.3s ease;
}

.logout-button:hover {
  background-color: #c0392b; /* Darker red */
}

.app-main {
  flex-grow: 1;
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 20px auto; /* Centering main content area */
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0,0,0,0.05);
  border-radius: 8px;
}

.app-footer {
  text-align: center;
  padding: 20px;
  background-color: #ecf0f1; /* Light grey */
  color: #7f8c8d; /* Grey text */
  font-size: 0.9em;
  border-top: 1px solid #dcdcdc;
}
</style>
