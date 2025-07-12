import axios from 'axios';
import store from '../../store'; // Adjusted path to root store

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Function to get the auth headers for the currently logged-in user (admin or superadmin)
const getAuthHeaders = () => {
  const token = store.getters['auth/token'];
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
};

// Create an apiClient instance.
// If you have a global one, you might not need this, but for modularity:
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the token dynamically
apiClient.interceptors.request.use(config => {
  const headers = getAuthHeaders();
  // Ensure the prefix for admin routes is /admin
  // This service is for /admin/... routes, so the base URL should be sufficient if it points to /api/v1
  // The specific endpoints like /admin/vpnusers will be appended.
  config.headers = { ...config.headers, ...headers };
  return config;
}, error => {
  return Promise.reject(error);
});


export default {
  // VPN User Management by Admin
  getVpnUsers(skip = 0, limit = 100) {
    return apiClient.get(`/admin/vpnusers/?skip=${skip}&limit=${limit}`);
  },

  createVpnUser(vpnUserData) {
    // vpnUserData: { marzban_username, plan_id, notes (optional) }
    return apiClient.post('/admin/vpnusers/', vpnUserData);
  },

  getVpnUserDetails(marzbanUsername) {
    // This endpoint in backend returns VpnUserWithMarzbanDetails
    return apiClient.get(`/admin/vpnusers/${marzbanUsername}`);
  },

  deleteVpnUser(marzbanUsername) {
    return apiClient.delete(`/admin/vpnusers/${marzbanUsername}`);
  },

  resetVpnUserTraffic(marzbanUsername) {
    return apiClient.post(`/admin/vpnusers/${marzbanUsername}/reset-traffic`);
  },

  getVpnUserSubscriptionInfo(marzbanUsername) {
    // Returns { marzban_username, subscription_url, raw_links }
    return apiClient.get(`/admin/vpnusers/${marzbanUsername}/subscription-info`);
  },

  // Plans (Admin viewing active plans)
  getActivePlans() {
    return apiClient.get('/admin/plans');
  },

  // Payment
  requestPayment(amount) {
    return apiClient.post('/admin/payments/request', { amount });
  }
};
