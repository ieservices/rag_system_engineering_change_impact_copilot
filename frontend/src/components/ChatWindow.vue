<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'

const emit = defineEmits(['show-impact'])
const chatStore = useChatStore()
const messageInput = ref('')
const messagesContainer = ref(null)

async function sendMessage() {
  const content = messageInput.value.trim()
  if (!content || chatStore.isLoading) return

  messageInput.value = ''
  await chatStore.sendMessage(content)

  await nextTick()
  scrollToBottom()
}

function selectExample(query) {
  messageInput.value = query
  sendMessage()
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

watch(() => chatStore.messages.length, () => {
  nextTick(scrollToBottom)
})

function getConfidenceClass(confidence) {
  if (confidence >= 0.7) return 'confidence-high'
  if (confidence >= 0.4) return 'confidence-medium'
  return 'confidence-low'
}

function formatConfidence(confidence) {
  return Math.round(confidence * 100)
}
</script>

<template>
  <div class="card h-[calc(100vh-180px)] flex flex-col">
    <!-- Header -->
    <div class="card-header flex items-center justify-between">
      <span>Chat</span>
      <button
        v-if="chatStore.messages.length > 0"
        @click="chatStore.clearChat()"
        class="text-sm text-gray-500 hover:text-gray-700"
      >
        Neuer Chat
      </button>
    </div>

    <!-- Messages Area -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4"
    >
      <!-- Welcome message when empty -->
      <div v-if="chatStore.messages.length === 0" class="text-center py-8">
        <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Engineering Change Impact Copilot</h3>
        <p class="text-gray-500 mb-6">
          Stellen Sie Fragen zu Komponenten, Dokumenten und technischen Änderungen.
        </p>

        <!-- Example queries -->
        <div class="space-y-2">
          <p class="text-sm text-gray-500 mb-2">Beispiele:</p>
          <div class="flex flex-wrap justify-center gap-2">
            <button
              v-for="example in chatStore.exampleQueries.slice(0, 4)"
              :key="example"
              @click="selectExample(example)"
              class="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-full text-gray-700 transition-colors"
            >
              {{ example.length > 50 ? example.slice(0, 50) + '...' : example }}
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div
        v-for="(message, index) in chatStore.messages"
        :key="index"
        :class="['chat-message', message.role]"
      >
        <div class="flex items-start gap-3">
          <!-- Avatar -->
          <div
            :class="[
              'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
              message.role === 'user' ? 'bg-blue-100' : 'bg-gray-200'
            ]"
          >
            <svg v-if="message.role === 'user'" class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
            </svg>
            <svg v-else class="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>

          <!-- Content -->
          <div class="flex-1">
            <div class="whitespace-pre-wrap">{{ message.content }}</div>

            <!-- Confidence indicator for assistant -->
            <div v-if="message.role === 'assistant' && message.confidence" class="mt-3">
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-500">Konfidenz:</span>
                <div class="confidence-meter w-24">
                  <div
                    :class="['confidence-fill', getConfidenceClass(message.confidence)]"
                    :style="{ width: formatConfidence(message.confidence) + '%' }"
                  ></div>
                </div>
                <span class="text-xs text-gray-600">{{ formatConfidence(message.confidence) }}%</span>
              </div>
            </div>

            <!-- Sources hint -->
            <div
              v-if="message.role === 'assistant' && message.sources?.length"
              class="mt-2 text-xs text-gray-500"
            >
              {{ message.sources.length }} Quelle(n) gefunden
            </div>
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="chatStore.isLoading" class="chat-message assistant">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
            <svg class="w-4 h-4 text-gray-600 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          </div>
          <div class="text-gray-500">
            Analysiere<span class="loading-dots"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-gray-200 p-4">
      <form @submit.prevent="sendMessage" class="flex gap-3">
        <input
          v-model="messageInput"
          type="text"
          placeholder="Stellen Sie eine Frage..."
          :disabled="chatStore.isLoading"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
        />
        <button
          type="submit"
          :disabled="!messageInput.trim() || chatStore.isLoading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>
