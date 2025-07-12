<template>
  <div class="admin-recharge">
    <h3>شارژ حساب کاربری</h3>
    <p>موجودی فعلی شما: <strong v-if="currentUser">{{ currentUser.balance ? currentUser.balance.toLocaleString() : 0 }} تومان</strong></p>
    <p>در این بخش می‌توانید موجودی حساب پنل ادمین خود را از طریق درگاه پرداخت زرین‌پال افزایش دهید.</p>

    <!-- Zarinpal integration form will go here -->
    <div class="placeholder-content">
      فرم ورود مبلغ و دکمه اتصال به درگاه پرداخت زرین‌پال در اینجا قرار خواهد گرفت.
      <br/>
      پس از پرداخت موفق، موجودی شما به صورت خودکار به‌روزرسانی می‌شود.
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'AdminRecharge',
  computed: {
    ...mapGetters('auth', ['currentUser'])
  }
  // Logic for Zarinpal payment initiation will be added later.
}
</script>

<style scoped>
.admin-recharge {
  padding: 15px;
  text-align: right; /* RTL */
}
.admin-recharge h3 {
  font-size: 1.5em;
  color: #333;
  margin-bottom: 10px;
}
.admin-recharge p {
  font-size: 1em;
  color: #555;
  margin-bottom: 10px;
  line-height: 1.6;
}
.admin-recharge p strong {
    font-weight: bold;
    color: #007bff; /* Bootstrap primary color for emphasis */
}
.placeholder-content {
  border: 1px dashed #ccc;
  padding: 20px;
  text-align: center;
  color: #777;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  background-color: #f9f9f9;
  margin-top: 25px;
}
</style>
