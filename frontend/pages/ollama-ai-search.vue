<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Ollama AI Vyhledávání</h1>
            <p class="mt-1 text-sm text-gray-500">
              Hybridní lokální AI vyhledávání s Ollama modely
            </p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="reindexAll"
              :disabled="isReindexing"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              <Icon name="arrow-path" class="w-4 h-4 mr-2" :class="{ 'animate-spin': isReindexing }" />
              {{ isReindexing ? 'Indexuji...' : 'Přeindexovat' }}
            </button>
            <button
              @click="clearIndex"
              class="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
            >
              <Icon name="trash" class="w-4 h-4 mr-2" />
              Vyčistit index
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Search Form -->
      <div class="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Dotaz
            </label>
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="getSuggestions"
                @keyup.enter="performSearch"
                type="text"
                placeholder="Zadejte dotaz pro AI vyhledávání..."
                class="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                @click="performSearch"
                :disabled="isSearching"
                class="absolute right-2 top-2 p-2 text-gray-400 hover:text-gray-600"
              >
                <Icon name="magnifying-glass" class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Typ vyhledávání
              </label>
              <select
                v-model="searchType"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="semantic">Sémantické</option>
                <option value="hybrid">Hybridní</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Počet výsledků
              </label>
              <select
                v-model="searchLimit"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Typ souboru
              </label>
              <select
                v-model="selectedFileType"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Všechny typy</option>
                <option value="txt">Textové soubory</option>
                <option value="md">Markdown</option>
                <option value="py">Python</option>
                <option value="js">JavaScript</option>
                <option value="vue">Vue</option>
                <option value="json">JSON</option>
                <option value="yaml">YAML</option>
                <option value="pdf">PDF</option>
                <option value="docx">Word</option>
              </select>
            </div>
          </div>

          <!-- Suggestions -->
          <div v-if="suggestions.length > 0" class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Návrhy
            </label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="useSuggestion(suggestion)"
                class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Answer -->
      <div v-if="aiAnswer" class="bg-white rounded-lg shadow-sm border p-6 mb-8">
        <h3 class="text-lg font-medium text-gray-900 mb-4">AI Odpověď</h3>
        <div class="prose max-w-none">
          <p class="text-gray-700 whitespace-pre-wrap">{{ aiAnswer }}</p>
        </div>
      </div>

      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="space-y-6">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold text-gray-900">
            Nalezeno {{ searchResults.length }} výsledků
          </h2>
          <div class="text-sm text-gray-500">
            Dotaz: "{{ lastQuery }}"
          </div>
        </div>

        <!-- Results List -->
        <div class="space-y-4">
          <div
            v-for="result in searchResults"
            :key="result.id"
            class="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
          >
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-medium text-gray-900 mb-2">
                  {{ result.file_name }}
                </h3>
                <p class="text-sm text-gray-500 mb-2">
                  {{ result.file_path }}
                </p>
                <div class="flex items-center space-x-4 text-sm text-gray-500">
                  <span>{{ result.watched_item_name }}</span>
                  <span>{{ result.file_type }}</span>
                  <span>Relevance: {{ (result.relevance_score * 100).toFixed(1) }}%</span>
                </div>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="openFile(result.file_path)"
                  class="inline-flex items-center px-3 py-1 border border-gray-300 text-sm rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Icon name="eye" class="w-4 h-4 mr-1" />
                  Otevřít
                </button>
              </div>
            </div>

            <!-- Context Snippets -->
            <div v-if="result.context_snippets && result.context_snippets.length > 0" class="mb-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Relevantní úryvky:</h4>
              <div class="space-y-2">
                <div
                  v-for="(snippet, index) in result.context_snippets"
                  :key="index"
                  class="p-3 bg-gray-50 rounded-md text-sm text-gray-700"
                >
                  {{ snippet }}
                </div>
              </div>
            </div>

            <!-- Content Preview -->
            <div class="border-t pt-4">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Náhled obsahu:</h4>
              <div class="text-sm text-gray-700 max-h-32 overflow-y-auto">
                {{ result.content_text.substring(0, 500) }}{{ result.content_text.length > 500 ? '...' : '' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Results -->
      <div v-else-if="hasSearched && !isSearching" class="text-center py-12">
        <Icon name="magnifying-glass" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Žádné výsledky</h3>
        <p class="text-gray-500">
          Zkuste upravit dotaz nebo použít jiné klíčové slovo.
        </p>
      </div>

      <!-- Loading -->
      <div v-if="isSearching" class="text-center py-12">
        <div class="inline-flex items-center">
          <Icon name="arrow-path" class="w-6 h-6 text-blue-600 animate-spin mr-3" />
          <span class="text-lg text-gray-700">Vyhledávám...</span>
        </div>
      </div>

      <!-- Stats -->
      <div v-if="stats" class="mt-8 bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Statistiky Ollama AI indexu</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ stats.ai_index_stats.total_documents }}</div>
            <div class="text-sm text-gray-500">Indexovaných dokumentů</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ stats.total_watched_items }}</div>
            <div class="text-sm text-gray-500">Sledovaných položek</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600">{{ stats.total_indexed_files }}</div>
            <div class="text-sm text-gray-500">Celkem souborů</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-600">{{ stats.ai_index_stats.embedding_model }}</div>
            <div class="text-sm text-gray-500">Embedding model</div>
          </div>
        </div>
        <div class="mt-4 text-sm text-gray-500">
          LLM model: {{ stats.ai_index_stats.llm_model }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()

// Reactive data
const searchQuery = ref('')
const searchType = ref('semantic')
const searchLimit = ref(10)
const selectedFileType = ref('')
const searchResults = ref([])
const suggestions = ref([])
const stats = ref(null)
const isSearching = ref(false)
const isReindexing = ref(false)
const hasSearched = ref(false)
const lastQuery = ref('')
const aiAnswer = ref('')

// Methods
const performSearch = async () => {
  if (!searchQuery.value.trim()) return

  isSearching.value = true
  hasSearched.value = true
  lastQuery.value = searchQuery.value
  aiAnswer.value = ''

  try {
    // Vyhledá dokumenty
    const searchResponse = await api.ollamaSearch({
      query: searchQuery.value,
      limit: parseInt(searchLimit.value),
      search_type: searchType.value,
      file_types: selectedFileType.value ? [selectedFileType.value] : undefined
    })

    searchResults.value = searchResponse.results || []

    // Generuje AI odpověď pokud jsou výsledky
    if (searchResults.value.length > 0) {
      const answerResponse = await api.ollamaGenerateAnswer({
        query: searchQuery.value,
        context_documents: searchResults.value.slice(0, 3), // Použije max 3 dokumenty
        max_length: 500
      })
      
      aiAnswer.value = answerResponse.answer
    }
  } catch (error) {
    console.error('Chyba při vyhledávání:', error)
    searchResults.value = []
    aiAnswer.value = ''
  } finally {
    isSearching.value = false
  }
}

const getSuggestions = async () => {
  if (!searchQuery.value.trim() || searchQuery.value.length < 2) {
    suggestions.value = []
    return
  }

  try {
    const response = await api.getOllamaSuggestions(searchQuery.value, 5)
    suggestions.value = response.suggestions || []
  } catch (error) {
    console.error('Chyba při načítání návrhů:', error)
    suggestions.value = []
  }
}

const useSuggestion = (suggestion) => {
  searchQuery.value = suggestion
  performSearch()
}

const reindexAll = async () => {
  isReindexing.value = true
  try {
    await api.ollamaReindex()
    await loadStats()
  } catch (error) {
    console.error('Chyba při přeindexování:', error)
  } finally {
    isReindexing.value = false
  }
}

const clearIndex = async () => {
  if (!confirm('Opravdu chcete vyčistit Ollama AI index?')) return

  try {
    await api.ollamaClearIndex()
    await loadStats()
    searchResults.value = []
    aiAnswer.value = ''
  } catch (error) {
    console.error('Chyba při čištění indexu:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await api.getOllamaStats()
    stats.value = response
  } catch (error) {
    console.error('Chyba při načítání statistik:', error)
  }
}

const openFile = (filePath) => {
  // Implementace otevření souboru
  console.log('Otevírám soubor:', filePath)
}

// Lifecycle
onMounted(() => {
  loadStats()
})
</script> 