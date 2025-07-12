<template>
  <div class="sa-manage-plans">
    <header class="content-header">
      <h3>مدیریت پلن‌های VPN</h3>
      <button @click="openCreateModal" class="btn btn-primary">افزودن پلن جدید</button>
    </header>

    <div v-if="loading" class="loading-indicator">در حال بارگذاری اطلاعات پلن‌ها...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="table-container">
      <table v-if="!loading && plans.length > 0" class="styled-table">
        <thead>
          <tr>
            <th>شناسه</th>
          <th>نام پلن</th>
          <th>قیمت (تومان)</th>
          <th>مدت (روز)</th>
          <th>محدودیت داده (GB)</th>
          <th>وضعیت</th>
          <th>تاریخ ایجاد</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="plan in plans" :key="plan.id">
          <td>{{ plan.id }}</td>
          <td>{{ plan.name }}</td>
          <td>{{ plan.price.toLocaleString() }}</td>
          <td>{{ plan.duration_days }}</td>
          <td>{{ plan.data_limit_gb }}</td>
          <td>
            <span :class="plan.is_active ? 'status-active' : 'status-inactive'">
              {{ plan.is_active ? 'فعال' : 'غیرفعال' }}
            </span>
          </td>
          <td>{{ formatDate(plan.created_at) }}</td>
          <td>
            <button @click="openEditModal(plan)" class="btn btn-sm btn-warning">ویرایش</button>
            <button @click="confirmDeletePlan(plan.id)" class="btn btn-sm btn-danger">حذف</button>
          </td>
        </tr>
      </tbody>
    </table>
    </div>
    <p v-if="!loading && plans.length === 0 && !error" class="empty-state">
      هیچ پلنی برای نمایش وجود ندارد.
    </p>

    <!-- Plan Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h4>{{ editingPlan ? 'ویرایش پلن' : 'افزودن پلن جدید' }}</h4>
        <form @submit.prevent="editingPlan ? handleUpdatePlan() : handleCreatePlan()">
          <div class="form-group">
            <label for="planName">نام پلن:</label>
            <input type="text" id="planName" v-model="currentPlanData.name" required />
          </div>
          <div class="form-group">
            <label for="planPrice">قیمت (تومان):</label>
            <input type="number" id="planPrice" v-model.number="currentPlanData.price" min="0" required />
          </div>
          <div class="form-group">
            <label for="planDuration">مدت اعتبار (روز):</label>
            <input type="number" id="planDuration" v-model.number="currentPlanData.duration_days" min="1" required />
          </div>
          <div class="form-group">
            <label for="planDataLimit">محدودیت داده (GB):</label>
            <input type="number" id="planDataLimit" v-model.number="currentPlanData.data_limit_gb" min="0" step="0.1" required />
          </div>
          <div class="form-group">
            <label for="planIsActive">وضعیت فعال:</label>
            <input type="checkbox" id="planIsActive" v-model="currentPlanData.is_active" />
          </div>

          <div v-if="modalError" class="error-message modal-error">{{ modalError }}</div>

          <div class="modal-actions">
            <button type="submit" class="btn btn-success" :disabled="modalLoading">
              <span v-if="modalLoading">درحال ذخیره...</span>
              <span v-else>{{ editingPlan ? 'به‌روزرسانی' : 'ایجاد' }}</span>
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">انصراف</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import superadminService from '../../../services/superadminService'; // Assuming this service also handles plans

