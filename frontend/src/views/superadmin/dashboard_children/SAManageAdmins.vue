<template>
  <div class="sa-manage-admins">
    <header class="content-header">
      <h3>مدیریت ادمین‌ها</h3>
      <button @click="openCreateModal" class="btn btn-primary">افزودن ادمین جدید</button>
    </header>

    <div v-if="loading" class="loading-indicator">در حال بارگذاری اطلاعات ادمین‌ها...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="table-container">
      <table v-if="!loading && admins.length > 0" class="styled-table">
        <thead>
          <tr>
            <th>شناسه</th>
          <th>نام کاربری</th>
          <th>ایمیل</th>
          <th>موجودی (تومان)</th>
          <th>وضعیت</th>
          <th>تاریخ ایجاد</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="admin in admins" :key="admin.id">
          <td>{{ admin.id }}</td>
          <td>{{ admin.username }}</td>
          <td>{{ admin.email }}</td>
          <td>{{ admin.balance.toLocaleString() }}</td>
          <td>
            <span :class="admin.is_active ? 'status-active' : 'status-inactive'">
              {{ admin.is_active ? 'فعال' : 'غیرفعال' }}
            </span>
          </td>
          <td>{{ formatDate(admin.created_at) }}</td>
          <td>
            <button @click="openEditModal(admin)" class="btn btn-sm btn-warning">ویرایش</button>
            <button @click="confirmDeleteAdmin(admin.id)" class="btn btn-sm btn-danger">حذف</button>
          </td>
        </tr>
      </tbody>
    </table>
    </div>
    <p v-if="!loading && admins.length === 0 && !error" class="empty-state">
      هیچ ادمینی برای نمایش وجود ندارد.
    </p>

    <!-- Admin Create/Edit Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <h4>{{ editingAdmin ? 'ویرایش ادمین' : 'افزودن ادمین جدید' }}</h4>
        <form @submit.prevent="editingAdmin ? handleUpdateAdmin() : handleCreateAdmin()">
          <div class="form-group">
            <label for="username">نام کاربری:</label>
            <input type="text" id="username" v-model="currentAdminData.username" required :disabled="editingAdmin && !isUsernameEditable" />
             <small v-if="editingAdmin && !isUsernameEditable" class="form-text text-muted">نام کاربری پس از ایجاد قابل تغییر نیست.</small>
          </div>
          <div class="form-group">
            <label for="email">ایمیل:</label>
            <input type="email" id="email" v-model="currentAdminData.email" required />
          </div>
          <div class="form-group" v-if="!editingAdmin">
            <label for="password">رمز عبور:</label>
            <input type="password" id="password" v-model="currentAdminData.password" required />
          </div>
           <div class="form-group" v-if="editingAdmin">
            <label for="new_password">رمز عبور جدید (اختیاری):</label>
            <input type="password" id="new_password" v_model="currentAdminData.new_password" placeholder="برای تغییر رمز وارد کنید" />
            <small class="form-text text-muted">برای تغییر رمز عبور ادمین، از طریق API اختصاصی تغییر رمز اقدام شود (در این فرم پیاده‌سازی نشده).</small>
          </div>
          <div class="form-group">
            <label for="balance">موجودی اولیه (تومان):</label>
            <input type="number" id="balance" v-model.number="currentAdminData.balance" min="0" />
          </div>
          <div class="form-group">
            <label for="is_active">وضعیت فعال:</label>
            <input type="checkbox" id="is_active" v-model="currentAdminData.is_active" />
          </div>

          <div v-if="modalError" class="error-message modal-error">{{ modalError }}</div>

          <div class="modal-actions">
            <button type="submit" class="btn btn-success" :disabled="modalLoading">
              <span v-if="modalLoading">درحال ذخیره...</span>
              <span v-else>{{ editingAdmin ? 'به‌روزرسانی' : 'ایجاد' }}</span>
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">انصراف</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import superadminService from '../../../services/superadminService';

