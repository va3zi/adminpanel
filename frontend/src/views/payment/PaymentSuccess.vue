<template>
  <div class="payment-status-container">
    <div class="payment-box success">
      <div class="icon-container">
        <span class="icon">&#10004;</span> <!-- Checkmark -->
      </div>
      <h2>پرداخت موفق</h2>
      <p>حساب شما با موفقیت شارژ شد. موجودی جدید شما در پنل به‌روزرسانی شده است.</p>
      <p v-if="refId" class="ref-id">شماره پیگیری: {{ refId }}</p>
      <router-link :to="{ name: 'AdminDashboard' }" class="btn btn-primary">بازگشت به داشبورد</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaymentSuccess',
  computed: {
    refId() {
      return this.$route.query.ref_id || null;
    }
  },
  created() {
    // Optionally, you can trigger a refresh of the user's data here
    // This is useful if the user navigates back using browser buttons instead of the dashboard link
    this.$store.dispatch('auth/fetchAdminMe');
  }
}
</script>

<style scoped>
.payment-status-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  text-align: center;
  padding: 20px;
  direction: rtl;
}
.payment-box {
  background-color: #fff;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  max-width: 500px;
  width: 100%;
}
.icon-container {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 20px auto;
  display: flex;
  justify-content: center;
  align-items: center;
}
.icon {
  font-size: 40px;
  color: white;
}
.payment-box.success .icon-container {
  background-color: #28a745; /* Green */
}
h2 {
  font-size: 2em;
  margin-bottom: 15px;
}
.payment-box.success h2 {
  color: #28a745;
}
p {
  font-size: 1.1em;
  color: #555;
  line-height: 1.6;
  margin-bottom: 20px;
}
.ref-id {
  font-size: 0.9em;
  color: #777;
  background-color: #f0f0f0;
  padding: 8px;
  border-radius: 4px;
  display: inline-block;
}
.btn {
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  text-decoration: none;
  display: inline-block;
  transition: background-color 0.3s;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
}
</style>
