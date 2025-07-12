import { mount } from '@vue/test-utils';
import AdminLoginView from '@/views/admin/AdminLoginView.vue';
import { createStore } from 'vuex';
import { createRouter, createWebHistory } from 'vue-router';

// Mock the router
const mockRouter = {
  push: jest.fn(),
};

// Mock Vuex store
const createMockStore = (loginAction) => {
  return createStore({
    modules: {
      auth: {
        namespaced: true,
        actions: {
          loginAdmin: loginAction,
        },
      },
    },
  });
};

describe('AdminLoginView.vue', () => {
  it('updates username and password data on input', async () => {
    const store = createMockStore(jest.fn());
    const wrapper = mount(AdminLoginView, {
      global: {
        plugins: [store],
        mocks: {
          $router: mockRouter,
        },
      },
    });

    const usernameInput = wrapper.find('input#username');
    const passwordInput = wrapper.find('input#password');

    await usernameInput.setValue('testuser');
    await passwordInput.setValue('testpass');

    expect(wrapper.vm.username).toBe('testuser');
    expect(wrapper.vm.password).toBe('testpass');
  });

  it('calls loginAdmin action and redirects on successful login', async () => {
    // Mock a successful login action
    const loginAdminSuccess = jest.fn().mockResolvedValue();
    const store = createMockStore(loginAdminSuccess);

    const wrapper = mount(AdminLoginView, {
      global: {
        plugins: [store],
        mocks: {
          $router: mockRouter,
        },
      },
    });

    // Set input values
    await wrapper.find('input#username').setValue('testuser');
    await wrapper.find('input#password').setValue('testpass');

    // Trigger form submission
    await wrapper.find('form').trigger('submit.prevent');

    // Check if the action was called with correct credentials
    expect(loginAdminSuccess).toHaveBeenCalledWith(expect.any(Object), { // First argument is Vuex context
      username: 'testuser',
      password: 'testpass',
    });

    // Wait for async operations to complete
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick(); // May need multiple ticks for all promises to resolve

    // Check if router was called to redirect
    expect(mockRouter.push).toHaveBeenCalledWith({ name: 'AdminDashboard' });
  });

  it('displays an error message on failed login', async () => {
    // Mock a failed login action
    const loginAdminFail = jest.fn().mockRejectedValue({ detail: 'Invalid credentials' });
    const store = createMockStore(loginAdminFail);

    const wrapper = mount(AdminLoginView, {
      global: {
        plugins: [store],
        mocks: {
          $router: mockRouter,
        },
      },
    });

    // Set input values and submit
    await wrapper.find('input#username').setValue('testuser');
    await wrapper.find('input#password').setValue('wrongpass');
    await wrapper.find('form').trigger('submit.prevent');

    // Wait for async operations to complete
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();

    // Check that an error message is displayed
    const errorMessage = wrapper.find('.error-message');
    expect(errorMessage.exists()).toBe(true);
    expect(errorMessage.text()).toContain('Invalid credentials');

    // Ensure no redirect happened
    expect(mockRouter.push).not.toHaveBeenCalled();
  });
});
