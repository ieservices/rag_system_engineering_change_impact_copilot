/* jshint esversion: 11 */
import { createRouter, createWebHistory } from 'vue-router';

var routes = [
  {
    path: '/',
    name: 'home',
    component: function() { return import('@/views/HomeView.vue'); }
  },
  {
    path: '/admin',
    name: 'admin',
    component: function() { return import('@/views/AdminView.vue'); }
  },
  {
    path: '/docs',
    name: 'docs',
    component: function() { return import('@/views/DocsView.vue'); }
  }
];

var router = createRouter({
  history: createWebHistory(),
  routes: routes
});

export default router;
