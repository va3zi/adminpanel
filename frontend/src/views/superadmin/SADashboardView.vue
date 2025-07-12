<template>
  <div class="dashboard-container sa-dashboard-container">
    <header class="dashboard-header">
      <h1>داشبورد مدیریت کل</h1>
      <p v-if="currentUser">خوش آمدید، {{ currentUser.username }}!</p>
    </header>

    <nav class="dashboard-nav">
      <ul>
        <li><router-link :to="{ name: 'SADashboardHome' }">صفحه اصلی داشبورد</router-link></li>
        <li><router-link :to="{ name: 'SAManageAdmins' }">مدیریت ادمین‌ها</router-link></li>
        <li><router-link :to="{ name: 'SAManagePlans' }">مدیریت پلن‌ها</router-link></li>
        <!-- Add more navigation links as features are developed -->
      </ul>
    </nav>

    <section class="dashboard-content">
      <!-- Child routes for SA Dashboard will be rendered here -->
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'SADashboardView',
  computed: {
    ...mapGetters('auth', ['currentUser'])
  },
  created() {
    // If landing directly on dashboard, ensure user info is loaded
    // This is mostly handled by router guards and App.vue's initializeAuth
    if (!this.currentUser && this.$store.getters['auth/isAuthenticated']) {
      this.$store.dispatch('auth/fetchSuperAdminMe');
    }
    // Default to a child route if SADashboardView is accessed directly without a child path
    if (this.$route.name === 'SuperAdminDashboard') {
      this.$router.replace({ name: 'SADashboardHome' });
    }
  }
};
</script>

<style scoped>
.sa-dashboard-container {
  padding: 20px;
  background-color: #f4f6f8; /* Light grey background for the dashboard area */
  border-radius: 8px; /* Consistent with App.vue main area */
}

.dashboard-header {
  text-align: right; /* RTL */
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dashboard-header h1 {
  font-size: 2.2em;
  color: #2c3e50; /* Dark blue-grey */
  margin-bottom: 5px;
}

.dashboard-header p {
  font-size: 1.1em;
  color: #555;
}

.dashboard-nav {
  margin-bottom: 30px;
  background-color: #fff;
  padding: 15px;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.dashboard-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  justify-content: flex-start; /* RTL */
  gap: 20px; /* Space between nav items */
}

.dashboard-nav li a {
  text-decoration: none;
  color: #3498db; /* Blue links */
  font-weight: bold;
  padding: 10px 15px;
  border-radius: 4px;
  transition: background-color 0.3s, color 0.3s;
}

.dashboard-nav li a:hover,
.dashboard-nav li a.router-link-exact-active { /* Style for active link */
  background-color: #3498db;
  color: white;
}

.dashboard-content {
  background-color: #ffffff;
  padding: 20px;
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  min-height: 300px; /* Give some space for content */
}
</style>
