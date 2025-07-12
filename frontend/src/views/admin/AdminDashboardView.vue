<template>
  <div class="dashboard-container admin-dashboard-container">
    <header class="dashboard-header">
      <h1>داشبورد ادمین</h1>
      <p v-if="currentUser">خوش آمدید، {{ currentUser.username }}! موجودی شما: {{ currentUser.balance ? currentUser.balance.toLocaleString() : 0 }} تومان</p>
    </header>

    <nav class="dashboard-nav">
      <ul>
        <li><router-link :to="{ name: 'AdminDashboardHome' }">صفحه اصلی</router-link></li>
        <li><router-link :to="{ name: 'AdminViewPlans' }">مشاهده پلن‌ها</router-link></li>
        <li><router-link :to="{ name: 'AdminManageUsers' }">مدیریت کاربران VPN</router-link></li>
        <li><router-link :to="{ name: 'AdminRecharge' }">شارژ حساب</router-link></li>
        <!-- Add more navigation links as features are developed -->
      </ul>
    </nav>

    <section class="dashboard-content">
      <!-- Child routes for Admin Dashboard will be rendered here -->
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'AdminDashboardView',
  computed: {
    // Assuming 'currentUser' from auth store contains { username, balance, ... } for admin
    ...mapGetters('auth', ['currentUser', 'isAuthenticated', 'userRole'])
  },
  created() {
    // If landing directly on dashboard, ensure user info is loaded
    // This is mostly handled by router guards and App.vue's initializeAuth
    if (this.isAuthenticated && this.userRole === 'admin' && !this.currentUser) {
      this.$store.dispatch('auth/fetchAdminMe');
    }
    // Default to a child route if AdminDashboardView is accessed directly
    if (this.$route.name === 'AdminDashboard') {
      this.$router.replace({ name: 'AdminDashboardHome' });
    }
  }
};
</script>

<style scoped>
/* Styles can be similar to SADashboardView, with minor color tweaks if desired */
.admin-dashboard-container {
  padding: 20px;
  background-color: #f8f9fa; /* Slightly different light grey */
  border-radius: 8px;
}

.dashboard-header {
  text-align: right; /* RTL */
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dashboard-header h1 {
  font-size: 2.2em;
  color: #17a2b8; /* Admin theme color - Info Blue */
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
  color: #17a2b8; /* Admin theme color */
  font-weight: bold;
  padding: 10px 15px;
  border-radius: 4px;
  transition: background-color 0.3s, color 0.3s;
}

.dashboard-nav li a:hover,
.dashboard-nav li a.router-link-exact-active { /* Style for active link */
  background-color: #17a2b8;
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
