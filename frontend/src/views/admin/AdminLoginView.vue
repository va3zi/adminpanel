<template>
  <div class="login-container admin-login-container">
    <div class="login-box">
      <h2>ورود ادمین</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">نام کاربری:</label>
          <input type="text" id="username" v-model="username" required autofocus />
        </div>
        <div class="input-group">
          <label for="password">رمز عبور:</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <button type="submit" class="login-button" :disabled="loading">
          <span v-if="loading">در حال ورود...</span>
          <span v-else>ورود</span>
        </button>
        <p v-if="error" class="error-message">{{ error }}</p>
      </form>
      <!-- Optional: Link to SuperAdmin login or other pages -->
      <!-- <div class="extra-links">
        <router-link :to="{ name: 'SuperAdminLogin'}">ورود مدیریت کل</router-link>
      </div> -->
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'AdminLoginView',
  data() {
    return {
      username: '',
      password: '',
      error: null,
      loading: false,
    };
  },
  methods: {
    ...mapActions('auth', ['loginAdmin']), // Use the new loginAdmin action
    async handleLogin() {
      this.loading = true;
      this.error = null;
      try {
        await this.loginAdmin({ username: this.username, password: this.password });
        this.$router.push({ name: 'AdminDashboard' }); // Redirect to AdminDashboard
      } catch (err) {
        if (err && err.detail) {
            this.error = err.detail;
        } else if (err && err.message) {
            this.error = err.message;
        } else {
            this.error = 'خطا در ورود. لطفاً اطلاعات خود را بررسی کرده و دوباره تلاش کنید.';
        }
        console.error("Admin Login failed:", err);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* Using similar styles to SALoginView for consistency */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.login-box {
  background-color: #ffffff;
  padding: 30px 40px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: right; /* RTL */
}

.login-box h2 {
  text-align: center;
  margin-bottom: 25px;
  color: #333;
  font-size: 1.8em;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: bold;
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1em;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #17a2b8; /* Info Blue - Differentiating from SA login */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background-color: #138496; /* Darker Info Blue */
}

.login-button:disabled {
  background-color: #a0d3dc;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 15px;
  text-align: center;
  font-size: 0.9em;
}

.admin-login-container .login-button {
  /* Specific styles if needed, but already differentiated by base color */
}
.extra-links {
  text-align: center;
  margin-top: 20px;
}
.extra-links a {
  color: #007bff;
  text-decoration: none;
  font-size: 0.9em;
}
.extra-links a:hover {
  text-decoration: underline;
}
</style>
