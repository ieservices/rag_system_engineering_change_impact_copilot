from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings


SYSTEM_PROMPT = """Du bist ein KI-Assistent für das Engineering Change Management.
Du hilfst Ingenieuren dabei, die Auswirkungen technischer Änderungen zu verstehen.

Deine Aufgaben:
1. Analysiere technische Änderungen und deren Auswirkungen auf Produktstrukturen
2. Finde relevante Dokumente, Spezifikationen und Prüfberichte
3. Identifiziere betroffene Bauteile und Baugruppen
4. Erkläre Abhängigkeiten zwischen Komponenten

Antworte immer auf Deutsch und beziehe dich auf die bereitgestellten Quellen.
Wenn du dir unsicher bist, sage das deutlich.
Gib immer die Quellen an, auf die du dich beziehst."""


class RAGService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER

        if self.provider == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        else:
            # vLLM with OpenAI-compatible API
            self.client = OpenAI(
                base_url=settings.VLLM_BASE_URL,
                api_key="not-needed"
            )
            self.model = settings.VLLM_MODEL

    def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate a response using RAG."""

        # Build context string from retrieved documents
        context_str = self._build_context(context)

        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges

        # Add current query with context
        user_message = f"""Kontext aus der Wissensbasis:
{context_str}

Frage des Nutzers:
{query}

Bitte beantworte die Frage basierend auf dem bereitgestellten Kontext.
Gib die Quellen an (Dokumentnummer, Version, Abschnitt)."""

        messages.append({"role": "user", "content": user_message})

        # Generate response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )

        return {
            "answer": response.choices[0].message.content,
            "model": self.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        }

    def _build_context(self, context: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not context:
            return "Keine relevanten Dokumente gefunden."

        context_parts = []
        for i, doc in enumerate(context, 1):
            doc_info = f"[Quelle {i}]"
            if doc.get("document_number"):
                doc_info += f" {doc['document_number']}"
            if doc.get("version"):
                doc_info += f" v{doc['version']}"
            if doc.get("title"):
                doc_info += f" - {doc['title']}"

            content = doc.get("content", "")
            score = doc.get("score", 0)

            context_parts.append(f"{doc_info} (Relevanz: {score:.2f}):\n{content}")

        return "\n\n---\n\n".join(context_parts)

    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract engineering entities from query."""
        messages = [
            {
                "role": "system",
                "content": """Extrahiere technische Entitäten aus der Anfrage.
Antworte im JSON-Format:
{
  "parts": ["Teilenummern"],
  "assemblies": ["Baugruppennummern"],
  "materials": ["Materialien"],
  "documents": ["Dokumentnummern"],
  "change_requests": ["CR-Nummern"]
}"""
            },
            {"role": "user", "content": query}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
            max_tokens=500
        )

        import json
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"parts": [], "assemblies": [], "materials": [], "documents": [], "change_requests": []}


rag_service = RAGService()
