import apiClient from './apiClient';

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
