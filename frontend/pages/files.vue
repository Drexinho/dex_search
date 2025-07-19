<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Sledované soubory a složky</h1>
      <p class="text-gray-600">Spravujte soubory a složky, které chcete indexovat pro vyhledávání</p>
    </div>

    <!-- Statistiky -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <Icon name="heroicons:folder" class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Sledované položky</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_watched_items || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <Icon name="heroicons:document" class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Indexované soubory</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_indexed_files || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <Icon name="heroicons:check-circle" class="w-6 h-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Aktivní položky</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.enabled_items || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="p-2 bg-orange-100 rounded-lg">
            <Icon name="heroicons:cpu-chip" class="w-6 h-6 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Indexování</p>
            <p class="text-2xl font-bold text-gray-900">{{ indexingCount }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Přidat novou položku -->
    <div class="bg-white rounded-lg shadow mb-8">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Přidat novou položku</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Cesta k souboru/složce</label>
            <div class="flex">
              <input
                v-model="newItem.path"
                type="text"
                placeholder="/cesta/k/souboru/nebo/složce"
                class="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <button
                @click="showBrowseModal = true"
                class="px-4 py-2 bg-gray-100 border border-l-0 border-gray-300 rounded-r-md hover:bg-gray-200"
              >
                <Icon name="heroicons:folder-open" class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Název</label>
            <input
              v-model="newItem.name"
              type="text"
              placeholder="Název položky"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Typ</label>
            <select
              v-model="newItem.type"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="file">Soubor</option>
              <option value="folder">Složka</option>
            </select>
          </div>

          <div class="flex items-center">
            <input
              v-model="newItem.recursive"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label class="ml-2 text-sm text-gray-700">Rekurzivní (pro složky)</label>
          </div>
        </div>

        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Typy souborů (volitelné)</label>
          <input
            v-model="newItem.fileTypesInput"
            type="text"
            placeholder=".txt,.md,.pdf (oddělené čárkami)"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        <div class="mt-6">
          <button
            @click="addWatchedItem"
            :disabled="!newItem.path || !newItem.name"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon name="heroicons:plus" class="w-5 h-5 inline mr-2" />
            Přidat položku
          </button>
        </div>
      </div>
    </div>

    <!-- Seznam sledovaných položek -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-lg font-semibold text-gray-900">Sledované položky</h2>
      </div>

      <div v-if="watchedItems.length === 0" class="p-8 text-center">
        <Icon name="heroicons:folder" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Žádné sledované položky</h3>
        <p class="text-gray-600">Přidejte první soubor nebo složku pro začátek indexování</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div
          v-for="item in watchedItems"
          :key="item.id"
          class="p-6 hover:bg-gray-50"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg mr-4">
                <Icon
                  :name="item.type === 'folder' ? 'heroicons:folder' : 'heroicons:document'"
                  class="w-6 h-6 text-blue-600"
                />
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">{{ item.name }}</h3>
                <p class="text-sm text-gray-600">{{ item.path }}</p>
                <div class="flex items-center mt-2 space-x-4">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ item.type }}
                  </span>
                  <span v-if="item.recursive" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Rekurzivní
                  </span>
                  <span class="text-sm text-gray-500">
                    {{ item.indexed_files_count || 0 }} souborů
                  </span>
                </div>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <!-- Status indexování -->
              <div v-if="item.indexing_status" class="text-sm">
                <span v-if="item.indexing_status.status === 'indexing'" class="text-blue-600">
                  Indexování... {{ item.indexing_status.progress }}%
                </span>
                <span v-else-if="item.indexing_status.status === 'completed'" class="text-green-600">
                  Dokončeno
                </span>
                <span v-else-if="item.indexing_status.status === 'error'" class="text-red-600">
                  Chyba
                </span>
              </div>

              <!-- Tlačítka -->
              <button
                v-if="item.indexing_status?.status !== 'indexing'"
                @click="startIndexing(item.id)"
                class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                <Icon name="heroicons:arrow-path" class="w-4 h-4 inline mr-1" />
                Indexovat
              </button>

              <button
                @click="toggleItem(item)"
                :class="item.enabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'"
                class="px-3 py-1 text-white text-sm rounded"
              >
                {{ item.enabled ? 'Aktivní' : 'Neaktivní' }}
              </button>

              <button
                @click="deleteItem(item.id)"
                class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
              >
                <Icon name="heroicons:trash" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal pro procházení souborů -->
    <div v-if="showBrowseModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[80vh] overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">Vybrat soubor nebo složku</h3>
            <button @click="showBrowseModal = false" class="text-gray-400 hover:text-gray-600">
              <Icon name="heroicons:x-mark" class="w-6 h-6" />
            </button>
          </div>
        </div>

        <div class="p-6">
          <!-- Breadcrumb -->
          <div class="flex items-center space-x-2 mb-4 text-sm">
            <button
              v-for="(part, index) in breadcrumb"
              :key="index"
              @click="navigateToBreadcrumb(index)"
              class="text-blue-600 hover:text-blue-800"
            >
              {{ part }}
            </button>
          </div>

          <!-- Seznam souborů a složek -->
          <div class="space-y-2 max-h-96 overflow-y-auto">
            <div
              v-for="item in browseItems"
              :key="item.path"
              @click="selectBrowseItem(item)"
              class="flex items-center p-3 hover:bg-gray-100 rounded cursor-pointer"
            >
              <Icon
                :name="item.type === 'folder' ? 'heroicons:folder' : 'heroicons:document'"
                class="w-5 h-5 text-gray-600 mr-3"
              />
              <span class="text-gray-900">{{ item.name }}</span>
              <span v-if="item.size" class="ml-auto text-sm text-gray-500">
                {{ formatFileSize(item.size) }}
              </span>
            </div>
          </div>

          <div v-if="browseError" class="mt-4 p-3 bg-red-100 text-red-700 rounded">
            {{ browseError }}
          </div>
        </div>

        <div class="p-6 border-t border-gray-200">
          <div class="flex justify-end space-x-3">
            <button
              @click="showBrowseModal = false"
              class="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
            >
              Zrušit
            </button>
            <button
              @click="selectCurrentPath"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Vybrat aktuální cestu
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useApi } from '~/composables/useApi'

