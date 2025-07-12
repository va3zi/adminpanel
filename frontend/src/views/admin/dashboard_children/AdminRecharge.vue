<template>
  <div class="admin-recharge">
    <h3>شارژ حساب کاربری</h3>
    <p>موجودی فعلی شما: <strong v-if="currentUser">{{ currentUser.balance ? currentUser.balance.toLocaleString() : 0 }} تومان</strong></p>
    <p>در این بخش می‌توانید موجودی حساب پنل ادمین خود را از طریق درگاه پرداخت زرین‌پال افزایش دهید.</p>

    <div class="recharge-form-container">
      <form @submit.prevent="handlePaymentRequest">
        <div class="form-group">
          <label for="amount">مبلغ شارژ (تومان):</label>
          <input type="number" id="amount" v-model.number="amount" placeholder="مثلاً: 50000" min="1000" required />
        </div>
        <button type="submit" class="btn btn-success" :disabled="loading">
          <span v-if="loading">درحال ارسال به درگاه...</span>
          <span v-else>پرداخت</span>
        </button>
        <p v-if="error" class="error-message">{{ error }}</p>
      </form>
    </div>

    <div class="payment-history">
      <h4>تاریخچه پرداخت‌ها</h4>
      <!-- Payment history table will be implemented later or as a separate component -->
      <p class="text-muted">تاریخچه پرداخت‌های شما در اینجا نمایش داده خواهد شد.</p>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import adminService from '../../../services/adminService';

export default {
  name: 'AdminRecharge',
  data() {
    return {
      amount: null,
      loading: false,
      error: null,
    };
  },
  computed: {
    ...mapGetters('auth', ['currentUser'])
  },
  methods: {
    ...mapActions('auth', ['fetchAdminMe']), // To refresh user data after payment
    async handlePaymentRequest() {
      if (!this.amount || this.amount < 1000) {
        this.error = 'مبلغ باید حداقل ۱۰۰۰ تومان باشد.';
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const response = await adminService.requestPayment(this.amount);
        const paymentUrl = response.data.payment_url;
        if (paymentUrl) {
          // Redirect the user to the payment gateway
          window.location.href = paymentUrl;
        } else {
          this.error = 'خطا: لینک پرداخت از سرور دریافت نشد.';
        }
      } catch (err) {
        this.error = 'خطا در اتصال به درگاه پرداخت: ' + (err.response?.data?.detail || err.message);
      } finally {
        this.loading = false;
      }
    },
    // This method can be called from the PaymentSuccess view via an event bus or by re-fetching user data
    // when the user navigates back to the dashboard.
    async refreshUserData() {
        await this.fetchAdminMe();
    }
  }
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
    color: #007bff;
}

.recharge-form-container {
  margin-top: 25px;
  padding: 20px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  max-width: 400px;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}

.form-group input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1em;
}

.btn-success {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s;
}
.btn-success:hover {
  background-color: #218838;
}
.btn-success:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 15px;
  font-size: 0.9em;
}

.payment-history {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}
.text-muted {
    color: #6c757d !important;
}
</style>
