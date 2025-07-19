<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Nastavení</h1>
      <p class="text-gray-600 dark:text-gray-400">
        Konfigurace aplikace a systémové informace
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- General settings -->
      <UCard>
        <template #header>
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5 text-blue-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Obecná nastavení</h3>
          </div>
        </template>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Název aplikace
            </label>
            <UInput v-model="settings.app_name" disabled />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Verze
            </label>
            <UInput v-model="settings.version" disabled />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Debug mód
            </label>
            <UCheckbox v-model="settings.debug" disabled />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              API Base URL
            </label>
            <UInput v-model="settings.api_base" disabled />
          </div>
        </div>
      </UCard>

      <!-- System info -->
      <UCard>
        <template #header>
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-cpu-chip" class="w-5 h-5 text-green-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Systémové informace</h3>
          </div>
        </template>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">CPU jádra</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ systemInfo.cpu?.count || 'N/A' }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">CPU frekvence</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ systemInfo.cpu?.frequency_mhz ? `${systemInfo.cpu.frequency_mhz} MHz` : 'N/A' }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">RAM celkem</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ systemInfo.memory?.total_gb ? `${systemInfo.memory.total_gb} GB` : 'N/A' }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">RAM dostupná</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ systemInfo.memory?.available_gb ? `${systemInfo.memory.available_gb} GB` : 'N/A' }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Disk celkem</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ systemInfo.disk?.total_gb ? `${systemInfo.disk.total_gb} GB` : 'N/A' }}
              </p>
            </div>
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Disk volný</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ systemInfo.disk?.free_gb ? `${systemInfo.disk.free_gb} GB` : 'N/A' }}
              </p>
            </div>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Models configuration -->
    <UCard>
      <template #header>
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-brain" class="w-5 h-5 text-purple-500" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Konfigurace modelů</h3>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- LLM Models -->
        <div>
          <h4 class="text-md font-medium text-gray-900 dark:text-white mb-4">LLM Modely</h4>
          <div class="space-y-3">
            <div
              v-for="model in availableModels"
              :key="model.id"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ model.name }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ model.description }}</p>
                  <p class="text-xs text-gray-400 dark:text-gray-500">Velikost: {{ model.size }}</p>
                </div>
                <div class="flex items-center space-x-2">
                  <UBadge
                    v-if="model.recommended"
                    label="Doporučený"
                    color="green"
                    variant="soft"
                    size="sm"
                  />
                  <UButton
                    :label="model.id === selectedLLMModel ? 'Aktivní' : 'Vybrat'"
                    :color="model.id === selectedLLMModel ? 'green' : 'blue'"
                    variant="soft"
                    size="sm"
                    @click="selectLLMModel(model.id)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Embedding Models -->
        <div>
          <h4 class="text-md font-medium text-gray-900 dark:text-white mb-4">Embedding Modely</h4>
          <div class="space-y-3">
            <div
              v-for="model in availableEmbeddingModels"
              :key="model.id"
              class="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-gray-900 dark:text-white">{{ model.name }}</p>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ model.description }}</p>
                  <p class="text-xs text-gray-400 dark:text-gray-500">Velikost: {{ model.size }}</p>
                </div>
                <div class="flex items-center space-x-2">
                  <UBadge
                    v-if="model.recommended"
                    label="Doporučený"
                    color="green"
                    variant="soft"
                    size="sm"
                  />
                  <UButton
                    :label="model.id === selectedEmbeddingModel ? 'Aktivní' : 'Vybrat'"
                    :color="model.id === selectedEmbeddingModel ? 'green' : 'blue'"
                    variant="soft"
                    size="sm"
                    @click="selectEmbeddingModel(model.id)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </UCard>

    <!-- File formats -->
    <UCard>
      <template #header>
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-document" class="w-5 h-5 text-blue-500" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Podporované formáty</h3>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="format in fileFormats"
          :key="format.extension"
          class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div>
            <p class="font-medium text-gray-900 dark:text-white">{{ format.name }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ format.description }}</p>
          </div>
          <div>
            <UBadge
              :label="format.supported ? 'Podporováno' : 'Nepodporováno'"
              :color="format.supported ? 'green' : 'gray'"
              variant="soft"
              size="sm"
            />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Vector databases -->
    <UCard>
      <template #header>
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-database" class="w-5 h-5 text-orange-500" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Vektorové databáze</h3>
        </div>
      </template>

      <div class="space-y-3">
        <div
          v-for="db in vectorDBs"
          :key="db.id"
          class="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div>
            <p class="font-medium text-gray-900 dark:text-white">{{ db.name }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ db.description }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <UBadge
              v-if="db.recommended"
              label="Doporučená"
              color="green"
              variant="soft"
              size="sm"
            />
            <UButton
              :label="db.id === selectedVectorDB ? 'Aktivní' : 'Vybrat'"
              :color="db.id === selectedVectorDB ? 'green' : 'blue'"
              variant="soft"
              size="sm"
              @click="selectVectorDB(db.id)"
            />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Actions -->
    <UCard>
      <template #header>
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-wrench-screwdriver" class="w-5 h-5 text-red-500" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Akce</h3>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UButton
          label="Test připojení"
          icon="i-heroicons-signal"
          color="blue"
          variant="soft"
          @click="testConnection"
          :loading="testingConnection"
        />
        
        <UButton
          label="Vymazat všechna data"
          icon="i-heroicons-trash"
          color="red"
          variant="soft"
          @click="clearAllData"
          :loading="clearingData"
        />
        
        <UButton
          label="Exportovat logy"
          icon="i-heroicons-arrow-down-tray"
          color="gray"
          variant="soft"
          @click="exportLogs"
        />
        
        <UButton
          label="Restartovat služby"
          icon="i-heroicons-arrow-path"
          color="yellow"
          variant="soft"
          @click="restartServices"
          :loading="restarting"
        />
      </div>
    </UCard>
  </div>
