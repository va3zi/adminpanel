import apiClient from '../../services/apiClient'; // Import the centralized client

const state = {
  token: localStorage.getItem('superadmin_token') || null, // Or a more generic 'auth_token'
  user: JSON.parse(localStorage.getItem('superadmin_user_info')) || null, // e.g., { username: '...', role: 'superadmin' }
  // userRole will determine if this is a superadmin or admin session
  // For now, we assume this module is primarily for SuperAdmin, but it can be generalized
  userRole: localStorage.getItem('user_role') || null, // 'superadmin' or 'admin'
};

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  userRole: state => state.userRole,
  authHeaders: state => {
    return state.token ? { Authorization: `Bearer ${state.token}` } : {};
  }
};

const mutations = {
  SET_TOKEN(state, { token, userType }) {
    state.token = token;
    state.userRole = userType; // 'superadmin' or 'admin'
    localStorage.setItem(`${userType}_token`, token); // e.g. superadmin_token or admin_token
    localStorage.setItem('user_role', userType);
  },
  CLEAR_AUTH(state) {
    const userType = state.userRole; // Get user type before clearing
    localStorage.removeItem(`${userType}_token`);
    localStorage.removeItem(`${userType}_user_info`);
    localStorage.removeItem('user_role');

    state.token = null;
    state.user = null;
    state.userRole = null;
  },
  SET_USER(state, { userInfo, userType }) {
    state.user = userInfo;
    localStorage.setItem(`${userType}_user_info`, JSON.stringify(userInfo));
  }
};

const actions = {
  // SuperAdmin Login Action
  async loginSuperAdmin({ commit, dispatch }, credentials) {
    try {
      // FastAPI's OAuth2PasswordRequestForm expects form data
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      // Use the apiClient which has the base URL pre-configured
      const response = await apiClient.post(`/superadmin/login/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const token = response.data.access_token;
      commit('SET_TOKEN', { token, userType: 'superadmin' });

      // After getting token, fetch superadmin details
      await dispatch('fetchSuperAdminMe', token);
      return Promise.resolve();
    } catch (error) {
      commit('CLEAR_AUTH'); // Clear any partial auth state
      console.error("SuperAdmin login error:", error.response ? error.response.data : error.message);
      return Promise.reject(error.response ? error.response.data : error);
    }
  },

  async fetchSuperAdminMe({ commit, state }, tokenToUse) {
    const currentToken = tokenToUse || state.token;
    if (!currentToken) return Promise.reject("No token available for fetchSuperAdminMe");
    try {
      // The interceptor in apiClient will add the token header automatically
      const response = await apiClient.get(`/superadmin/me`);
      commit('SET_USER', { userInfo: response.data, userType: 'superadmin' });
      return Promise.resolve(response.data);
    } catch (error) {
      // If fetching user fails (e.g. token expired), clear auth
      commit('CLEAR_AUTH');
      console.error("Fetch SuperAdmin Me error:", error.response ? error.response.data : error.message);
      return Promise.reject(error.response ? error.response.data : error);
    }
  },

  // General Logout Action
  logout({ commit, state }) {
    // Here you could also make an API call to invalidate the token on the server if supported
    const userType = state.userRole;
    commit('CLEAR_AUTH');
    // Redirect to appropriate login page based on userType, handled by router guard or component
    // For example, if router is available: router.push(`/${userType}/login`);
    return Promise.resolve(userType); // return userType to help redirect
  },

  // Action to initialize auth state from localStorage (e.g., on app load)
  async initializeAuth({ dispatch, state }) {
    if (state.token && state.userRole === 'superadmin') {
      // Validate token by fetching user data
      try {
        await dispatch('fetchSuperAdminMe', state.token);
      } catch (error) {
        // Token might be invalid or expired, already cleared by fetchSuperAdminMe
        console.log("Token validation failed during init, auth cleared.");
      }
    }
    // Add similar logic for 'admin' role when implemented
  }

};

export default {
  namespaced: true, // Important for modular Vuex stores
  state,
  getters,
  mutations,
  actions
};
