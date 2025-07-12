<template>
  <div class="admin-manage-users">
    <header class="content-header">
      <h3>مدیریت کاربران VPN</h3>
      <button @click="openCreateUserModal" class="btn btn-primary">ایجاد کاربر VPN جدید</button>
    </header>

    <div v-if="loadingUsers" class="loading-indicator">در حال بارگذاری کاربران...</div>
    <div v-if="usersError" class="error-message">{{ usersError }}</div>

    <table v-if="!loadingUsers && vpnUsers.length > 0" class="styled-table">
      <thead>
        <tr>
          <th>نام کاربری (Marzban)</th>
          <th>پلن</th>
          <th>تاریخ انقضا</th>
          <th>وضعیت پنل</th>
          <th>وضعیت Marzban</th>
          <th>حجم مصرفی / کل</th>
          <th>عملیات</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in vpnUsers" :key="user.id">
          <td>{{ user.marzban_username }}</td>
          <td>{{ getPlanName(user.plan_id) }}</td>
          <td>{{ user.expires_at ? formatDate(user.expires_at) : 'نامحدود' }}</td>
          <td>
            <span :class="user.is_active ? 'status-active' : 'status-inactive'">
              {{ user.is_active ? 'فعال' : 'غیرفعال' }}
            </span>
          </td>
          <td>{{ user.marzban_details?.status || 'درحال بررسی...' }}</td>
          <td>
            <template v-if="user.marzban_details">
              {{ formatBytes(user.marzban_details.used_traffic) }} /
              {{ user.marzban_details.data_limit > 0 ? formatBytes(user.marzban_details.data_limit) : 'نامحدود' }}
            </template>
            <template v-else>درحال بررسی...</template>
          </td>
          <td>
            <button @click="fetchUserDetailsAndShowSubscription(user.marzban_username)" class="btn btn-sm btn-info">لینک اتصال</button>
            <button @click="confirmResetTraffic(user.marzban_username)" class="btn btn-sm btn-warning">ریست ترافیک</button>
            <button @click="confirmDeleteUser(user.marzban_username)" class="btn btn-sm btn-danger">حذف</button>
            <!-- TODO: Edit User (e.g. change plan, notes - needs backend support for plan change propagation to Marzban) -->
          </td>
        </tr>
      </tbody>
    </table>
     <p v-if="!loadingUsers && vpnUsers.length === 0 && !usersError" class="empty-state">
      هنوز هیچ کاربر VPN ایجاد نکرده‌اید.
    </p>

    <!-- Create VPN User Modal -->
    <div v-if="showCreateUserModal" class="modal-overlay" @click.self="closeCreateUserModal">
      <div class="modal-content">
        <h4>ایجاد کاربر VPN جدید</h4>
        <form @submit.prevent="handleCreateVpnUser">
          <div class="form-group">
            <label for="marzbanUsername">نام کاربری در Marzban:</label>
            <input type="text" id="marzbanUsername" v-model="newUser.marzban_username" required />
            <small>این نام کاربری باید در Marzban یکتا باشد.</small>
          </div>
          <div class="form-group">
            <label for="planSelect">انتخاب پلن:</label>
            <select id="planSelect" v-model.number="newUser.plan_id" required>
              <option disabled value="">یک پلن انتخاب کنید...</option>
              <option v-for="plan in activePlans" :key="plan.id" :value="plan.id">
                {{ plan.name }} ({{ plan.price.toLocaleString() }} تومان - {{ plan.duration_days }} روز - {{ plan.data_limit_gb }}GB)
              </option>
            </select>
            <div v-if="loadingPlans" class="form-text text-muted">درحال بارگذاری پلن‌ها...</div>
          </div>
          <div class="form-group">
            <label for="userNotes">یادداشت (اختیاری):</label>
            <textarea id="userNotes" v-model="newUser.notes" rows="3"></textarea>
          </div>
          <div v-if="createUserError" class="error-message modal-error">{{ createUserError }}</div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-success" :disabled="creatingUser">
              <span v-if="creatingUser">درحال ایجاد...</span>
              <span v-else>ایجاد کاربر</span>
            </button>
            <button type="button" @click="closeCreateUserModal" class="btn btn-secondary">انصراف</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Subscription Info Modal -->
    <div v-if="showSubscriptionModal" class="modal-overlay" @click.self="closeSubscriptionModal">
        <div class="modal-content subscription-modal-content">
            <h4>اطلاعات اتصال کاربر: {{ currentSubscriptionInfo.marzban_username }}</h4>
            <div v-if="loadingSubscription" class="loading-indicator">درحال دریافت اطلاعات...</div>
            <div v-if="subscriptionError" class="error-message modal-error">{{ subscriptionError }}</div>
            <div v-if="!loadingSubscription && !subscriptionError">
                <div class="form-group">
                    <label>لینک اشتراک (Subscription URL):</label>
                    <input type="text" :value="currentSubscriptionInfo.subscription_url" readonly @focus="$event.target.select()" class="sub-link-input"/>
                    <button @click="copyToClipboard(currentSubscriptionInfo.subscription_url)" class="btn btn-sm btn-outline-secondary">کپی</button>
                </div>
                 <div v-if="currentSubscriptionInfo.subscription_url" class="qr-code-container">
                    <p>QR Code:</p>
                    <qr-code :text="currentSubscriptionInfo.subscription_url" :size="200" error-level="L"></qr-code>
                </div>
                <div v-if="currentSubscriptionInfo.raw_links && currentSubscriptionInfo.raw_links.length > 0" class="raw-links-container">
                    <h5>لینک‌های خام:</h5>
                    <ul>
                        <li v-for="(link, index) in currentSubscriptionInfo.raw_links" :key="index">
                            <input type="text" :value="link" readonly @focus="$event.target.select()" class="sub-link-input raw-link-input"/>
                             <button @click="copyToClipboard(link)" class="btn btn-sm btn-outline-secondary">کپی</button>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="modal-actions">
                <button type="button" @click="closeSubscriptionModal" class="btn btn-secondary">بستن</button>
            </div>
        </div>
    </div>

  </div>