</template>

<script setup>
// Page metadata
useHead({
  title: 'Nastavení - Dex Search'
})

// Reactive data
const testingConnection = ref(false)
const clearingData = ref(false)
const restarting = ref(false)

const settings = ref({
  app_name: 'Dex Search',
  version: '1.0.0',
  debug: true,
  api_base: 'http://localhost:8000'
})

const systemInfo = ref({
  cpu: {},
  memory: {},
  disk: {}
})

const selectedLLMModel = ref('microsoft/phi-3-mini-4k-instruct')
const selectedEmbeddingModel = ref('BAAI/bge-base-en-v1.5')
const selectedVectorDB = ref('chromadb')

const availableModels = ref([
  {
    id: 'microsoft/phi-3-mini-4k-instruct',
    name: 'Phi-3 Mini (4K)',
    description: 'Efektivní model pro slabší hardware',
    size: '3.8B',
    recommended: true
  },
  {
    id: 'mistralai/Mistral-7B-Instruct-v0.2',
    name: 'Mistral-7B Instruct',
    description: 'Lehký a výkonný model',
    size: '7B',
    recommended: false
  },
  {
    id: 'meta-llama/Meta-Llama-3-8B',
    name: 'Llama-3 8B',
    description: 'Přesný model, náročnější na hardware',
    size: '8B',
    recommended: false
  }
])

const availableEmbeddingModels = ref([
  {
    id: 'BAAI/bge-base-en-v1.5',
    name: 'BGE Base EN v1.5',
    description: 'Výkonný embedding model pro angličtinu',
    size: '0.5GB',
    recommended: true
  },
  {
    id: 'sentence-transformers/all-MiniLM-L6-v2',
    name: 'All-MiniLM-L6-v2',
    description: 'Rychlý a kompaktní model',
    size: '0.1GB',
    recommended: false
  }
])

