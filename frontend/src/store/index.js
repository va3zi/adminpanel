import { createStore } from 'vuex'
import auth from './modules/auth'
// Import other modules as needed, e.g., superadmin, admin specific stores

export default createStore({
  modules: {
    auth
    // superadmin,
    // admin
  },
  // Global state, getters, mutations, actions can also be defined here if not module-specific
  // For example, global loading state or notifications
  state: {
    // appLoading: false
  },
  getters: {
    // isAppLoading: state => state.appLoading
  },
  mutations: {
    // SET_APP_LOADING(state, isLoading) {
    //   state.appLoading = isLoading;
    // }
  },
  actions: {
    // asyncinitializeApp({ commit }) {
    //   commit('SET_APP_LOADING', true);
    //   // ... any async app init logic
    //   commit('SET_APP_LOADING', false);
    // }
  }
})
