import { mount } from '@vue/test-utils'
import PaymentSuccess from '@/views/payment/PaymentSuccess.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createStore } from 'vuex'

// Mock Vuex store
const createMockStore = () => {
  return createStore({
    modules: {
      auth: {
        namespaced: true,
        actions: {
          fetchAdminMe: jest.fn(), // Mock the action
        },
      },
    },
  });
};

// Mock router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'AdminDashboard', component: { template: '<div>Dashboard</div>' } },
    { path: '/payment/success', name: 'PaymentSuccess', component: PaymentSuccess },
  ],
});

describe('PaymentSuccess.vue', () => {
  it('renders a success message', async () => {
    // Navigate to the route to be able to read query params
    await router.push('/payment/success');

    const store = createMockStore();

    const wrapper = mount(PaymentSuccess, {
      global: {
        plugins: [router, store],
      },
    });

    expect(wrapper.find('h2').text()).toContain('پرداخت موفق');
    expect(wrapper.find('p').text()).toContain('حساب شما با موفقیت شارژ شد');
  });

  it('displays the reference ID from the route query', async () => {
    const refId = 'TEST12345';
    await router.push(`/payment/success?ref_id=${refId}`);

    const store = createMockStore();

    const wrapper = mount(PaymentSuccess, {
      global: {
        plugins: [router, store],
      },
    });

    // Ensure the component has processed the route update
    await wrapper.vm.$nextTick();

    const refIdElement = wrapper.find('.ref-id');
    expect(refIdElement.exists()).toBe(true);
    expect(refIdElement.text()).toContain(refId);
  });

  it('dispatches fetchAdminMe action on creation', async () => {
    await router.push('/payment/success');
    const store = createMockStore();

    // Spy on the dispatch method before mounting
    const dispatchSpy = jest.spyOn(store, 'dispatch');

    mount(PaymentSuccess, {
      global: {
        plugins: [router, store],
      },
    });

    expect(dispatchSpy).toHaveBeenCalledWith('auth/fetchAdminMe');
  });
});
