<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  selected: {
    type: Object,
    default: null
  }
})

const loading = ref(false)
const impactData = ref(null)
const error = ref(null)

watch(() => props.selected, async (newVal) => {
  if (!newVal) {
    impactData.value = null
    return
  }

  loading.value = true
  error.value = null

  try {
    const endpoint = newVal.type === 'part'
      ? `/api/parts/${newVal.id}/impact`
      : `/api/assemblies/${newVal.id}/impact`

    const response = await axios.get(endpoint)
    impactData.value = response.data
  } catch (e) {
    error.value = 'Fehler beim Laden der Impact-Analyse'
    console.error(e)
  } finally {
    loading.value = false
  }
}, { immediate: true })

function getStatusClass(status) {
  return `status-${status?.toLowerCase() || 'draft'}`
}
</script>

<template>
  <div class="p-4">
    <!-- Empty state -->
    <div v-if="!selected && !impactData" class="text-center py-12">
      <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      <p class="text-gray-500">Keine Impact-Analyse ausgewählt</p>
      <p class="text-sm text-gray-400">Klicken Sie auf ein Objekt, um dessen Auswirkungen zu sehen.</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="text-center py-12">
      <svg class="w-8 h-8 mx-auto text-blue-500 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
      </svg>
      <p class="text-gray-500 mt-3">Lade Impact-Analyse...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12">
      <svg class="w-12 h-12 mx-auto text-red-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-red-500">{{ error }}</p>
    </div>

    <!-- Impact Data -->
    <div v-else-if="impactData" class="space-y-4">
      <!-- Header -->
      <div class="bg-blue-50 rounded-lg p-3">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span class="font-medium text-blue-900">Impact-Analyse</span>
        </div>
        <p class="text-sm text-blue-700 mt-1">
          {{ selected.type === 'part' ? 'Teil' : 'Baugruppe' }}:
          <strong>{{ selected.id }}</strong>
        </p>
      </div>

      <!-- Part Impact -->
      <template v-if="selected.type === 'part' && impactData.part">
        <!-- Affected Assemblies -->
        <div v-if="impactData.affected_assemblies?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Betroffene Baugruppen</h4>
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-2 py-1 text-left">Nummer</th>
                <th class="px-2 py-1 text-left">Name</th>
                <th class="px-2 py-1 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="asm in impactData.affected_assemblies" :key="asm.assembly_number" class="border-t">
                <td class="px-2 py-1 font-medium">{{ asm.assembly_number }}</td>
                <td class="px-2 py-1">{{ asm.name }}</td>
                <td class="px-2 py-1">
                  <span :class="['status-badge text-xs', getStatusClass(asm.status)]">
                    {{ asm.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Related Documents -->
        <div v-if="impactData.related_documents?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Verknüpfte Dokumente</h4>
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-2 py-1 text-left">Nummer</th>
                <th class="px-2 py-1 text-left">Titel</th>
                <th class="px-2 py-1 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in impactData.related_documents" :key="doc.document_number" class="border-t">
                <td class="px-2 py-1 font-medium">{{ doc.document_number }}</td>
                <td class="px-2 py-1">{{ doc.title }}</td>
                <td class="px-2 py-1">
                  <span :class="['status-badge text-xs', getStatusClass(doc.status)]">
                    {{ doc.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Change Requests -->
        <div v-if="impactData.change_requests?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Offene Änderungsanträge</h4>
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-2 py-1 text-left">CR</th>
                <th class="px-2 py-1 text-left">Titel</th>
                <th class="px-2 py-1 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cr in impactData.change_requests" :key="cr.cr_number" class="border-t">
                <td class="px-2 py-1 font-medium">{{ cr.cr_number }}</td>
                <td class="px-2 py-1">{{ cr.title }}</td>
                <td class="px-2 py-1">
                  <span :class="['status-badge text-xs', getStatusClass(cr.status)]">
                    {{ cr.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- Assembly Impact -->
      <template v-else-if="selected.type === 'assembly' && impactData.assembly">
        <!-- Parts in Assembly -->
        <div v-if="impactData.parts?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Enthaltene Teile</h4>
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-2 py-1 text-left">Teil</th>
                <th class="px-2 py-1 text-left">Name</th>
                <th class="px-2 py-1 text-left">Material</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="part in impactData.parts" :key="part.part_number" class="border-t">
                <td class="px-2 py-1 font-medium">{{ part.part_number }}</td>
                <td class="px-2 py-1">{{ part.name }}</td>
                <td class="px-2 py-1 text-xs">{{ part.material }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Parent Assemblies -->
        <div v-if="impactData.parent_assemblies?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Übergeordnete Baugruppen</h4>
          <div class="space-y-1">
            <div v-for="parent in impactData.parent_assemblies" :key="parent.assembly_number"
                 class="text-sm p-2 bg-gray-50 rounded">
              <span class="font-medium">{{ parent.assembly_number }}</span>
              <span class="text-gray-500"> - {{ parent.name }}</span>
            </div>
          </div>
        </div>

        <!-- Related Documents -->
        <div v-if="impactData.related_documents?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Verknüpfte Dokumente</h4>
          <table class="w-full text-sm">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-2 py-1 text-left">Nummer</th>
                <th class="px-2 py-1 text-left">Titel</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in impactData.related_documents" :key="doc.document_number" class="border-t">
                <td class="px-2 py-1 font-medium">{{ doc.document_number }}</td>
                <td class="px-2 py-1">{{ doc.title }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Change Requests -->
        <div v-if="impactData.change_requests?.length > 0">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Offene Änderungsanträge</h4>
          <div class="space-y-1">
            <div v-for="cr in impactData.change_requests" :key="cr.cr_number"
                 class="text-sm p-2 bg-yellow-50 rounded border border-yellow-200">
              <span class="font-medium">{{ cr.cr_number }}</span>
              <span class="text-gray-600"> - {{ cr.title }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- No impacts found -->
      <div v-if="!impactData.affected_assemblies?.length &&
                 !impactData.related_documents?.length &&
                 !impactData.change_requests?.length &&
                 !impactData.parts?.length"
           class="text-center py-6 text-gray-500">
        Keine Auswirkungen gefunden.
      </div>
    </div>
  </div>
</template>
