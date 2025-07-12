<template>
  <div class="admin-dashboard-home">
    <h3>به داشبورد ادمین خوش آمدید</h3>
    <p>از این پنل می‌توانید کاربران VPN خود را مدیریت کرده، پلن‌های موجود را مشاهده و حساب خود را شارژ نمایید.</p>
    <div v-if="currentUser" class="balance-info">
      موجودی فعلی شما: <strong>{{ currentUser.balance ? currentUser.balance.toLocaleString() : 0 }} تومان</strong>
    </div>
    <!-- Add summary widgets or quick stats here later -->
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'AdminDashboardHome',
  computed: {
    ...mapGetters('auth', ['currentUser'])
  }
}
</script>

<style scoped>
.admin-dashboard-home {
  padding: 15px;
  text-align: right; /* RTL */
}
.admin-dashboard-home h3{
  font-size: 1.5em;
  color: #333;
  margin-bottom: 10px;
}
.admin-dashboard-home p{
  font-size: 1em;
  color: #555;
  line-height: 1.6;
}
.balance-info {
  margin-top: 20px;
  padding: 15px;
  background-color: #e3f2fd; /* Light blue background */
  border: 1px solid #bbdefb; /* Blue border */
  border-radius: 5px;
  color: #1e88e5; /* Blue text */
  font-size: 1.1em;
}
.balance-info strong {
  font-weight: bold;
}
</style>
