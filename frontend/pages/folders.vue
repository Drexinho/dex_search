<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Sledované složky</h1>
        <p class="text-gray-600 dark:text-gray-400">Spravujte složky, které chcete indexovat</p>
      </div>
      <UButton
        label="Přidat složku"
        icon="i-heroicons-plus"
        @click="showAddFolderModal = true"
      />
    </div>

    <!-- Folders grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      <UCard
        v-for="folder in folders"
        :key="folder.id"
        class="relative"
      >
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <UIcon name="i-heroicons-folder" class="w-5 h-5 text-blue-500" />
              <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                {{ getFolderName(folder.path) }}
              </h3>
            </div>
            <UDropdown :items="getFolderActions(folder)">
              <UButton
                icon="i-heroicons-ellipsis-vertical"
                color="gray"
                variant="ghost"
                size="sm"
              />
            </UDropdown>
          </div>
        </template>

        <div class="space-y-4">
          <!-- Path -->
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Cesta</p>
            <p class="text-sm text-gray-900 dark:text-white font-mono truncate">
              {{ folder.path }}
            </p>
          </div>

          <!-- Tags -->
          <div v-if="folder.tags && folder.tags.length">
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Tagy</p>
            <div class="flex flex-wrap gap-1">
              <UBadge
                v-for="tag in folder.tags"
                :key="tag"
                color="blue"
                variant="soft"
                size="sm"
              >
                {{ tag }}
              </UBadge>
            </div>
          </div>

          <!-- Settings -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-gray-500 dark:text-gray-400">Rekurze</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ folder.recursive ? 'Zapnuto' : 'Vypnuto' }}
              </p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Formáty</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ folder.file_types.length }} typů
              </p>
            </div>
          </div>

          <!-- Status -->
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full" :class="getStatusColor(folder)"></div>
              <span class="text-sm text-gray-600 dark:text-gray-400">
                {{ getStatusText(folder) }}
              </span>
            </div>
            <UButton
              v-if="folder.enabled"
              size="sm"
              color="blue"
              variant="soft"
              @click="triggerIndex(folder.id)"
              :loading="indexingFolders.includes(folder.id)"
            >
              Indexovat
            </UButton>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-gray-500 dark:text-gray-400">Soubory</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ folder.file_count || 0 }}
              </p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Poslední indexace</p>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ formatDate(folder.last_indexed) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Status indicator -->
        <div class="absolute top-2 right-2">
          <UButton
            :icon="folder.enabled ? 'i-heroicons-eye' : 'i-heroicons-eye-slash'"
            :color="folder.enabled ? 'green' : 'gray'"
            variant="ghost"
            size="xs"
            @click="toggleFolder(folder.id)"
          />
        </div>
      </UCard>
    </div>

    <!-- Empty state -->
    <UCard v-if="folders.length === 0" class="text-center py-12">
      <div class="flex flex-col items-center space-y-4">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
          <UIcon name="i-heroicons-folder" class="w-8 h-8 text-gray-400" />
        </div>
        <div>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">Žádné sledované složky</h3>
          <p class="text-gray-500 dark:text-gray-400">
            Přidejte první složku k indexaci
          </p>
        </div>
        <UButton
          label="Přidat složku"
          icon="i-heroicons-plus"
          @click="showAddFolderModal = true"
        />
      </div>
    </UCard>

    <!-- Add folder modal -->
    <UModal v-model="showAddFolderModal">
      <UCard>
        <template #header>
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-folder-plus" class="w-5 h-5 text-blue-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Přidat novou složku
            </h3>
          </div>
        </template>

        <form @submit.prevent="addFolder" class="space-y-4">
          <!-- Path input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Cesta k složce
            </label>
            <div class="flex space-x-2">
              <UInput
                v-model="newFolder.path"
                placeholder="/cesta/k/složce"
                :error="pathError"
                @blur="validatePath"
                class="flex-1"
              />
              <UButton
                icon="i-heroicons-folder-open"
                color="blue"
                variant="soft"
                @click="showBrowseModal = true"
                title="Procházet složky"
              />
            </div>
          </div>

          <!-- Tags -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tagy (volitelné)
            </label>
            <UInput
              v-model="newFolder.tagsInput"
              placeholder="práce, důležité, 2024"
            />
            <p class="text-xs text-gray-500 mt-1">
              Oddělte tagy čárkami
            </p>
          </div>

          <!-- Settings -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="flex items-center space-x-2">
                <UCheckbox v-model="newFolder.recursive" />
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  Zahrnout podsložky
                </span>
              </label>
            </div>
            <div>
              <label class="flex items-center space-x-2">
                <UCheckbox v-model="newFolder.reindex_on_change" />
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  Reindex při změnách
                </span>
              </label>
            </div>
          </div>

          <!-- File types -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Podporované formáty
            </label>
            <div class="grid grid-cols-2 gap-2">
              <label
                v-for="format in availableFormats"
                :key="format.extension"
                class="flex items-center space-x-2"
              >
                <UCheckbox
                  v-model="newFolder.file_types"
                  :value="format.extension"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ format.name }}
                </span>
              </label>
            </div>
          </div>
        </form>

        <template #footer>
          <div class="flex justify-end space-x-2">
            <UButton
              label="Zrušit"
              color="gray"
              variant="soft"
              @click="showAddFolderModal = false"
            />
            <UButton
              label="Přidat složku"
              icon="i-heroicons-plus"
              @click="addFolder"
              :loading="addingFolder"
              :disabled="!newFolder.path"
            />
          </div>
        </template>
      </UCard>
    </UModal>

    <!-- Browse folders modal -->
    <UModal v-model="showBrowseModal" size="lg">
      <UCard>
        <template #header>
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-folder-open" class="w-5 h-5 text-blue-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              Procházet složky
            </h3>
          </div>
        </template>

        <div class="space-y-4">
          <!-- Breadcrumb -->
          <div class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <UButton
              v-if="browseData.parent_path"
              icon="i-heroicons-chevron-left"
              color="gray"
              variant="ghost"
              size="sm"
              @click="navigateToParent"
            />
            <span class="font-mono">{{ browseData.current_path || '/' }}</span>
          </div>

          <!-- Error message -->
          <UAlert
            v-if="browseData.error"
            color="red"
            variant="soft"
            :title="browseData.error"
          />

          <!-- Folders list -->
          <div class="max-h-96 overflow-y-auto">
            <div
              v-for="folder in browseData.folders"
              :key="folder.path"
              class="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg cursor-pointer"
              @click="selectFolder(folder.path)"
            >
              <div class="flex items-center space-x-3">
                <UIcon name="i-heroicons-folder" class="w-5 h-5 text-blue-500" />
                <span class="font-medium text-gray-900 dark:text-white">
                  {{ folder.name }}
                </span>
              </div>
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 text-gray-400" />
            </div>

            <!-- Empty state -->
            <div
              v-if="browseData.folders.length === 0 && !browseData.error"
              class="text-center py-8 text-gray-500 dark:text-gray-400"
            >
              Žádné složky k zobrazení
            </div>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-end space-x-2">
            <UButton
              label="Zrušit"
              color="gray"
              variant="soft"
              @click="showBrowseModal = false"
            />
            <UButton
              label="Vybrat aktuální složku"
              icon="i-heroicons-check"
              @click="selectCurrentFolder"
              :disabled="!browseData.current_path"
            />
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup>
// Page metadata
useHead({
  title: 'Složky - Dex Search'
})