const api = useApi()

// Reaktivní data
const watchedItems = ref([])
const stats = ref({})
const showBrowseModal = ref(false)
const browseItems = ref([])
const browseError = ref('')
const currentBrowsePath = ref('/home')
const breadcrumb = ref(['home'])

const newItem = ref({
  path: '',
  name: '',
  type: 'folder',
  recursive: false,
  fileTypesInput: ''
})

// Computed properties
const indexingCount = computed(() => {
  return watchedItems.value.filter(item => 
    item.indexing_status?.status === 'indexing'
  ).length
})

// Metody
const loadWatchedItems = async () => {
  try {
    const response = await api.getWatchedItems()
    watchedItems.value = response
  } catch (error) {
    console.error('Chyba při načítání sledovaných položek:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await api.getFilesStats()
    stats.value = response
  } catch (error) {
    console.error('Chyba při načítání statistik:', error)
  }
}

const addWatchedItem = async () => {
  try {
    // Parsuje typy souborů
    const fileTypes = newItem.value.fileTypesInput
      ? newItem.value.fileTypesInput.split(',').map(t => t.trim())
      : []

    const response = await api.addWatchedItem({
      path: newItem.value.path,
      name: newItem.value.name,
      type: newItem.value.type,
      recursive: newItem.value.recursive,
      file_types: fileTypes
    })

    // Reset formuláře
    newItem.value = {
      path: '',
      name: '',
      type: 'folder',
      recursive: false,
      fileTypesInput: ''
    }

    // Znovu načte data
    await loadWatchedItems()
    await loadStats()
  } catch (error) {
    console.error('Chyba při přidávání položky:', error)
  }
}

const deleteItem = async (itemId) => {
  if (!confirm('Opravdu chcete smazat tuto položku?')) return

  try {
    await api.deleteWatchedItem(itemId)
    await loadWatchedItems()
    await loadStats()
  } catch (error) {
    console.error('Chyba při mazání položky:', error)
  }
}

const toggleItem = async (item) => {
  try {
    await api.updateWatchedItem(item.id, { enabled: !item.enabled })
    await loadWatchedItems()
  } catch (error) {
    console.error('Chyba při přepínání položky:', error)
  }
}

const startIndexing = async (itemId) => {
  try {
    await api.startIndexing(itemId)
    await loadWatchedItems()
  } catch (error) {
    console.error('Chyba při spouštění indexování:', error)
  }
}

const loadBrowseData = async (path) => {
  try {
    browseError.value = ''
    const response = await api.browseFiles(path)
    browseItems.value = response.items
    currentBrowsePath.value = response.current_path
    breadcrumb.value = response.current_path.split('/').filter(Boolean)
  } catch (error) {
    browseError.value = 'Chyba při načítání: ' + error.message
  }
}

const selectBrowseItem = (item) => {
  if (item.type === 'folder') {
    loadBrowseData(item.path)
  } else {
    // Vybere soubor
    newItem.value.path = item.path
    newItem.value.name = item.name
    newItem.value.type = 'file'
    showBrowseModal.value = false
  }
}

const selectCurrentPath = () => {
  newItem.value.path = currentBrowsePath.value
  newItem.value.name = currentBrowsePath.value.split('/').pop() || 'root'
  newItem.value.type = 'folder'
  showBrowseModal.value = false
}

const navigateToBreadcrumb = (index) => {
  const path = '/' + breadcrumb.value.slice(0, index + 1).join('/')
  loadBrowseData(path)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Watchers
watch(showBrowseModal, (newVal) => {
  if (newVal) {
    loadBrowseData('/home')
  }
})

// Načtení dat při mountování
onMounted(async () => {
  await loadWatchedItems()
  await loadStats()
})
</script> 