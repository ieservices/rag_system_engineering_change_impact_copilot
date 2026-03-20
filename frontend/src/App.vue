<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <svg class="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          <h1 class="text-xl font-semibold text-gray-900">Engineering Change Impact Copilot</h1>
        </div>

        <nav class="flex items-center space-x-6">
          <RouterLink
            to="/"
            class="text-gray-600 hover:text-gray-900 font-medium"
            :class="{ 'text-blue-600': $route.path === '/' }"
          >
            Chat
          </RouterLink>
          <RouterLink
            to="/admin"
            class="text-gray-600 hover:text-gray-900 font-medium"
            :class="{ 'text-blue-600': $route.path === '/admin' }"
          >
            Admin
          </RouterLink>
          <RouterLink
            to="/docs"
            class="text-gray-600 hover:text-gray-900 font-medium"
            :class="{ 'text-blue-600': $route.path === '/docs' }"
          >
            Dokumentation
          </RouterLink>
        </nav>
      </div>
    </header>

    <!-- Main Content -->
    <main>
      <RouterView />
    </main>
  </div>
</template>
