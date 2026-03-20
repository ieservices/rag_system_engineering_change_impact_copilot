# Engineering Change Impact Copilot

Ein KI-gestützter Assistent, der technische Änderungen entlang der Produktstruktur analysiert und alle relevanten Dokumente, Anforderungen und betroffenen Komponenten mit Quellenbezug auffindbar macht.

## Features

- **Chat-Interface**: Natürlichsprachliche Abfragen zu Komponenten, Dokumenten und Änderungen
- **Quellenpanel**: Treffer mit Dokumentname, Version, Status und Relevanzscore
- **Objektpanel**: Gefundene Teile, Baugruppen, Change Requests und Spezifikationen
- **Impact View**: Graph-/Tabellenansicht für betroffene Teile und Abhängigkeiten
- **Admin/Ingestion**: Dokumenten-Upload, Re-Index und Systemstatus

## Beispiel-Anfragen

- "Welche Dokumente sind von einer Änderung an Baugruppe BG-240 betroffen?"
- "Zeige mir alle Spezifikationen und Prüfberichte für Ventil V-202."
- "Welche Risiken bestehen, wenn Material M-17 ersetzt wird?"
- "Welche offenen Änderungen betreffen Bauteile aus Edelstahl?"

## Tech Stack

- **Backend**: FastAPI, SQLModel, pgvector
- **Frontend**: Vue 3, Vite, TailwindCSS
- **Datenbank**: PostgreSQL mit pgvector
- **LLM**: OpenAI API oder lokales vLLM

## Schnellstart mit Docker

```bash
# Repository klonen
git clone <repository-url>
cd rag-system-engineering-change-impact-copilot

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env bearbeiten und OPENAI_API_KEY setzen

# Docker Compose starten
docker-compose up -d

# Synthetische Daten generieren
docker-compose exec backend python scripts/generate_data.py

# Anwendung öffnen
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
```

## Lokale Entwicklung

### Backend

```bash
cd backend

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# PostgreSQL mit pgvector starten (Docker)
docker run -d \
  --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=impact_copilot \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Backend starten
uvicorn app.main:app --reload

# Synthetische Daten generieren
python scripts/generate_data.py
```

### Frontend

```bash
cd frontend

# Dependencies installieren
npm install

# Development Server starten
npm run dev

# Produktions-Build
npm run build
```

## Lokales LLM (Datenschutz)

Für den Einsatz mit sensiblen Unternehmensdaten kann ein lokales LLM verwendet werden.

### vLLM Setup

```bash
# vLLM installieren
pip install vllm

# Server starten
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct-v0.2 \
  --host 0.0.0.0 \
  --port 8000

# .env anpassen
LLM_PROVIDER=vllm
VLLM_BASE_URL=http://localhost:8000/v1
```

### Ollama Setup

```bash
# Ollama installieren
curl -fsSL https://ollama.com/install.sh | sh

# Modell herunterladen
ollama pull mistral

# Server starten
ollama serve
```

Weitere Details zur lokalen LLM-Integration finden Sie in der integrierten Dokumentation unter `/docs`.

## API Endpunkte

| Endpunkt | Beschreibung |
|----------|--------------|
| `POST /api/chat/` | Chat-Anfrage mit RAG |
| `GET /api/chat/examples` | Beispiel-Anfragen |
| `GET /api/search/` | Dokumentensuche |
| `GET /api/parts/` | Teile auflisten |
| `GET /api/parts/{id}/impact` | Impact-Analyse für Teil |
| `GET /api/assemblies/` | Baugruppen auflisten |
| `GET /api/assemblies/{id}/impact` | Impact-Analyse für Baugruppe |
| `GET /api/change-requests/` | Änderungsanträge |
| `GET /api/documents/` | Dokumente |
| `POST /api/admin/ingest` | Dokument hochladen |
| `POST /api/admin/reindex` | Neu indizieren |
| `GET /api/admin/stats` | Systemstatistiken |

## Projektstruktur

```
├── backend/
│   ├── app/
│   │   ├── api/          # API Router
│   │   ├── core/         # Konfiguration & Datenbank
│   │   ├── models/       # SQLModel Definitionen
│   │   └── services/     # Business Logic (RAG, Search)
│   ├── scripts/          # Datengenerierung
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue Komponenten
│   │   ├── views/        # Seiten
│   │   └── stores/       # Pinia Stores
│   └── Dockerfile
├── data/                 # Dokumente & synthetische Daten
├── docker-compose.yml
└── README.md
```

## Lizenz

MIT License
