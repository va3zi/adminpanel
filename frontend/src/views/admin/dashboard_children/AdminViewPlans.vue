<template>
  <div class="admin-view-plans">
    <h3>مشاهده پلن‌های موجود</h3>
    <p>در این بخش می‌توانید لیست پلن‌های فعال VPN را که توسط مدیریت کل تعریف شده‌اند، مشاهده کنید.</p>

    <div v-if="loading" class="loading-indicator">در حال بارگذاری پلن‌ها...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!loading && plans.length > 0" class="plans-grid">
      <div v-for="plan in plans" :key="plan.id" class="plan-card">
        <h4>{{ plan.name }}</h4>
        <p><strong>قیمت:</strong> {{ plan.price.toLocaleString() }} تومان</p>
        <p><strong>مدت اعتبار:</strong> {{ plan.duration_days }} روز</p>
        <p><strong>محدودیت داده:</strong> {{ plan.data_limit_gb }} گیگابایت</p>
        <p><strong>وضعیت:</strong> <span :class="plan.is_active ? 'status-active' : 'status-inactive'">{{ plan.is_active ? 'فعال' : 'غیرفعال' }}</span></p>
        <!-- Add a button to select plan for user creation if needed in future -->
      </div>
    </div>
    <p v-if="!loading && plans.length === 0 && !error" class="empty-state">
      در حال حاضر هیچ پلن فعالی برای نمایش وجود ندارد.
    </p>
  </div>
</template>

<script>
import adminService from '../../../services/adminService';

export default {
  name: 'AdminViewPlans',
  data() {
    return {
      plans: [],
      loading: false,
      error: null,
    };
  },
  methods: {
    async fetchActivePlans() {
      this.loading = true;
      this.error = null;
      try {
        const response = await adminService.getActivePlans();
        this.plans = response.data;
      } catch (err) {
        this.error = 'خطا در دریافت لیست پلن‌ها: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  },
  created() {
    this.fetchActivePlans();
  }
}
</script>

<style scoped>
.admin-view-plans {
  padding: 15px;
  text-align: right; /* RTL */
}
.admin-view-plans h3 {
  font-size: 1.5em;
  color: #333;
  margin-bottom: 10px;
}
.admin-view-plans p {
  font-size: 1em;
  color: #555;
  margin-bottom: 20px;
}

.loading-indicator, .empty-state, .error-message {
  text-align: center;
  padding: 20px;
  font-size: 1.1em;
  color: #555;
}
.error-message {
  color: #e74c3c;
  background-color: #fdd;
  border: 1px solid #fbb;
  border-radius: 5px;
  margin-bottom: 15px;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.plan-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.plan-card h4 {
  font-size: 1.3em;
  color: #17a2b8; /* Admin theme color */
  margin-top: 0;
  margin-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
}

.plan-card p {
  font-size: 0.95em;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.5;
}
.plan-card p strong {
  font-weight: 600;
  margin-left: 5px; /* RTL */
}

.status-active {
  color: #28a745; /* Green */
  font-weight: bold;
}
.status-inactive {
  color: #dc3545; /* Red */
  font-weight: bold;
}
</style>
