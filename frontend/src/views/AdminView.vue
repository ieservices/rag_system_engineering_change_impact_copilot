<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref(null)
const loading = ref(false)
const uploading = ref(false)
const reindexing = ref(false)
const loadingDocs = ref(false)
const uploadMessage = ref(null)
const fileInput = ref(null)
const selectedFile = ref(null)
const documentType = ref('GENERAL')
const documents = ref([])
const selectedDocument = ref(null)
const documentChunks = ref([])
const loadingChunks = ref(false)
const activeTab = ref('stats')

const documentTypes = [
  { value: 'SPEC', label: 'Spezifikation' },
  { value: 'TEST', label: 'Prüfbericht' },
  { value: 'DWG', label: 'Zeichnung' },
  { value: 'MANUAL', label: 'Handbuch' },
  { value: 'GENERAL', label: 'Allgemein' }
]

onMounted(() => {
  loadStats()
  loadDocuments()
})

async function loadStats() {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/stats')
    stats.value = response.data
  } catch (e) {
    console.error('Failed to load stats:', e)
  } finally {
    loading.value = false
  }
}

function handleFileSelect(event) {
  selectedFile.value = event.target.files[0]
}

async function uploadDocument() {
  if (!selectedFile.value) return

  uploading.value = true
  uploadMessage.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('document_type', documentType.value)

    const response = await axios.post('/api/admin/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    uploadMessage.value = {
      type: 'success',
      text: `Dokument ${response.data.document_number} erfolgreich hochgeladen. ${response.data.chunks_created} Chunks erstellt.`
    }

    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    loadStats()
  } catch (e) {
    uploadMessage.value = {
      type: 'error',
      text: 'Fehler beim Hochladen: ' + (e.response?.data?.detail || e.message)
    }
  } finally {
    uploading.value = false
  }
}

async function reindexAll() {
  if (!confirm('Alle Dokumente neu indizieren? Dies kann einige Zeit dauern.')) return

  reindexing.value = true
  try {
    const response = await axios.post('/api/admin/reindex')
    uploadMessage.value = {
      type: 'success',
      text: `${response.data.documents_processed} Dokumente neu indiziert. ${response.data.chunks_created} Chunks erstellt.`
    }
    loadStats()
  } catch (e) {
    uploadMessage.value = {
      type: 'error',
      text: 'Fehler beim Re-Index: ' + (e.response?.data?.detail || e.message)
    }
  } finally {
    reindexing.value = false
  }
}

async function initDatabase() {
  try {
    await axios.post('/api/admin/init-db')
    uploadMessage.value = {
      type: 'success',
      text: 'Datenbank erfolgreich initialisiert.'
    }
    loadStats()
  } catch (e) {
    uploadMessage.value = {
      type: 'error',
      text: 'Fehler: ' + (e.response?.data?.detail || e.message)
    }
  }
}

async function loadDocuments() {
  loadingDocs.value = true
  try {
    const response = await axios.get('/api/documents/')
    documents.value = response.data
  } catch (e) {
    console.error('Failed to load documents:', e)
  } finally {
    loadingDocs.value = false
  }
}

async function viewDocument(doc) {
  selectedDocument.value = doc
  loadingChunks.value = true
  indexMessage.value = null
  try {
    const response = await axios.get(`/api/admin/chunks/${doc.id}`)
    documentChunks.value = response.data.chunks
  } catch (e) {
    console.error('Failed to load chunks:', e)
    documentChunks.value = []
  } finally {
    loadingChunks.value = false
  }
}

async function loadDataFolder() {
  uploading.value = true
  uploadMessage.value = null
  try {
    const response = await axios.post('/api/admin/load-documents')
    uploadMessage.value = {
      type: 'success',
      text: `${response.data.documents_processed} Dokumente aus data/documents geladen.`
    }
    loadStats()
    loadDocuments()
  } catch (e) {
    uploadMessage.value = {
      type: 'error',
      text: 'Fehler: ' + (e.response?.data?.detail || e.message)
    }
  } finally {
    uploading.value = false
  }
}

function closeDocumentModal() {
  selectedDocument.value = null
  documentChunks.value = []
}