export default {
  name: 'SAManagePlans',
  data() {
    return {
      plans: [],
      loading: false,
      error: null,
      showModal: false,
      editingPlan: null, // Holds the plan object being edited
      currentPlanData: { // Data for the form
        name: '',
        price: 0,
        duration_days: 30,
        data_limit_gb: 10,
        is_active: true,
      },
      modalLoading: false,
      modalError: null,
    };
  },
  methods: {
    async fetchPlans() {
      this.loading = true;
      this.error = null;
      try {
        const response = await superadminService.getPlans();
        this.plans = response.data;
      } catch (err) {
        this.error = 'خطا در دریافت لیست پلن‌ها: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateTimeString) {
      if (!dateTimeString) return '';
      const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
      return new Date(dateTimeString).toLocaleDateString('fa-IR', options);
    },
    openCreateModal() {
      this.editingPlan = null;
      this.currentPlanData = { name: '', price: 0, duration_days: 30, data_limit_gb: 10, is_active: true };
      this.modalError = null;
      this.showModal = true;
    },
    openEditModal(plan) {
      this.editingPlan = plan;
      // Make a copy to avoid mutating the original plan object in the list directly
      this.currentPlanData = { ...plan };
      this.modalError = null;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.editingPlan = null;
      // Reset currentPlanData if needed, or leave it as is if preferred
      // this.currentPlanData = { name: '', price: 0, duration_days: 30, data_limit_gb: 10, is_active: true };
      this.modalError = null;
    },
    async handleCreatePlan() {
      this.modalLoading = true;
      this.modalError = null;
      try {
        const payload = {
            ...this.currentPlanData,
            price: Number(this.currentPlanData.price),
            duration_days: Number(this.currentPlanData.duration_days),
            data_limit_gb: Number(this.currentPlanData.data_limit_gb),
        };
        await superadminService.createPlan(payload);
        this.closeModal();
        await this.fetchPlans(); // Refresh list
      } catch (err) {
        this.modalError = 'خطا در ایجاد پلن: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        this.modalLoading = false;
      }
    },
    async handleUpdatePlan() {
      if (!this.editingPlan) return;
      this.modalLoading = true;
      this.modalError = null;
      try {
        const payload = {
            ...this.currentPlanData,
            price: Number(this.currentPlanData.price),
            duration_days: Number(this.currentPlanData.duration_days),
            data_limit_gb: Number(this.currentPlanData.data_limit_gb),
        };
        await superadminService.updatePlan(this.editingPlan.id, payload);
        this.closeModal();
        await this.fetchPlans(); // Refresh list
      } catch (err) {
        this.modalError = 'خطا در به‌روزرسانی پلن: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        this.modalLoading = false;
      }
    },
    async confirmDeletePlan(planId) {
      if (window.confirm('آیا از حذف این پلن اطمینان دارید؟ این عمل ممکن است بر کاربران فعال این پلن تاثیر بگذارد.')) {
        this.loading = true; // Use main loading indicator for delete action
        this.error = null;
        try {
          await superadminService.deletePlan(planId);
          await this.fetchPlans(); // Refresh list
        } catch (err) {
          this.error = 'خطا در حذف پلن: ' + (err.response?.data?.detail || err.message);
          console.error(err);
          this.loading = false;
        }
      }
    }
  },
  created() {
    this.fetchPlans();
  }
};
</script>

<style scoped>
/* Styles are largely similar to SAManageAdmins.vue, so they can be shared or defined globally */
.sa-manage-plans {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.content-header h3 {
  font-size: 1.8em;
  color: #333;
  margin: 0;
}

.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.95em;
  transition: background-color 0.2s ease-in-out, box-shadow 0.2s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}
.btn-warning:hover {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}
.btn-danger:hover {
  background-color: #c82333;
}

.btn-success {
  background-color: #28a745;
  color: white;
}
.btn-success:hover {
  background-color: #1e7e34;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #545b62;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.85em;
  margin: 0 3px;
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

.styled-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  font-size: 0.95em;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  overflow: hidden;
}

.styled-table thead tr {
  background-color: #17a2b8; /* A different color for plans - info blue */
  color: #ffffff;
  text-align: right;
  font-weight: bold;
}

.styled-table th,
.styled-table td {
  padding: 12px 15px;
  text-align: right;
}

.styled-table tbody tr {
  border-bottom: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
  background-color: #f3f3f3;
}

.styled-table tbody tr:last-of-type {
  border-bottom: 2px solid #17a2b8;
}

.styled-table tbody tr:hover {
  background-color: #e2f3f5; /* Light info blue hover */
}

.status-active {
  color: #28a745;
  font-weight: bold;
}
.status-inactive {
  color: #dc3545;
  font-weight: bold;
}

/* Modal Styles - identical to SAManageAdmins, can be globalized */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  direction: rtl;
}

.modal-content {
  background-color: white;
  padding: 25px 30px;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2);
  width: 90%;
  max-width: 500px; /* Or adjust for plan form if wider fields are needed */
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h4 {
  font-size: 1.6em;
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 18px;
  text-align: right;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #444;
}

.form-group input[type="text"],
.form-group input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1em;
}
.form-group input[type="checkbox"] {
  margin-left: 8px;
  vertical-align: middle;
}

.modal-error {
  margin-top: 0;
  margin-bottom: 15px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 25px;
}

.table-container {
  overflow-x: auto;
  width: 100%;
}

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .styled-table {
    font-size: 0.85em; /* Smaller font on mobile */
  }

  .styled-table th,
  .styled-table td {
    padding: 8px 10px;
  }

  .btn-sm {
    display: block;
    width: 100%;
    margin-bottom: 5px;
  }
  .btn-sm:last-child {
    margin-bottom: 0;
  }
}
</style>