export default {
  name: 'SAManageAdmins',
  data() {
    return {
      admins: [],
      loading: false,
      error: null,
      showModal: false,
      editingAdmin: null, // Holds the admin object being edited
      currentAdminData: { // Data for the form
        username: '',
        email: '',
        password: '',
        new_password: '', // For editing password, though this form won't directly use it for update
        balance: 0,
        is_active: true,
      },
      modalLoading: false,
      modalError: null,
      isUsernameEditable: false, // Username is typically not editable after creation
    };
  },
  methods: {
    async fetchAdmins() {
      this.loading = true;
      this.error = null;
      try {
        const response = await superadminService.getAdmins();
        this.admins = response.data;
      } catch (err) {
        this.error = 'خطا در دریافت لیست ادمین‌ها: ' + (err.response?.data?.detail || err.message);
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
      this.editingAdmin = null;
      this.currentAdminData = { username: '', email: '', password: '', new_password: '', balance: 0, is_active: true };
      this.isUsernameEditable = true; // Username is editable for new admins
      this.modalError = null;
      this.showModal = true;
    },
    openEditModal(admin) {
      this.editingAdmin = admin;
      // Make a copy to avoid mutating the original admin object in the list directly
      this.currentAdminData = {
        ...admin,
        password: '', // Clear password field for edit
        new_password: '',
      };
      this.isUsernameEditable = false; // Username is not editable
      this.modalError = null;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.editingAdmin = null;
      this.currentAdminData = { username: '', email: '', password: '', new_password:'', balance: 0, is_active: true };
      this.modalError = null;
    },
    async handleCreateAdmin() {
      this.modalLoading = true;
      this.modalError = null;
      try {
        // Ensure balance is a number, default to 0 if not set
        const payload = {
            username: this.currentAdminData.username,
            email: this.currentAdminData.email,
            password: this.currentAdminData.password,
            balance: Number(this.currentAdminData.balance) || 0,
            is_active: this.currentAdminData.is_active,
        };
        await superadminService.createAdmin(payload);
        this.closeModal();
        await this.fetchAdmins(); // Refresh list
      } catch (err) {
        this.modalError = 'خطا در ایجاد ادمین: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        this.modalLoading = false;
      }
    },
    async handleUpdateAdmin() {
      if (!this.editingAdmin) return;
      this.modalLoading = true;
      this.modalError = null;
      try {
        const payload = {
            email: this.currentAdminData.email,
            balance: Number(this.currentAdminData.balance) || 0,
            is_active: this.currentAdminData.is_active,
            // Username is not sent for update as it's not editable here.
            // Password change should be a separate endpoint / logic.
        };
        // if (this.currentAdminData.new_password) {
        //   payload.password = this.currentAdminData.new_password; // This API might not support password change directly
        // }
        await superadminService.updateAdmin(this.editingAdmin.id, payload);
        this.closeModal();
        await this.fetchAdmins(); // Refresh list
      } catch (err) {
        this.modalError = 'خطا در به‌روزرسانی ادمین: ' + (err.response?.data?.detail || err.message);
        console.error(err);
      } finally {
        this.modalLoading = false;
      }
    },
    async confirmDeleteAdmin(adminId) {
      if (window.confirm('آیا از حذف این ادمین اطمینان دارید؟ این عمل قابل بازگشت نیست.')) {
        this.loading = true; // Use main loading indicator for delete action
        this.error = null;
        try {
          await superadminService.deleteAdmin(adminId);
          await this.fetchAdmins(); // Refresh list
        } catch (err) {
          this.error = 'خطا در حذف ادمین: ' + (err.response?.data?.detail || err.message);
          console.error(err);
          this.loading = false; // Reset loading if error occurs during delete
        }
        // No finally here for loading, as fetchAdmins will set it.
      }
    }
  },
  created() {
    this.fetchAdmins();
  }
};
</script>

<style scoped>
.sa-manage-admins {
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
  background-color: #007bff; /* Bootstrap primary */
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
}

.btn-warning {
  background-color: #ffc107; /* Bootstrap warning */
  color: #212529;
}
.btn-warning:hover {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545; /* Bootstrap danger */
  color: white;
}
.btn-danger:hover {
  background-color: #c82333;
}

.btn-success {
  background-color: #28a745; /* Bootstrap success */
  color: white;
}
.btn-success:hover {
  background-color: #1e7e34;
}

.btn-secondary {
  background-color: #6c757d; /* Bootstrap secondary */
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
  color: #e74c3c; /* Red for errors */
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
  overflow: hidden; /* For border-radius on table */
}

.styled-table thead tr {
  background-color: #009879; /* A nice teal color */
  color: #ffffff;
  text-align: right; /* RTL */
  font-weight: bold;
}

.styled-table th,
.styled-table td {
  padding: 12px 15px;
  text-align: right; /* RTL */
}

.styled-table tbody tr {
  border-bottom: 1px solid #dddddd;
}

.styled-table tbody tr:nth-of-type(even) {
  background-color: #f3f3f3;
}

.styled-table tbody tr:last-of-type {
  border-bottom: 2px solid #009879;
}

.styled-table tbody tr:hover {
  background-color: #e8f4f2; /* Light teal hover */
  cursor: default;
}

.status-active {
  color: #28a745; /* Green */
  font-weight: bold;
}
.status-inactive {
  color: #dc3545; /* Red */
  font-weight: bold;
}

/* Modal Styles */
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
  max-width: 500px;
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
.form-group input[type="email"],
.form-group input[type="password"],
.form-group input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1em;
}
.form-group input[type="checkbox"] {
  margin-left: 8px; /* RTL: margin-right */
  vertical-align: middle;
}

.form-text.text-muted {
    font-size: 0.85em;
    color: #6c757d;
}


.modal-error {
  margin-top: 0;
  margin-bottom: 15px; /* Space before actions */
}

.modal-actions {
  display: flex;
  justify-content: flex-end; /* Buttons to the left in RTL for forms */
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