// Reactive data
const showAddFolderModal = ref(false)
const showBrowseModal = ref(false)
const addingFolder = ref(false)
const indexingFolders = ref([])
const pathError = ref('')

const browseData = ref({
  folders: [],
  current_path: '',
  parent_path: null,
  error: ''
})

const folders = ref([])

const newFolder = ref({
  path: '',
  tagsInput: '',
  recursive: true,
  reindex_on_change: true,
  file_types: ['.pdf', '.docx', '.txt']
})

const availableFormats = ref([
  { extension: '.pdf', name: 'PDF' },
  { extension: '.docx', name: 'Word' },
  { extension: '.doc', name: 'Word (Legacy)' },
  { extension: '.txt', name: 'Text' },
  { extension: '.md', name: 'Markdown' }
])

// Computed
const getFolderName = (path) => {
  return path.split('/').pop() || path
}

const getStatusColor = (folder) => {
  if (!folder.enabled) return 'bg-gray-400'
  if (folder.last_indexed) return 'bg-green-500'
  return 'bg-yellow-500'
}

const getStatusText = (folder) => {
  if (!folder.enabled) return 'Vypnuto'
  if (folder.last_indexed) return 'Indexováno'
  return 'Čeká na indexaci'
}

const getFolderActions = (folder) => [
  {
    label: 'Upravit',
    icon: 'i-heroicons-pencil-square',
    click: () => editFolder(folder)
  },
  {
    label: folder.enabled ? 'Vypnout' : 'Zapnout',
    icon: folder.enabled ? 'i-heroicons-eye-slash' : 'i-heroicons-eye',
    click: () => toggleFolder(folder.id)
  },
  {
    label: 'Indexovat nyní',
    icon: 'i-heroicons-arrow-path',
    click: () => triggerIndex(folder.id)
  },
  {
    label: 'Odstranit',
    icon: 'i-heroicons-trash',
    click: () => deleteFolder(folder.id)
  }
]

