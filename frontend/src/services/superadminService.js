import apiClient from './apiClient';

export default {
  // Admins Management
  getAdmins(skip = 0, limit = 100) {
    return apiClient.get(`/admins/?skip=${skip}&limit=${limit}`);
  },

  getAdmin(adminId) {
    return apiClient.get(`/admins/${adminId}`);
  },

  createAdmin(adminData) {
    // adminData expected: { username, email, password, balance (optional), is_active (optional) }
    return apiClient.post('/admins/', adminData);
  },

  updateAdmin(adminId, adminData) {
    // adminData expected: { username (optional), email (optional), balance (optional), is_active (optional) }
    // Password updates should be handled separately if needed.
    return apiClient.put(`/admins/${adminId}`, adminData);
  },

  deleteAdmin(adminId) {
    return apiClient.delete(`/admins/${adminId}`);
  },

  // Plans Management
  getPlans(skip = 0, limit = 100) {
    return apiClient.get(`/plans/?skip=${skip}&limit=${limit}`);
  },

  getPlan(planId) {
    return apiClient.get(`/plans/${planId}`);
  },

  createPlan(planData) {
    // planData: { name, price, duration_days, data_limit_gb, is_active (optional) }
    return apiClient.post('/plans/', planData);
  },

  updatePlan(planId, planData) {
    // planData: similar to create, all fields optional for update
    return apiClient.put(`/plans/${planId}`, planData);
  },

  deletePlan(planId) {
    return apiClient.delete(`/plans/${planId}`);
  }
};
