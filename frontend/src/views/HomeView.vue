<script setup>
import { ref, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatWindow from '@/components/ChatWindow.vue'
import ChatHistory from '@/components/ChatHistory.vue'
import SourceList from '@/components/SourceList.vue'
import ObjectInspector from '@/components/ObjectInspector.vue'
import ImpactTable from '@/components/ImpactTable.vue'

const chatStore = useChatStore()
const activeTab = ref('sources')
const selectedImpact = ref(null)

onMounted(() => {
  chatStore.loadExamples()
  chatStore.loadSessions()
})

function showImpact(type, id) {
  selectedImpact.value = { type, id }
  activeTab.value = 'impact'
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-6">
    <div class="grid grid-cols-12 gap-6">
      <!-- Chat History Sidebar -->
      <div class="col-span-12 lg:col-span-2">
        <div class="h-[calc(100vh-180px)]">
          <ChatHistory />
        </div>
      </div>

      <!-- Main Chat Area -->
      <div class="col-span-12 lg:col-span-5">
        <ChatWindow @show-impact="showImpact" />
      </div>

      <!-- Side Panel -->
      <div class="col-span-12 lg:col-span-5">
        <!-- Tab Navigation -->
        <div class="bg-white rounded-t-lg border border-b-0 border-gray-200">
          <nav class="flex">
            <button
              @click="activeTab = 'sources'"
              :class="[
                'flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'sources'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Quellen
            </button>
            <button
              @click="activeTab = 'objects'"
              :class="[
                'flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'objects'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Objekte
            </button>
            <button
              @click="activeTab = 'impact'"
              :class="[
                'flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'impact'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              ]"
            >
              Impact
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="bg-white rounded-b-lg border border-gray-200 min-h-[500px]">
          <SourceList
            v-if="activeTab === 'sources'"
            :sources="chatStore.currentSources"
          />
          <ObjectInspector
            v-else-if="activeTab === 'objects'"
            :objects="chatStore.currentObjects"
            @show-impact="showImpact"
          />
          <ImpactTable
            v-else-if="activeTab === 'impact'"
            :selected="selectedImpact"
          />
        </div>
      </div>
    </div>
  </div>
</template>