const indexing = ref(false)
const indexMessage = ref(null)

async function indexDocument(docId) {
  indexing.value = true
  indexMessage.value = null
  try {
    const response = await axios.post(`/api/admin/index-document/${docId}`)
    indexMessage.value = {
      type: 'success',
      text: `${response.data.chunks_created} Chunks erstellt.`
    }
    // Reload chunks
    const chunksResponse = await axios.get(`/api/admin/chunks/${docId}`)
    documentChunks.value = chunksResponse.data.chunks
    loadStats()
  } catch (e) {
    indexMessage.value = {
      type: 'error',
      text: 'Fehler: ' + (e.response?.data?.detail || e.message)
    }
  } finally {
    indexing.value = false
  }
}

function getTypeColor(type) {
  const colors = {
    'SPEC': 'bg-blue-100 text-blue-800',
    'TEST': 'bg-green-100 text-green-800',
    'DWG': 'bg-purple-100 text-purple-800',
    'MANUAL': 'bg-orange-100 text-orange-800',
    'CR': 'bg-red-100 text-red-800',
    'GENERAL': 'bg-gray-100 text-gray-800'
  }
  return colors[type] || colors['GENERAL']
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Administration</h1>

    <!-- Tab Navigation -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="flex gap-4">
        <button
          @click="activeTab = 'stats'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'stats'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          Statistiken & Upload
        </button>
        <button
          @click="activeTab = 'documents'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'documents'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          ]"
        >
          Dokumente & Chunks
        </button>
      </nav>
    </div>

    <!-- Stats Tab -->
    <div v-show="activeTab === 'stats'">

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <div class="card p-4">
        <div class="text-2xl font-bold text-blue-600">{{ stats?.parts_count || 0 }}</div>
        <div class="text-sm text-gray-500">Teile</div>
      </div>
      <div class="card p-4">
        <div class="text-2xl font-bold text-green-600">{{ stats?.assemblies_count || 0 }}</div>
        <div class="text-sm text-gray-500">Baugruppen</div>
      </div>
      <div class="card p-4">
        <div class="text-2xl font-bold text-purple-600">{{ stats?.documents_count || 0 }}</div>
        <div class="text-sm text-gray-500">Dokumente</div>
      </div>
      <div class="card p-4">
        <div class="text-2xl font-bold text-orange-600">{{ stats?.chunks_count || 0 }}</div>
        <div class="text-sm text-gray-500">Chunks</div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
      <div class="card p-4">
        <div class="text-2xl font-bold text-red-600">{{ stats?.change_requests_count || 0 }}</div>
        <div class="text-sm text-gray-500">Änderungsanträge</div>
      </div>
      <div class="card p-4">
        <div class="text-2xl font-bold text-teal-600">{{ stats?.specifications_count || 0 }}</div>
        <div class="text-sm text-gray-500">Spezifikationen</div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="uploadMessage" :class="[
      'p-4 rounded-lg mb-6',
      uploadMessage.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
    ]">
      {{ uploadMessage.text }}
    </div>

    <!-- Document Upload -->
    <div class="card mb-6">
      <div class="card-header">Dokument hochladen</div>
      <div class="card-body">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Dokumenttyp</label>
            <select v-model="documentType" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option v-for="type in documentTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Datei</label>
            <input
              ref="fileInput"
              type="file"
              @change="handleFileSelect"
              accept=".pdf,.md,.txt"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">Unterstützte Formate: PDF, Markdown, Text</p>
          </div>

          <button
            @click="uploadDocument"
            :disabled="!selectedFile || uploading"
            class="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="uploading">Hochladen...</span>
            <span v-else>Hochladen & Indizieren</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Admin Actions -->
    <div class="card">
      <div class="card-header">System-Aktionen</div>
      <div class="card-body space-y-3">
        <button
          @click="loadDataFolder"
          :disabled="uploading"
          class="w-full py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
        >
          <span v-if="uploading">Laden...</span>
          <span v-else>Dokumente aus data/documents laden</span>
        </button>

        <button
          @click="initDatabase"
          class="w-full py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          Datenbank initialisieren
        </button>

        <button
          @click="reindexAll"
          :disabled="reindexing"
          class="w-full py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400"
        >
          <span v-if="reindexing">Re-Indizieren...</span>
          <span v-else>Alle Dokumente neu indizieren</span>
        </button>

        <button
          @click="loadStats"
          :disabled="loading"
          class="w-full py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
        >
          Statistiken aktualisieren
        </button>
      </div>
    </div>

    </div><!-- End Stats Tab -->

    <!-- Documents Tab -->
    <div v-show="activeTab === 'documents'">
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <span>Dokumente ({{ documents.length }})</span>
          <button
            @click="loadDocuments"
            :disabled="loadingDocs"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            Aktualisieren
          </button>
        </div>
        <div class="card-body p-0">
          <div v-if="loadingDocs" class="p-8 text-center text-gray-500">
            Laden...
          </div>
          <div v-else-if="documents.length === 0" class="p-8 text-center text-gray-500">
            Keine Dokumente gefunden. Verwenden Sie "Dokumente aus data/documents laden" um Dokumente zu importieren.
          </div>
          <div v-else class="divide-y divide-gray-200 max-h-[500px] overflow-y-auto">
            <div
              v-for="doc in documents"
              :key="doc.id"
              @click="viewDocument(doc)"
              class="p-4 hover:bg-gray-50 cursor-pointer flex items-center gap-4"
            >
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-medium text-gray-900">{{ doc.document_number }}</span>
                  <span :class="['text-xs px-2 py-0.5 rounded', getTypeColor(doc.document_type)]">
                    {{ doc.document_type }}
                  </span>
                </div>
                <div class="text-sm text-gray-500 truncate">{{ doc.title }}</div>
              </div>
              <div class="text-sm text-gray-400">
                v{{ doc.version }}
              </div>
              <svg class="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div><!-- End Documents Tab -->

    <!-- Document Detail Modal -->
    <div v-if="selectedDocument" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium text-gray-900">{{ selectedDocument.document_number }}</h3>
            <p class="text-sm text-gray-500">{{ selectedDocument.title }}</p>
          </div>
          <button @click="closeDocumentModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- Document Content -->
          <div class="mb-6">
            <h4 class="text-sm font-medium text-gray-700 mb-2">Inhalt</h4>
            <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap max-h-48 overflow-y-auto">
              {{ selectedDocument.content || 'Kein Inhalt' }}
            </div>
          </div>

          <!-- Chunks -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-gray-700">
                Vektorisierte Chunks ({{ documentChunks.length }})
              </h4>
              <button
                @click="indexDocument(selectedDocument.id)"
                :disabled="indexing"
                class="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                <span v-if="indexing">Indexiere...</span>
                <span v-else>Jetzt indexieren</span>
              </button>
            </div>

            <!-- Index Message -->
            <div v-if="indexMessage" :class="[
              'p-2 rounded text-sm mb-3',
              indexMessage.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            ]">
              {{ indexMessage.text }}
            </div>

            <div v-if="loadingChunks" class="text-center text-gray-500 py-4">
              Laden...
            </div>
            <div v-else-if="documentChunks.length === 0" class="text-center text-gray-500 py-4 bg-yellow-50 rounded-lg">
              <p>Keine Chunks gefunden.</p>
              <p class="text-xs mt-1">Klicken Sie auf "Jetzt indexieren" um das Dokument zu vektorisieren.</p>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="chunk in documentChunks"
                :key="chunk.id"
                class="border border-gray-200 rounded-lg p-3"
              >
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-medium text-gray-500">Chunk #{{ chunk.chunk_index }}</span>
                  <span v-if="chunk.has_embedding" class="text-xs text-green-600 flex items-center gap-1">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                    Embedding vorhanden
                  </span>
                </div>
                <div class="text-sm text-gray-700 whitespace-pre-wrap">{{ chunk.content }}</div>
                <div v-if="chunk.embedding_preview" class="mt-2 text-xs text-gray-400 font-mono">
                  Embedding: [{{ chunk.embedding_preview.map(v => v.toFixed(4)).join(', ') }}, ...]
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
