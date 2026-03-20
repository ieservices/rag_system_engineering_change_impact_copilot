<script setup>
import { computed } from 'vue'

const props = defineProps({
  objects: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['show-impact'])

const hasObjects = computed(() => {
  return (
    props.objects?.parts?.length > 0 ||
    props.objects?.assemblies?.length > 0 ||
    props.objects?.change_requests?.length > 0 ||
    props.objects?.specifications?.length > 0
  )
})

function getStatusClass(status) {
  return `status-${status?.toLowerCase() || 'draft'}`
}

function getPriorityClass(priority) {
  return `priority-${priority?.toLowerCase() || 'medium'}`
}
</script>

<template>
  <div class="p-4">
    <!-- Empty state -->
    <div v-if="!hasObjects" class="text-center py-12">
      <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <p class="text-gray-500">Keine Objekte gefunden</p>
      <p class="text-sm text-gray-400">Stellen Sie eine Frage, um relevante Objekte zu finden.</p>
    </div>

    <!-- Objects list -->
    <div v-else class="space-y-6">
      <!-- Parts -->
      <div v-if="objects.parts?.length > 0">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Teile ({{ objects.parts.length }})
        </h3>
        <div class="space-y-2">
          <div
            v-for="part in objects.parts"
            :key="part.part_number"
            @click="emit('show-impact', 'part', part.part_number)"
            class="p-2 bg-gray-50 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-sm">{{ part.part_number }}</span>
              <span :class="['status-badge text-xs', getStatusClass(part.status)]">
                {{ part.status }}
              </span>
            </div>
            <p class="text-xs text-gray-500 mt-0.5">{{ part.name }}</p>
          </div>
        </div>
      </div>

      <!-- Assemblies -->
      <div v-if="objects.assemblies?.length > 0">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          Baugruppen ({{ objects.assemblies.length }})
        </h3>
        <div class="space-y-2">
          <div
            v-for="assembly in objects.assemblies"
            :key="assembly.assembly_number"
            @click="emit('show-impact', 'assembly', assembly.assembly_number)"
            class="p-2 bg-gray-50 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-sm">{{ assembly.assembly_number }}</span>
              <span :class="['status-badge text-xs', getStatusClass(assembly.status)]">
                {{ assembly.status }}
              </span>
            </div>
            <p class="text-xs text-gray-500 mt-0.5">{{ assembly.name }}</p>
          </div>
        </div>
      </div>

      <!-- Change Requests -->
      <div v-if="objects.change_requests?.length > 0">
        <h3 class="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Änderungsanträge ({{ objects.change_requests.length }})
        </h3>
        <div class="space-y-2">
          <div
            v-for="cr in objects.change_requests"
            :key="cr.cr_number"
            class="p-2 bg-gray-50 rounded-lg"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-sm">{{ cr.cr_number }}</span>
              <span :class="['status-badge text-xs', getStatusClass(cr.status)]">
                {{ cr.status }}
              </span>
            </div>
            <p class="text-xs text-gray-500 mt-0.5">{{ cr.title }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
