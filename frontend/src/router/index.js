import { createRouter, createWebHistory } from 'vue-router';
import store from '../store'; // We'll use this for navigation guards

// SuperAdmin Views
import SALoginView from '../views/superadmin/SALoginView.vue';
import SADashboardView from '../views/superadmin/SADashboardView.vue';
// SuperAdmin Dashboard Children
import SADashboardHome from '../views/superadmin/dashboard_children/SADashboardHome.vue';
import SAManageAdmins from '../views/superadmin/dashboard_children/SAManageAdmins.vue';
import SAManagePlans from '../views/superadmin/dashboard_children/SAManagePlans.vue';

// Admin views (Import later)
import AdminLoginView from '../views/admin/AdminLoginView.vue';
import AdminDashboardView from '../views/admin/AdminDashboardView.vue';
// Admin Dashboard Children
import AdminDashboardHome from '../views/admin/dashboard_children/AdminDashboardHome.vue';
import AdminViewPlans from '../views/admin/dashboard_children/AdminViewPlans.vue';
import AdminManageUsers from '../views/admin/dashboard_children/AdminManageUsers.vue';
import AdminRecharge from '../views/admin/dashboard_children/AdminRecharge.vue';


// General Views
import NotFoundView from '../views/NotFoundView.vue';
import PaymentSuccess from '../views/payment/PaymentSuccess.vue';
import PaymentFailed from '../views/payment/PaymentFailed.vue';


const routes = [
  {
    path: '/',
    // Redirect to superadmin login if no specific role is detected, or to a general landing page if you add one
    redirect: () => {
      const userRole = store.getters['auth/userRole'];
      if (userRole === 'superadmin') {
        return { name: 'SuperAdminDashboard' };
      } else if (userRole === 'admin') {
        // return { name: 'AdminDashboard' }; // When implemented
        return { name: 'SuperAdminLogin' }; // Fallback
      }
      return { name: 'SuperAdminLogin' }; // Default redirect
    }
  },
  {
    path: '/superadmin/login',
    name: 'SuperAdminLogin',
    component: SALoginView,
    meta: { requiresGuest: true, userType: 'superadmin' }
  },
  {
    path: '/superadmin/dashboard',
    component: SADashboardView, // This is the layout component for SA dashboard
    meta: { requiresAuth: true, userType: 'superadmin' },
    // SADashboardView itself might redirect to SADashboardHome or have a default child.
    // The `name` property should ideally be on the parent for direct navigation if needed,
    // but often children are the actual targets.
    // Let's ensure SADashboardView handles its default child view or redirect.
    children: [
      {
        path: '', // Default child route for /superadmin/dashboard
        name: 'SuperAdminDashboard', // Can also be named e.g., SADashboardRedirector
        redirect: { name: 'SADashboardHome' } // Or component: SADashboardHome
      },
      {
        path: 'home',
        name: 'SADashboardHome',
        component: SADashboardHome
      },
      {
        path: 'admins',
        name: 'SAManageAdmins',
        component: SAManageAdmins
      },
      {
        path: 'plans',
        name: 'SAManagePlans',
        component: SAManagePlans
      }
      // More SA dashboard children here
    ]
  },
  // {
  //   path: '/admin/login',
  //   name: 'AdminLogin',
  //   component: AdminLoginView,
  //   meta: { requiresGuest: true, userType: 'admin' }
  // },
  // {
  //   path: '/admin/dashboard',
  //   name: 'AdminDashboard',
  //   component: AdminDashboardView,
  //   meta: { requiresAuth: true, userType: 'admin' }
  // },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLoginView,
    meta: { requiresGuest: true, userType: 'admin' }
  },
  {
    path: '/admin/dashboard',
    component: AdminDashboardView,
    meta: { requiresAuth: true, userType: 'admin' },
    children: [
      {
        path: '',
        name: 'AdminDashboard', // Default child for /admin/dashboard
        redirect: { name: 'AdminDashboardHome' }
      },
      {
        path: 'home',
        name: 'AdminDashboardHome',
        component: AdminDashboardHome
      },
      {
        path: 'plans',
        name: 'AdminViewPlans',
        component: AdminViewPlans
      },
      {
        path: 'users',
        name: 'AdminManageUsers',
        component: AdminManageUsers
      },
      {
        path: 'recharge',
        name: 'AdminRecharge',
        component: AdminRecharge
      }
    ]
  },
  // Add a catch-all route for 404
  {
    path: '/payment/success',
    name: 'PaymentSuccess',
    component: PaymentSuccess,
    // This route should be public but might benefit from requiresAuth if we want to show user-specific success messages
    // For now, keeping it simple. The backend has already updated the balance.
  },
  {
    path: '/payment/failed',
    name: 'PaymentFailed',
    component: PaymentFailed,
  },
  {
    path: '/:catchAll(.*)*',
    name: 'NotFound',
    component: NotFoundView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']; // Path to getter
  const userRole = store.getters['auth/userRole']; // Path to getter for user role/type

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // Determine where to redirect based on user type meta
      if (to.meta.userType === 'superadmin') {
        next({ name: 'SuperAdminLogin' });
      } else if (to.meta.userType === 'admin') {
        // next({ name: 'AdminLogin' }); // When admin login exists
        next({ name: 'SuperAdminLogin' }); // Fallback for now
      } else {
        next({ name: 'SuperAdminLogin' }); // Default fallback
      }
    } else {
      // Check if the authenticated user has the correct role for the route
      if (to.meta.userType && to.meta.userType !== userRole) {
        // If roles don't match, redirect to a relevant dashboard or login
        if (userRole === 'superadmin') {
          next({ name: 'SuperAdminDashboard' });
        } else if (userRole === 'admin') {
          // next({ name: 'AdminDashboard' });
          next({ name: 'SuperAdminLogin' }); // Fallback
        } else {
          next({ name: 'SuperAdminLogin' }); // Fallback
        }
      } else {
        next(); // User is authenticated and has correct role (or no role specified)
      }
    }
  } else if (to.matched.some(record => record.meta.requiresGuest)) {
    if (isAuthenticated) {
      // If trying to access login page while already logged in
      if (userRole === 'superadmin') {
        next({ name: 'SuperAdminDashboard' });
      } else if (userRole === 'admin') {
        // next({ name: 'AdminDashboard' });
        next({ name: 'SuperAdminDashboard' }); // Fallback
      } else {
        next(); // Or some default page
      }
    } else {
      next();
    }
  } else {
    next(); // Make sure to always call next()!
  }
});

export default router
