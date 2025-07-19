<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Vyhledávání v souborech</h1>
      <p class="text-gray-600">Vyhledávejte v indexovaných souborech a složkách</p>
    </div>

    <!-- Vyhledávací formulář -->
    <div class="bg-white rounded-lg shadow mb-8">
      <div class="p-6">
        <div class="flex space-x-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              @keyup.enter="performSearch"
              type="text"
              placeholder="Zadejte dotaz pro vyhledávání..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            @click="performSearch"
            :disabled="!searchQuery.trim()"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon name="heroicons:magnifying-glass" class="w-5 h-5 inline mr-2" />
            Vyhledat
          </button>
        </div>

        <!-- Návrhy -->
        <div v-if="suggestions.length > 0 && showSuggestions" class="mt-4">
          <div class="text-sm text-gray-600 mb-2">Návrhy:</div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="selectSuggestion(suggestion)"
              class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistiky -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <Icon name="heroicons:document" class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Indexované soubory</p>
            <p class="text-2xl font-bold text-gray-900">{{ searchStats.total_indexed_files || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <Icon name="heroicons:folder" class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Sledované položky</p>
            <p class="text-2xl font-bold text-gray-900">{{ searchStats.total_watched_items || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <Icon name="heroicons:magnifying-glass" class="w-6 h-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Výsledky</p>
            <p class="text-2xl font-bold text-gray-900">{{ searchResults.total_results || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Výsledky vyhledávání -->
    <div v-if="searchResults.results && searchResults.results.length > 0" class="bg-white rounded-lg shadow">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">
          Výsledky vyhledávání pro "{{ searchQuery }}"
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          Nalezeno {{ searchResults.total_results }} výsledků
        </p>
      </div>

      <div class="divide-y divide-gray-200">
        <div
          v-for="result in searchResults.results"
          :key="result.id"
          class="p-6 hover:bg-gray-50"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center mb-2">
                <Icon
                  :name="getFileIcon(result.file_type)"
                  class="w-5 h-5 text-gray-600 mr-2"
                />
                <h3 class="text-lg font-medium text-gray-900">{{ result.file_name }}</h3>
                <span class="ml-2 text-sm text-gray-500">
                  {{ formatFileSize(result.file_size) }}
                </span>
              </div>
              
              <p class="text-sm text-gray-600 mb-2">
                {{ result.watched_item_name }} • {{ result.file_path }}
              </p>

              <!-- Náhled obsahu -->
              <div class="bg-gray-50 rounded p-3 text-sm text-gray-700">
                <div class="line-clamp-3">{{ getContentPreview(result.content_text) }}</div>
              </div>

              <div class="flex items-center mt-3 space-x-4 text-xs text-gray-500">
                <span>Typ: {{ result.file_type }}</span>
                <span>Indexováno: {{ formatDate(result.indexed_at) }}</span>
              </div>
            </div>

            <div class="ml-4">
              <button
                @click="openFile(result.file_path)"
                class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                <Icon name="heroicons:eye" class="w-4 h-4 inline mr-1" />
                Zobrazit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Prázdný stav -->
    <div v-else-if="hasSearched && searchResults.results && searchResults.results.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
      <Icon name="heroicons:magnifying-glass" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">Žádné výsledky</h3>
      <p class="text-gray-600">
        Pro dotaz "{{ searchQuery }}" nebyly nalezeny žádné výsledky. 
        Zkuste jiný dotaz nebo přidejte více souborů k indexování.
      </p>
    </div>

    <!-- Úvodní stav -->
    <div v-else-if="!hasSearched" class="bg-white rounded-lg shadow p-8 text-center">
      <Icon name="heroicons:magnifying-glass" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">Začněte vyhledávání</h3>
      <p class="text-gray-600">
        Zadejte dotaz do vyhledávacího pole a najděte soubory v indexovaných složkách.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()

// Reaktivní data
const searchQuery = ref('')
const searchResults = ref({})
const searchStats = ref({})
const suggestions = ref([])
const showSuggestions = ref(false)
const hasSearched = ref(false)

// Metody
const performSearch = async () => {
  if (!searchQuery.value.trim()) return

  try {
    hasSearched.value = true
    showSuggestions.value = false
    const response = await api.searchFiles(searchQuery.value)
    searchResults.value = response
  } catch (error) {
    console.error('Chyba při vyhledávání:', error)
  }
}

const loadSearchSuggestions = async () => {
  if (!searchQuery.value.trim()) {
    suggestions.value = []
    return
  }

  try {
    const response = await api.getSearchSuggestions(searchQuery.value)
    suggestions.value = response.suggestions
    showSuggestions.value = true
  } catch (error) {
    console.error('Chyba při načítání návrhů:', error)
  }
}

const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion
  showSuggestions.value = false
  performSearch()
}

const loadSearchStats = async () => {
  try {
    const response = await api.getSearchStats()
    searchStats.value = response
  } catch (error) {
    console.error('Chyba při načítání statistik:', error)
  }
}

const getFileIcon = (fileType) => {
  const iconMap = {
    '.pdf': 'heroicons:document',
    '.docx': 'heroicons:document',
    '.doc': 'heroicons:document',
    '.txt': 'heroicons:document-text',
    '.md': 'heroicons:document-text',
    '.py': 'heroicons:code-bracket',
    '.js': 'heroicons:code-bracket',
    '.html': 'heroicons:code-bracket',
    '.css': 'heroicons:code-bracket'
  }
  return iconMap[fileType] || 'heroicons:document'
}

const getContentPreview = (content) => {
  if (!content) return 'Žádný obsah'
  return content.length > 200 ? content.substring(0, 200) + '...' : content
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('cs-CZ')
}

const openFile = (filePath) => {
  // V budoucnu by se dalo implementovat otevření souboru
  console.log('Otevřít soubor:', filePath)
}

// Watchers
watch(searchQuery, (newQuery) => {
  if (newQuery.trim()) {
    // Debounce pro návrhy
    clearTimeout(window.suggestionTimeout)
    window.suggestionTimeout = setTimeout(() => {
      loadSearchSuggestions()
    }, 300)
  } else {
    suggestions.value = []
    showSuggestions.value = false
  }
})

// Načtení dat při mountování
onMounted(async () => {
  await loadSearchStats()
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 