</template>

<script>
import adminService from '../../../services/adminService';
import QrCode from 'vue-qrcode-component'; // Import QR Code component

export default {
  name: 'AdminManageUsers',
  components: {
    QrCode,
  },
  data() {
    return {
      vpnUsers: [],
      activePlans: [],
      loadingUsers: false,
      loadingPlans: false,
      usersError: null,
      plansError: null, // For plans loading error in modal
      showCreateUserModal: false,
      creatingUser: false,
      createUserError: null,
      newUser: {
        marzban_username: '',
        plan_id: '',
        notes: '',
      },
      showSubscriptionModal: false,
      loadingSubscription: false,
      subscriptionError: null,
      currentSubscriptionInfo: {
        marzban_username: '',
        subscription_url: '',
        raw_links: [],
      },
    };
  },
  methods: {
    formatDate(dateTimeString) {
      if (!dateTimeString) return '';
      return new Date(dateTimeString).toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },
    async fetchVpnUsers() {
      this.loadingUsers = true;
      this.usersError = null;
      try {
        const response = await adminService.getVpnUsers();
        // Fetch Marzban details for each user sequentially for now to avoid rate limits / complexity
        // In a real app, might do this on demand or batch it carefully.
        const usersWithDetails = [];
        for (const user of response.data) {
            try {
                const detailsResponse = await adminService.getVpnUserDetails(user.marzban_username);
                usersWithDetails.push(detailsResponse.data); // This contains VpnUser + marzban_details
            } catch (detailError) {
                console.warn(`Could not fetch Marzban details for ${user.marzban_username}:`, detailError);
                usersWithDetails.push({...user, marzban_details: null}); // Add user with null details
            }
        }
        this.vpnUsers = usersWithDetails;
      } catch (err) {
        this.usersError = 'خطا در دریافت لیست کاربران VPN: ' + (err.response?.data?.detail || err.message);
      } finally {
        this.loadingUsers = false;
      }
    },
    async fetchActivePlans() {
      this.loadingPlans = true;
      this.plansError = null;
      try {
        const response = await adminService.getActivePlans();
        this.activePlans = response.data;
      } catch (err) {
        this.plansError = 'خطا در دریافت لیست پلن‌ها: ' + (err.response?.data?.detail || err.message);
        this.createUserError = this.plansError; // Show in modal if plans fail to load
      } finally {
        this.loadingPlans = false;
      }
    },
    getPlanName(planId) {
        const plan = this.activePlans.find(p => p.id === planId);
        return plan ? plan.name : 'نامشخص';
    },
    openCreateUserModal() {
      this.newUser = { marzban_username: '', plan_id: '', notes: '' };
      this.createUserError = null;
      if (this.activePlans.length === 0) { // Fetch plans if not already loaded for the modal
          this.fetchActivePlans();
      }
      this.showCreateUserModal = true;
    },
    closeCreateUserModal() {
      this.showCreateUserModal = false;
    },
    async handleCreateVpnUser() {
      this.creatingUser = true;
      this.createUserError = null;
      try {
        await adminService.createVpnUser(this.newUser);
        this.closeCreateUserModal();
        await this.fetchVpnUsers(); // Refresh user list
      } catch (err) {
        this.createUserError = 'خطا در ایجاد کاربر VPN: ' + (err.response?.data?.detail || err.message);
      } finally {
        this.creatingUser = false;
      }
    },
    async confirmDeleteUser(marzbanUsername) {
      if (window.confirm(`آیا از حذف کاربر '${marzbanUsername}' اطمینان دارید؟ این عمل از Marzban نیز کاربر را حذف خواهد کرد.`)) {
        this.loadingUsers = true; // Use main table loader
        try {
          await adminService.deleteVpnUser(marzbanUsername);
          await this.fetchVpnUsers();
        } catch (err) {
          this.usersError = `خطا در حذف کاربر '${marzbanUsername}': ` + (err.response?.data?.detail || err.message);
          this.loadingUsers = false;
        }
      }
    },
    async confirmResetTraffic(marzbanUsername) {
      if (window.confirm(`آیا از ریست کردن ترافیک کاربر '${marzbanUsername}' اطمینان دارید؟`)) {
        this.loadingUsers = true; // Use main table loader
        try {
          await adminService.resetVpnUserTraffic(marzbanUsername);
          await this.fetchVpnUsers(); // Refresh to see updated status/usage
        } catch (err) {
          this.usersError = `خطا در ریست ترافیک کاربر '${marzbanUsername}': ` + (err.response?.data?.detail || err.message);
           this.loadingUsers = false;
        }
      }
    },
    async fetchUserDetailsAndShowSubscription(marzbanUsername) {
        this.currentSubscriptionInfo = { marzban_username, subscription_url: '', raw_links: [] };
        this.subscriptionError = null;
        this.loadingSubscription = true;
        this.showSubscriptionModal = true;
        try {
            const response = await adminService.getVpnUserSubscriptionInfo(marzbanUsername);
            this.currentSubscriptionInfo = response.data;
        } catch (err) {
            this.subscriptionError = `خطا در دریافت اطلاعات اتصال: ` + (err.response?.data?.detail || err.message);
        } finally {
            this.loadingSubscription = false;
        }
    },
    closeSubscriptionModal() {
        this.showSubscriptionModal = false;
    },
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            alert('لینک کپی شد!'); // Replace with a more elegant notification later
        } catch (err) {
            alert('خطا در کپی کردن لینک.');
            console.error('Failed to copy: ', err);
        }
    }
  },
  async created() {
    await this.fetchActivePlans(); // Fetch plans once when component is created for the creation modal
    await this.fetchVpnUsers();
  },
};
</script>

