<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const editingSessionId = ref(null)
const editingTitle = ref('')
const editInput = ref(null)

onMounted(() => {
  chatStore.loadSessions()
})

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return 'Heute'
  } else if (diffDays === 1) {
    return 'Gestern'
  } else if (diffDays < 7) {
    return `Vor ${diffDays} Tagen`
  } else {
    return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
  }
}

function truncateTitle(title, maxLength = 30) {
  if (title.length <= maxLength) return title
  return title.slice(0, maxLength) + '...'
}

async function selectSession(sessionId) {
  await chatStore.loadSession(sessionId)
}

function handleDelete(event, sessionId) {
  event.stopPropagation()
  if (confirm('Diese Unterhaltung wirklich loeschen?')) {
    chatStore.deleteSession(sessionId)
  }
}

function startEditing(event, session) {
  event.stopPropagation()
  editingSessionId.value = session.id
  editingTitle.value = session.title
  nextTick(() => {
    if (editInput.value) {
      editInput.value.focus()
      editInput.value.select()
    }
  })
}

async function saveEdit() {
  if (editingSessionId.value && editingTitle.value.trim()) {
    await chatStore.renameSession(editingSessionId.value, editingTitle.value.trim())
  }
  cancelEdit()
}

function cancelEdit() {
  editingSessionId.value = null
  editingTitle.value = ''
}

function handleEditKeydown(event) {
  if (event.key === 'Enter') {
    saveEdit()
  } else if (event.key === 'Escape') {
    cancelEdit()
  }
}
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 h-full flex flex-col">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
      <h3 class="font-medium text-gray-900">Verlauf</h3>
      <button
        @click="chatStore.startNewChat()"
        class="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Neu
      </button>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="chatStore.sessionsLoading" class="p-4 text-center text-gray-500">
        <svg class="w-5 h-5 mx-auto animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
      </div>

      <div v-else-if="chatStore.sessions.length === 0" class="p-4 text-center text-gray-500 text-sm">
        Keine Unterhaltungen
      </div>

      <div v-else class="py-2">
        <button
          v-for="session in chatStore.sessions"
          :key="session.id"
          @click="selectSession(session.id)"
          :class="[
            'w-full px-4 py-2.5 text-left hover:bg-gray-50 transition-colors group flex items-start gap-2',
            chatStore.currentSessionId === session.id ? 'bg-blue-50' : ''
          ]"
        >
          <svg class="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <div class="flex-1 min-w-0">
            <!-- Edit mode -->
            <div v-if="editingSessionId === session.id" class="flex items-center gap-1">
              <input
                ref="editInput"
                v-model="editingTitle"
                @keydown="handleEditKeydown"
                @blur="saveEdit"
                @click.stop
                class="text-sm text-gray-900 w-full px-1 py-0.5 border border-blue-400 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <!-- Display mode -->
            <template v-else>
              <div class="text-sm text-gray-900 truncate">
                {{ truncateTitle(session.title) }}
              </div>
              <div class="text-xs text-gray-500 flex items-center gap-2">
                <span>{{ formatDate(session.updated_at) }}</span>
                <span class="text-gray-300">|</span>
                <span>{{ session.message_count }} Nachrichten</span>
              </div>
            </template>
          </div>
          <!-- Edit button -->
          <button
            v-if="editingSessionId !== session.id"
            @click="startEditing($event, session)"
            class="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-all"
            title="Umbenennen"
          >
            <svg class="w-4 h-4 text-gray-400 hover:text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <!-- Delete button -->
          <button
            v-if="editingSessionId !== session.id"
            @click="handleDelete($event, session.id)"
            class="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-all"
            title="Loeschen"
          >
            <svg class="w-4 h-4 text-gray-400 hover:text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </button>
      </div>
    </div>
  </div>
</template>
