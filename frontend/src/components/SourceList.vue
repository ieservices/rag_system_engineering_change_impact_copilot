<script setup>
defineProps({
  sources: {
    type: Array,
    default: () => []
  }
})

function getDocTypeLabel(type) {
  const types = {
    'SPEC': 'Spezifikation',
    'TEST': 'Prüfbericht',
    'DWG': 'Zeichnung',
    'MANUAL': 'Handbuch',
    'GENERAL': 'Dokument'
  }
  return types[type] || type
}

function getStatusClass(status) {
  return `status-${status?.toLowerCase() || 'draft'}`
}

function formatScore(score) {
  return Math.round(score * 100)
}
</script>

<template>
  <div class="p-4">
    <!-- Empty state -->
    <div v-if="sources.length === 0" class="text-center py-12">
      <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-500">Keine Quellen gefunden</p>
      <p class="text-sm text-gray-400">Stellen Sie eine Frage, um relevante Dokumente zu finden.</p>
    </div>

    <!-- Source list -->
    <div v-else class="space-y-3">
      <h3 class="text-sm font-medium text-gray-700 mb-3">
        {{ sources.length }} relevante Quelle(n)
      </h3>

      <div
        v-for="(source, index) in sources"
        :key="index"
        class="source-card"
      >
        <div class="flex items-start justify-between mb-2">
          <div>
            <span class="font-medium text-gray-900">{{ source.document_number }}</span>
            <span class="text-gray-400 mx-1">|</span>
            <span class="text-sm text-gray-500">v{{ source.version }}</span>
          </div>
          <span :class="['status-badge', getStatusClass(source.status)]">
            {{ source.status }}
          </span>
        </div>

        <p class="text-sm text-gray-700 mb-2">{{ source.title }}</p>

        <div class="flex items-center justify-between text-xs">
          <span class="text-gray-500">{{ getDocTypeLabel(source.document_type) }}</span>
          <div class="flex items-center gap-1">
            <span class="text-gray-500">Relevanz:</span>
            <div class="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-blue-500 rounded-full"
                :style="{ width: formatScore(source.score) + '%' }"
              ></div>
            </div>
            <span class="text-gray-600">{{ formatScore(source.score) }}%</span>
          </div>
        </div>

        <!-- Excerpt -->
        <div v-if="source.excerpt" class="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
          {{ source.excerpt.slice(0, 150) }}{{ source.excerpt.length > 150 ? '...' : '' }}
        </div>
      </div>
    </div>
  </div>
</template>
