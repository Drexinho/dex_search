<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Dashboard - Dex Search</h1>
      <p class="text-gray-600">Přehled vašeho systému pro vyhledávání v souborech</p>
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

    <!-- Rychlé akce -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Rychlé akce</h2>
        <div class="space-y-3">
          <NuxtLink
            to="/files"
            class="flex items-center p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <Icon name="heroicons:folder-plus" class="w-6 h-6 text-blue-600 mr-3" />
            <div>
              <p class="font-medium text-gray-900">Přidat soubory/složky</p>
              <p class="text-sm text-gray-600">Přidejte nové položky k indexování</p>
            </div>
          </NuxtLink>

          <NuxtLink
            to="/search"
            class="flex items-center p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <Icon name="heroicons:magnifying-glass" class="w-6 h-6 text-green-600 mr-3" />
            <div>
              <p class="font-medium text-gray-900">Vyhledávání</p>
              <p class="text-sm text-gray-600">Vyhledejte v indexovaných souborech</p>
            </div>
          </NuxtLink>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Poslední aktivita</h2>
        <div v-if="recentItems.length > 0" class="space-y-3">
          <div
            v-for="item in recentItems"
            :key="item.id"
            class="flex items-center p-3 bg-gray-50 rounded-lg"
          >
            <Icon
              :name="item.type === 'folder' ? 'heroicons:folder' : 'heroicons:document'"
              class="w-5 h-5 text-gray-600 mr-3"
            />
            <div class="flex-1">
              <p class="font-medium text-gray-900">{{ item.name }}</p>
              <p class="text-sm text-gray-600">{{ item.path }}</p>
            </div>
            <span class="text-xs text-gray-500">
              {{ formatDate(item.created_at) }}
            </span>
          </div>
        </div>
        <div v-else class="text-center py-8">
          <Icon name="heroicons:clock" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-600">Žádná nedávná aktivita</p>
        </div>
      </div>
    </div>

    <!-- Stav systému -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Stav systému</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="flex items-center">
          <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
          <span class="text-sm text-gray-700">API server</span>
        </div>
        <div class="flex items-center">
          <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
          <span class="text-sm text-gray-700">Databáze</span>
        </div>
        <div class="flex items-center">
          <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
          <span class="text-sm text-gray-700">Indexování</span>
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
const stats = ref({})
const watchedItems = ref([])

// Computed properties
const indexingCount = computed(() => {
  return watchedItems.value.filter(item => 
    item.indexing_status?.status === 'indexing'
  ).length
})

const recentItems = computed(() => {
  return watchedItems.value
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5)
})

// Metody
const loadStats = async () => {
  try {
    const response = await api.getFilesStats()
    stats.value = response
  } catch (error) {
    console.error('Chyba při načítání statistik:', error)
  }
}

const loadWatchedItems = async () => {
  try {
    const response = await api.getWatchedItems()
    watchedItems.value = response
  } catch (error) {
    console.error('Chyba při načítání sledovaných položek:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('cs-CZ')
}

// Načtení dat při mountování
onMounted(async () => {
  await loadStats()
  await loadWatchedItems()
})
</script> 