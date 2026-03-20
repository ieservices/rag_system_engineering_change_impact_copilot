<script setup>
import { ref } from 'vue'

const activeSection = ref('overview')

const sections = [
  { id: 'overview', title: 'Übersicht' },
  { id: 'local-llm', title: 'Lokales LLM' },
  { id: 'vllm', title: 'vLLM Setup' },
  { id: 'ollama', title: 'Ollama Setup' },
  { id: 'config', title: 'Konfiguration' }
]
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Dokumentation</h1>

    <div class="grid grid-cols-12 gap-6">
      <!-- Sidebar Navigation -->
      <div class="col-span-12 md:col-span-3">
        <nav class="card p-4 sticky top-4">
          <ul class="space-y-1">
            <li v-for="section in sections" :key="section.id">
              <button
                @click="activeSection = section.id"
                :class="[
                  'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors',
                  activeSection === section.id
                    ? 'bg-blue-100 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                ]"
              >
                {{ section.title }}
              </button>
            </li>
          </ul>
        </nav>
      </div>

      <!-- Content -->
      <div class="col-span-12 md:col-span-9">
        <div class="card p-6">
          <!-- Overview -->
          <div v-if="activeSection === 'overview'">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Engineering Change Impact Copilot</h2>

            <div class="prose prose-sm max-w-none">
              <p class="text-gray-700 mb-4">
                Der Engineering Change Impact Copilot ist ein KI-gestützter Assistent zur Analyse technischer
                Änderungen in Produktstrukturen. Das System nutzt RAG (Retrieval-Augmented Generation) um
                relevante Dokumente, Anforderungen und betroffene Komponenten aufzufinden.
              </p>

              <h3 class="text-lg font-semibold mt-6 mb-3">Hauptfunktionen</h3>
              <ul class="list-disc list-inside space-y-2 text-gray-700">
                <li>Natürlichsprachliche Abfragen zu Komponenten und Dokumenten</li>
                <li>Impact-Analyse für Teile und Baugruppen</li>
                <li>Dokumenten-Retrieval mit Relevanzbewertung</li>
                <li>Visualisierung von Abhängigkeiten</li>
                <li>Verwaltung von Change Requests</li>
              </ul>

              <h3 class="text-lg font-semibold mt-6 mb-3">Architektur</h3>
              <ul class="list-disc list-inside space-y-2 text-gray-700">
                <li><strong>Backend:</strong> FastAPI mit Python</li>
                <li><strong>Datenbank:</strong> PostgreSQL mit pgvector</li>
                <li><strong>Frontend:</strong> Vue 3 mit Vite</li>
                <li><strong>LLM:</strong> OpenAI API oder lokales vLLM</li>
              </ul>
            </div>
          </div>

          <!-- Local LLM -->
          <div v-if="activeSection === 'local-llm'">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Lokales LLM für Datenschutz</h2>

            <div class="prose prose-sm max-w-none">
              <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
                <p class="text-blue-700">
                  <strong>Warum lokal?</strong><br>
                  Für sensible Unternehmensdaten empfiehlt sich der Einsatz eines lokalen LLMs.
                  So verlassen keine vertraulichen Informationen das Firmennetzwerk.
                </p>
              </div>

              <h3 class="text-lg font-semibold mt-6 mb-3">Unterstützte Optionen</h3>
              <div class="space-y-4">
                <div class="border rounded-lg p-4">
                  <h4 class="font-medium">vLLM</h4>
                  <p class="text-sm text-gray-600 mt-1">
                    Hochperformanter Inference-Server mit OpenAI-kompatibler API.
                    Optimal für Produktion mit GPU-Unterstützung.
                  </p>
                </div>
                <div class="border rounded-lg p-4">
                  <h4 class="font-medium">Ollama</h4>
                  <p class="text-sm text-gray-600 mt-1">
                    Einfache Einrichtung für lokale Entwicklung.
                    Unterstützt viele Open-Source-Modelle.
                  </p>
                </div>
                <div class="border rounded-lg p-4">
                  <h4 class="font-medium">Text Generation Inference (TGI)</h4>
                  <p class="text-sm text-gray-600 mt-1">
                    Hugging Face's Inference Server.
                    Gute Alternative zu vLLM.
                  </p>
                </div>
              </div>

              <h3 class="text-lg font-semibold mt-6 mb-3">Empfohlene Modelle</h3>
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left">Modell</th>
                    <th class="px-3 py-2 text-left">Parameter</th>
                    <th class="px-3 py-2 text-left">VRAM</th>
                    <th class="px-3 py-2 text-left">Empfehlung</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-t">
                    <td class="px-3 py-2">Mistral 7B</td>
                    <td class="px-3 py-2">7B</td>
                    <td class="px-3 py-2">~16 GB</td>
                    <td class="px-3 py-2">Gutes Preis-Leistungs-Verhältnis</td>
                  </tr>
                  <tr class="border-t">
                    <td class="px-3 py-2">Mixtral 8x7B</td>
                    <td class="px-3 py-2">46.7B MoE</td>
                    <td class="px-3 py-2">~90 GB</td>
                    <td class="px-3 py-2">Beste Qualität</td>
                  </tr>
                  <tr class="border-t">
                    <td class="px-3 py-2">Llama 3 8B</td>
                    <td class="px-3 py-2">8B</td>
                    <td class="px-3 py-2">~16 GB</td>
                    <td class="px-3 py-2">Gute Deutsch-Kenntnisse</td>
                  </tr>
                  <tr class="border-t">
                    <td class="px-3 py-2">LeoLM 13B</td>
                    <td class="px-3 py-2">13B</td>
                    <td class="px-3 py-2">~26 GB</td>
                    <td class="px-3 py-2">Optimiert für Deutsch</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- vLLM -->
          <div v-if="activeSection === 'vllm'">
            <h2 class="text-xl font-bold text-gray-900 mb-4">vLLM Setup</h2>

            <div class="prose prose-sm max-w-none">
              <h3 class="text-lg font-semibold mb-3">1. Installation</h3>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Mit pip installieren
