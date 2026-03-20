/* jshint esversion: 11 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';

export var useChatStore = defineStore('chat', function() {
  var messages = ref([]);
  var isLoading = ref(false);
  var currentSources = ref([]);
  var currentObjects = ref({});
  var exampleQueries = ref([]);
  var currentSessionId = ref(null);
  var sessions = ref([]);
  var sessionsLoading = ref(false);

  var conversationHistory = computed(function() {
    return messages.value.map(function(m) {
      return {
        role: m.role,
        content: m.content
      };
    });
  });

  async function loadExamples() {
    try {
      var response = await axios.get('/api/chat/examples');
      exampleQueries.value = response.data;
    } catch (error) {
      console.error('Failed to load examples:', error);
      exampleQueries.value = [
        'Welche Dokumente sind von einer Änderung an Baugruppe BG-240 betroffen?',
        'Zeige mir alle Spezifikationen und Prüfberichte für Ventil V-202.',
        'Welche Risiken bestehen, wenn Material M-17 ersetzt wird?',
        'Welche offenen Änderungen betreffen Bauteile aus Edelstahl?'
      ];
    }
  }

  async function loadSessions() {
    sessionsLoading.value = true;
    try {
      var response = await axios.get('/api/sessions/');
      sessions.value = response.data;
    } catch (error) {
      console.error('Failed to load sessions:', error);
      sessions.value = [];
    } finally {
      sessionsLoading.value = false;
    }
  }

  async function loadSession(sessionId) {
    isLoading.value = true;
    try {
      var response = await axios.get('/api/sessions/' + sessionId);
      var session = response.data;

      currentSessionId.value = session.id;
      messages.value = session.messages.map(function(m) {
        return {
          role: m.role,
          content: m.content,
          timestamp: new Date(m.created_at),
          sources: m.sources,
          confidence: m.confidence
        };
      });

      // Set sources and objects from last assistant message
      var reversed = session.messages.slice().reverse();
      var lastAssistant = reversed.find(function(m) { return m.role === 'assistant'; });
      if (lastAssistant) {
        currentSources.value = lastAssistant.sources || [];
        currentObjects.value = lastAssistant.affected_objects || {};
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      isLoading.value = false;
    }
  }

  async function deleteSession(sessionId) {
    try {
      await axios.delete('/api/sessions/' + sessionId);
      sessions.value = sessions.value.filter(function(s) { return s.id !== sessionId; });

      // If we deleted the current session, clear the chat
      if (currentSessionId.value === sessionId) {
        clearChat();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  }

  async function sendMessage(content) {
    // Add user message
    messages.value.push({
      role: 'user',
      content: content,
      timestamp: new Date()
    });

    isLoading.value = true;

    try {
      var response = await axios.post('/api/chat/', {
        message: content,
        session_id: currentSessionId.value,
        conversation_history: conversationHistory.value.slice(0, -1) // Exclude current message
      });

      var data = response.data;

      // Update session ID if this is a new session
      if (!currentSessionId.value && data.session_id) {
        currentSessionId.value = data.session_id;
        // Refresh sessions list to include the new session
        loadSessions();
      }

      // Add assistant message
      messages.value.push({
        role: 'assistant',
        content: data.answer,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence
      });

      // Update current sources and objects
      currentSources.value = data.sources;
      currentObjects.value = data.affected_objects;

    } catch (error) {
      console.error('Chat error:', error);
      messages.value.push({
        role: 'assistant',
        content: 'Entschuldigung, es ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.',
        timestamp: new Date(),
        error: true
      });
    } finally {
      isLoading.value = false;
    }
  }

  function clearChat() {
    messages.value = [];
    currentSources.value = [];
    currentObjects.value = {};
    currentSessionId.value = null;
  }

  async function startNewChat() {
    clearChat();
    try {
      // Create a new session in the database immediately
      var response = await axios.post('/api/sessions/', {
        title: 'Neue Unterhaltung'
      });
      currentSessionId.value = response.data.id;
      // Refresh the sessions list
      await loadSessions();
    } catch (error) {
      console.error('Failed to create new session:', error);
    }
  }

  async function renameSession(sessionId, newTitle) {
    try {
      await axios.patch('/api/sessions/' + sessionId, { title: newTitle });
      // Update local state
      var session = sessions.value.find(function(s) { return s.id === sessionId; });
      if (session) {
        session.title = newTitle;
      }
    } catch (error) {
      console.error('Failed to rename session:', error);
    }
  }

  return {
    messages: messages,
    isLoading: isLoading,
    currentSources: currentSources,
    currentObjects: currentObjects,
    exampleQueries: exampleQueries,
    conversationHistory: conversationHistory,
    currentSessionId: currentSessionId,
    sessions: sessions,
    sessionsLoading: sessionsLoading,
    loadExamples: loadExamples,
    loadSessions: loadSessions,
    loadSession: loadSession,
    deleteSession: deleteSession,
    sendMessage: sendMessage,
    clearChat: clearChat,
    startNewChat: startNewChat,
    renameSession: renameSession
  };
});
