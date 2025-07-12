<template>
  <div class="payment-status-container">
    <div class="payment-box failed">
      <div class="icon-container">
        <span class="icon">&#10006;</span> <!-- Cross mark -->
      </div>
      <h2>پرداخت ناموفق</h2>
      <p>{{ errorMessage }}</p>
      <p v-if="errorCode" class="ref-id">کد خطا: {{ errorCode }}</p>
      <router-link :to="{ name: 'AdminRecharge' }" class="btn btn-primary">تلاش مجدد</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaymentFailed',
  computed: {
    errorCode() {
      return this.$route.query.code || null;
    },
    errorMessage() {
      const error = this.$route.query.error;
      switch (error) {
        case 'transaction_not_found':
          return 'تراکنش مورد نظر یافت نشد یا قبلاً پردازش شده است.';
        case 'payment_cancelled':
          return 'پرداخت توسط شما لغو شد.';
        case 'verification_failed':
          return 'تایید پرداخت با خطا مواجه شد. در صورت کسر وجه، مبلغ طی ۷۲ ساعت آینده به حساب شما باز خواهد گشت.';
        case 'internal_error':
          return 'یک خطای داخلی در سرور رخ داده است. لطفاً با پشتیبانی تماس بگیرید.';
        default:
          return 'پرداخت با خطا مواجه شد. لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.';
      }
    }
  }
}
</script>

<style scoped>
/* Using same styles as PaymentSuccess.vue but with different colors */
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
.payment-box.failed .icon-container {
  background-color: #dc3545; /* Red */
}
h2 {
  font-size: 2em;
  margin-bottom: 15px;
}
.payment-box.failed h2 {
  color: #dc3545;
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