pip install vllm

# Oder mit Docker
docker pull vllm/vllm-openai:latest</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">2. Server starten</h3>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Mistral 7B starten
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1

# Mit Docker
docker run -d \
  --gpus all \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model mistralai/Mistral-7B-Instruct-v0.2</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">3. Embedding-Server</h3>
              <p class="text-gray-700 mb-3">
                Für Embeddings empfiehlt sich ein separater Server:
              </p>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># TEI (Text Embeddings Inference) von Hugging Face
docker run -d \
  --gpus all \
  -p 8001:80 \
  ghcr.io/huggingface/text-embeddings-inference:latest \
  --model-id BAAI/bge-large-en-v1.5</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">4. Konfiguration anpassen</h3>
              <p class="text-gray-700 mb-3">
                In der <code class="bg-gray-100 px-1 rounded">.env</code> Datei:
              </p>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code>LLM_PROVIDER=vllm
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
VLLM_EMBEDDING_MODEL=BAAI/bge-large-en-v1.5</code></pre>
            </div>
          </div>

          <!-- Ollama -->
          <div v-if="activeSection === 'ollama'">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Ollama Setup</h2>

            <div class="prose prose-sm max-w-none">
              <p class="text-gray-700 mb-4">
                Ollama ist die einfachste Methode für lokale LLM-Entwicklung.
              </p>

              <h3 class="text-lg font-semibold mb-3">1. Installation</h3>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download von https://ollama.com/download</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">2. Modell herunterladen</h3>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Mistral für Chat
ollama pull mistral

# Für Embeddings
ollama pull nomic-embed-text</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">3. Server starten</h3>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Ollama startet automatisch, oder:
ollama serve</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">4. API testen</h3>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Chat-Anfrage testen
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hallo, wer bist du?"
}'</code></pre>

              <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 mt-6">
                <p class="text-yellow-700">
                  <strong>Hinweis:</strong> Ollama verwendet eine eigene API.
                  Für OpenAI-kompatible Anfragen nutzen Sie vLLM oder einen Adapter.
                </p>
              </div>
            </div>
          </div>

          <!-- Configuration -->
          <div v-if="activeSection === 'config'">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Konfiguration</h2>

            <div class="prose prose-sm max-w-none">
              <h3 class="text-lg font-semibold mb-3">Umgebungsvariablen</h3>
              <p class="text-gray-700 mb-3">
                Erstellen Sie eine <code class="bg-gray-100 px-1 rounded">.env</code> Datei im Backend-Verzeichnis:
              </p>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Datenbank
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/impact_copilot

# LLM Provider: "openai" oder "vllm"
LLM_PROVIDER=openai

# OpenAI Konfiguration (wenn LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# vLLM Konfiguration (wenn LLM_PROVIDER=vllm)
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
VLLM_EMBEDDING_MODEL=BAAI/bge-large-en-v1.5

# RAG Einstellungen
EMBEDDING_DIMENSION=1536
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5</code></pre>

              <h3 class="text-lg font-semibold mt-6 mb-3">Provider wechseln</h3>
              <p class="text-gray-700 mb-3">
                Um zwischen OpenAI und lokalem LLM zu wechseln:
              </p>
              <ol class="list-decimal list-inside space-y-2 text-gray-700">
                <li>Ändern Sie <code class="bg-gray-100 px-1 rounded">LLM_PROVIDER</code> in der .env Datei</li>
                <li>Starten Sie das Backend neu</li>
                <li>Bei vLLM: Stellen Sie sicher, dass der Inference-Server läuft</li>
              </ol>

              <h3 class="text-lg font-semibold mt-6 mb-3">Docker Compose</h3>
              <p class="text-gray-700 mb-3">
                Die komplette Umgebung mit Docker starten:
              </p>
              <pre class="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm"><code># Entwicklung starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Stoppen
docker-compose down</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