<style scoped>
/* Using styles similar to SAManageAdmins/SAManagePlans for consistency */
.admin-manage-users {
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
.content-header h3 { margin: 0; font-size: 1.8em; color: #333; }

.btn {
  padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; font-size: 0.95em;
  transition: background-color 0.2s ease, box-shadow 0.2s ease; text-decoration: none;
  display: inline-block; text-align: center;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-info { background-color: #17a2b8; color: white; }
.btn-info:hover { background-color: #117a8b; }
.btn-warning { background-color: #ffc107; color: #212529; }
.btn-warning:hover { background-color: #e0a800; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-success { background-color: #28a745; color: white; }
.btn-success:hover { background-color: #1e7e34; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #545b62; }
.btn-sm { padding: 5px 10px; font-size: 0.85em; margin: 0 3px; }
.btn-outline-secondary {
    background-color: transparent;
    border: 1px solid #6c757d;
    color: #6c757d;
}
.btn-outline-secondary:hover {
    background-color: #6c757d;
    color: white;
}


.loading-indicator, .empty-state, .error-message {
  text-align: center; padding: 20px; font-size: 1.1em; color: #555;
}
.error-message { color: #e74c3c; background-color: #fdd; border: 1px solid #fbb; border-radius: 5px; margin-bottom: 15px; }

.styled-table {
  width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.9em; /* Slightly smaller font for more data */
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05); border-radius: 8px; overflow: hidden;
}
.styled-table thead tr { background-color: #663399; color: #ffffff; text-align: right; font-weight: bold; } /* Rebeccapurple for users */
.styled-table th, .styled-table td { padding: 10px 12px; text-align: right; } /* Slightly less padding */
.styled-table tbody tr { border-bottom: 1px solid #dddddd; }
.styled-table tbody tr:nth-of-type(even) { background-color: #f3f3f3; }
.styled-table tbody tr:last-of-type { border-bottom: 2px solid #663399; }
.styled-table tbody tr:hover { background-color: #e8e2f2; }

.status-active { color: #28a745; font-weight: bold; }
.status-inactive { color: #dc3545; font-weight: bold; }

/* Modal Styles */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.6); display: flex;
  justify-content: center; align-items: center; z-index: 1000; direction: rtl;
}
.modal-content {
  background-color: white; padding: 25px 30px; border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.2); width: 90%;
  max-width: 550px; max-height: 90vh; overflow-y: auto;
}
.modal-content h4 { font-size: 1.6em; margin-top: 0; margin-bottom: 20px; color: #333; text-align: center; }
.form-group { margin-bottom: 18px; text-align: right; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; color: #444; }
.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.form-group input[type="number"],
.form-group select,
.form-group textarea {
  width: 100%; padding: 10px 12px; border: 1px solid #ccc;
  border-radius: 5px; box-sizing: border-box; font-size: 1em;
}
.form-group textarea { resize: vertical; min-height: 80px; }
.form-group small { font-size: 0.85em; color: #6c757d; display: block; margin-top: 4px;}
.modal-error { margin-top: 0; margin-bottom: 15px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; }

.subscription-modal-content {
    max-width: 600px; /* Wider for QR code and links */
}
.sub-link-input {
    direction: ltr; /* Links are usually LTR */
    margin-bottom: 10px;
}
.raw-link-input {
    font-size: 0.9em;
    padding: 6px 10px;
    width: calc(100% - 70px); /* Adjust width to make space for copy button */
    display: inline-block;
}
.subscription-modal-content .form-group label{
    margin-bottom: 8px;
}
.qr-code-container {
    text-align: center;
    margin: 15px 0;
}
.qr-code-container p {
    margin-bottom: 5px;
    font-weight: bold;
}
.raw-links-container {
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 15px;
}
.raw-links-container h5 {
    margin-bottom: 10px;
}
.raw-links-container ul {
    list-style: none;
    padding: 0;
}
.raw-links-container li {
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 5px;
}
</style>
