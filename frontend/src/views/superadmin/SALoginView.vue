<template>
  <div class="login-container sa-login-container">
    <div class="login-box">
      <h2>ورود مدیریت کل (Super Admin)</h2>
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
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'SALoginView',
  data() {
    return {
      username: '',
      password: '',
      error: null,
      loading: false,
    };
  },
  methods: {
    ...mapActions('auth', ['loginSuperAdmin']),
    async handleLogin() {
      this.loading = true;
      this.error = null;
      try {
        await this.loginSuperAdmin({ username: this.username, password: this.password });
        this.$router.push({ name: 'SuperAdminDashboard' });
      } catch (err) {
        this.error = err.detail || 'نام کاربری یا رمز عبور اشتباه است.';
        if (err.non_field_errors) { // Django-style errors
            this.error = err.non_field_errors.join(" ");
        } else if (err.detail) { // FastAPI style errors
            this.error = err.detail;
        } else if (err.message) {
            this.error = err.message;
        } else {
            this.error = 'خطا در ورود. لطفاً دوباره تلاش کنید.';
        }
        console.error("Login failed:", err);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh; /* Adjust as needed */
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
  background-color: #3498db; /* Primary blue */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1.1em;
  font-weight: bold;
  transition: background-color 0.3s ease;
}

.login-button:hover {
  background-color: #2980b9; /* Darker blue */
}

.login-button:disabled {
  background-color: #a0c4e0;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c; /* Red */
  margin-top: 15px;
  text-align: center;
  font-size: 0.9em;
}

/* Specific styles for SA login if needed, e.g. different color scheme */
.sa-login-container .login-button {
  background-color: #2c3e50; /* Darker color for SA */
}
.sa-login-container .login-button:hover {
  background-color: #1a252f;
}
</style>