// API composable
const api = useApi()

// Methods
const validatePath = async () => {
  if (!newFolder.value.path) {
    pathError.value = ''
    return
  }

  try {
    const response = await api.validatePath(newFolder.value.path)
    
    if (!response.valid) {
      pathError.value = response.error
    } else {
      pathError.value = ''
    }
  } catch (error) {
    pathError.value = 'Chyba při validaci cesty'
  }
}

// Browse methods
const loadBrowseData = async (path = '') => {
  try {
    const response = await api.browseFolders(path)
    browseData.value = response
  } catch (error) {
    browseData.value = {
      folders: [],
      current_path: path,
      parent_path: null,
      error: 'Chyba při načítání složek'
    }
  }
}

const selectFolder = async (path) => {
  await loadBrowseData(path)
}

const navigateToParent = async () => {
  if (browseData.value.parent_path) {
    await loadBrowseData(browseData.value.parent_path)
  }
}

const selectCurrentFolder = () => {
  newFolder.value.path = browseData.value.current_path
  showBrowseModal.value = false
  validatePath()
}

// Watcher pro načtení složek při otevření modalu
watch(showBrowseModal, async (newValue) => {
  if (newValue) {
    await loadBrowseData('/home')
  }
})

const addFolder = async () => {
  if (!newFolder.value.path) return

  addingFolder.value = true
  try {
    const folderData = {
      path: newFolder.value.path,
      tags: newFolder.value.tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag),
      recursive: newFolder.value.recursive,
      file_types: newFolder.value.file_types,
      reindex_on_change: newFolder.value.reindex_on_change,
      enabled: true
    }

    const newFolderResponse = await api.createFolder(folderData)

    folders.value.push(newFolderResponse)
    showAddFolderModal.value = false
    
    // Reset form
    newFolder.value = {
      path: '',
      tagsInput: '',
      recursive: true,
      reindex_on_change: true,
      file_types: ['.pdf', '.docx', '.txt']
    }
  } catch (error) {
    console.error('Chyba při přidávání složky:', error)
  } finally {
    addingFolder.value = false
  }
}

const toggleFolder = async (folderId) => {
  const folder = folders.value.find(f => f.id === folderId)
  if (!folder) return

  try {
    const updatedFolder = await api.updateFolder(folderId, { enabled: !folder.enabled })

    const index = folders.value.findIndex(f => f.id === folderId)
    if (index !== -1) {
      folders.value[index] = updatedFolder
    }
  } catch (error) {
    console.error('Chyba při přepínání složky:', error)
  }
}

const triggerIndex = async (folderId) => {
  if (indexingFolders.value.includes(folderId)) return

  indexingFolders.value.push(folderId)
  try {
    await api.triggerIndex(folderId)
  } catch (error) {
    console.error('Chyba při spouštění indexace:', error)
  } finally {
    const index = indexingFolders.value.indexOf(folderId)
    if (index !== -1) {
      indexingFolders.value.splice(index, 1)
    }
  }
}

const editFolder = (folder) => {
  // TODO: Implementovat editaci složky
  console.log('Edit folder:', folder)
}

const deleteFolder = async (folderId) => {
  if (!confirm('Opravdu chcete odstranit tuto složku?')) return

  try {
    await api.deleteFolder(folderId)

    const index = folders.value.findIndex(f => f.id === folderId)
    if (index !== -1) {
      folders.value.splice(index, 1)
    }
  } catch (error) {
    console.error('Chyba při odstraňování složky:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Nikdy'
  return new Date(dateString).toLocaleString('cs-CZ')
}

// Load data on mount
onMounted(async () => {
  try {
    const response = await api.getFolders()
    folders.value = response
  } catch (error) {
    console.error('Chyba při načítání složek:', error)
  }
})
</script> 