const fileFormats = ref([
  {
    extension: '.pdf',
    name: 'PDF',
    description: 'Portable Document Format',
    supported: true
  },
  {
    extension: '.docx',
    name: 'Word Document',
    description: 'Microsoft Word dokument',
    supported: true
  },
  {
    extension: '.txt',
    name: 'Text File',
    description: 'Prostý text',
    supported: true
  },
  {
    extension: '.md',
    name: 'Markdown',
    description: 'Markdown dokument',
    supported: true
  },
  {
    extension: '.rtf',
    name: 'Rich Text Format',
    description: 'Rich Text Format',
    supported: false
  }
])

const vectorDBs = ref([
  {
    id: 'chromadb',
    name: 'ChromaDB',
    description: 'Jednoduchá, lokální vektorová DB',
    recommended: true
  },
  {
    id: 'faiss',
    name: 'FAISS',
    description: 'Rychlá vektorová DB od Facebooku',
    recommended: false
  },
  {
    id: 'weaviate',
    name: 'Weaviate',
    description: 'Pokročilá vektorová DB',
    recommended: false
  }
])

// Methods
const selectLLMModel = async (modelId) => {
  selectedLLMModel.value = modelId
  // TODO: Implementovat změnu modelu na backendu
  console.log('Selected LLM model:', modelId)
}

const selectEmbeddingModel = async (modelId) => {
  selectedEmbeddingModel.value = modelId
  // TODO: Implementovat změnu modelu na backendu
  console.log('Selected embedding model:', modelId)
}

const selectVectorDB = async (dbId) => {
  selectedVectorDB.value = dbId
  // TODO: Implementovat změnu DB na backendu
  console.log('Selected vector DB:', dbId)
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    const response = await $fetch('/api/settings/test-connection', {
      method: 'POST'
    })
    console.log('Connection test:', response)
  } catch (error) {
    console.error('Connection test failed:', error)
  } finally {
    testingConnection.value = false
  }
}

const clearAllData = async () => {
  if (!confirm('Opravdu chcete vymazat všechna data? Tato akce je nevratná.')) {
    return
  }

  clearingData.value = true
  try {
    await $fetch('/api/settings/clear-data', {
      method: 'POST'
    })
    console.log('All data cleared')
  } catch (error) {
    console.error('Failed to clear data:', error)
  } finally {
    clearingData.value = false
  }
}

const exportLogs = async () => {
  try {
    const logs = await $fetch('/api/settings/logs')
    console.log('Logs:', logs)
    // TODO: Implementovat export do souboru
  } catch (error) {
    console.error('Failed to export logs:', error)
  }
}

const restartServices = async () => {
  restarting.value = true
  try {
    // TODO: Implementovat restart služeb
    console.log('Restarting services...')
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulace
  } catch (error) {
    console.error('Failed to restart services:', error)
  } finally {
    restarting.value = false
  }
}

const loadSettings = async () => {
  try {
    const response = await $fetch('/api/settings')
    settings.value = { ...settings.value, ...response }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

const loadSystemInfo = async () => {
  try {
    const response = await $fetch('/api/settings/system-info')
    systemInfo.value = response
  } catch (error) {
    console.error('Failed to load system info:', error)
  }
}

const loadModels = async () => {
  try {
    const [modelsResponse, embeddingModelsResponse] = await Promise.all([
      $fetch('/api/settings/models'),
      $fetch('/api/settings/embedding-models')
    ])
    
    availableModels.value = modelsResponse.models
    availableEmbeddingModels.value = embeddingModelsResponse.models
  } catch (error) {
    console.error('Failed to load models:', error)
  }
}

const loadFileFormats = async () => {
  try {
    const response = await $fetch('/api/settings/file-formats')
    fileFormats.value = response.formats
  } catch (error) {
    console.error('Failed to load file formats:', error)
  }
}

const loadVectorDBs = async () => {
  try {
    const response = await $fetch('/api/settings/vector-dbs')
    vectorDBs.value = response.databases
  } catch (error) {
    console.error('Failed to load vector DBs:', error)
  }
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    loadSettings(),
    loadSystemInfo(),
    loadModels(),
    loadFileFormats(),
    loadVectorDBs()
  ])
})
</script> 