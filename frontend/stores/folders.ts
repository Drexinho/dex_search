import { defineStore } from 'pinia'

export interface WatchedFolder {
  id?: string
  path: string
  tags: string[]
  recursive: boolean
  file_types: string[]
  reindex_on_change: boolean
  enabled: boolean
  last_indexed?: string
  next_scheduled?: string
  file_count: number
}

export interface IndexStatus {
  folder_id: string
  status: string
  progress: number
  files_processed: number
  total_files: number
  start_time?: string
  end_time?: string
  error_message?: string
}

export const useFoldersStore = defineStore('folders', () => {
  const folders = ref<WatchedFolder[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const indexingFolders = ref<string[]>([])

  const api = useApi()

  // Actions
  const loadFolders = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.getFolders()
      folders.value = response
    } catch (err: any) {
      error.value = err.message || 'Chyba při načítání složek'
      console.error('Failed to load folders:', err)
    } finally {
      loading.value = false
    }
  }

  const addFolder = async (folderData: Omit<WatchedFolder, 'id'>) => {
    loading.value = true
    error.value = null
    
    try {
      const newFolder = await api.createFolder(folderData)
      folders.value.push(newFolder)
      return newFolder
    } catch (err: any) {
      error.value = err.message || 'Chyba při přidávání složky'
      console.error('Failed to add folder:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateFolder = async (id: string, updates: Partial<WatchedFolder>) => {
    loading.value = true
    error.value = null
    
    try {
      const updatedFolder = await api.updateFolder(id, updates)
      const index = folders.value.findIndex(f => f.id === id)
      if (index !== -1) {
        folders.value[index] = updatedFolder
      }
      return updatedFolder
    } catch (err: any) {
      error.value = err.message || 'Chyba při aktualizaci složky'
      console.error('Failed to update folder:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteFolder = async (id: string) => {
    loading.value = true
    error.value = null
    
    try {
      await api.deleteFolder(id)
      const index = folders.value.findIndex(f => f.id === id)
      if (index !== -1) {
        folders.value.splice(index, 1)
      }
    } catch (err: any) {
      error.value = err.message || 'Chyba při odstraňování složky'
      console.error('Failed to delete folder:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const triggerIndex = async (id: string) => {
    if (indexingFolders.value.includes(id)) return

    indexingFolders.value.push(id)
    error.value = null
    
    try {
      await api.triggerIndex(id)
    } catch (err: any) {
      error.value = err.message || 'Chyba při spouštění indexace'
      console.error('Failed to trigger index:', err)
      throw err
    } finally {
      const index = indexingFolders.value.indexOf(id)
      if (index !== -1) {
        indexingFolders.value.splice(index, 1)
      }
    }
  }

  const getFolderStatus = async (id: string) => {
    try {
      const status = await api.getFolderStatus(id)
      return status
    } catch (err: any) {
      console.error('Failed to get folder status:', err)
      throw err
    }
  }

  const validatePath = async (path: string) => {
    try {
      const validation = await api.validatePath(path)
      return validation
    } catch (err: any) {
      console.error('Failed to validate path:', err)
      throw err
    }
  }

  const toggleFolder = async (id: string) => {
    const folder = folders.value.find(f => f.id === id)
    if (!folder) return

    try {
      await updateFolder(id, { enabled: !folder.enabled })
    } catch (err) {
      console.error('Failed to toggle folder:', err)
      throw err
    }
  }

  // Getters
  const getFolderById = (id: string) => {
    return folders.value.find(f => f.id === id)
  }

  const getEnabledFolders = () => {
    return folders.value.filter(f => f.enabled)
  }

  const getFoldersByTag = (tag: string) => {
    return folders.value.filter(f => f.tags.includes(tag))
  }

  const getTotalFileCount = () => {
    return folders.value.reduce((total, folder) => total + (folder.file_count || 0), 0)
  }

  const getIndexingFolders = () => {
    return folders.value.filter(f => indexingFolders.value.includes(f.id!))
  }

  return {
    // State
    folders: readonly(folders),
    loading: readonly(loading),
    error: readonly(error),
    indexingFolders: readonly(indexingFolders),

    // Actions
    loadFolders,
    addFolder,
    updateFolder,
    deleteFolder,
    triggerIndex,
    getFolderStatus,
    validatePath,
    toggleFolder,

    // Getters
    getFolderById,
    getEnabledFolders,
    getFoldersByTag,
    getTotalFileCount,
    getIndexingFolders
  }
}) 