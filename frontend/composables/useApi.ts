export const useApi = () => {
  const baseURL = 'http://localhost:8000'

  const api = {
    // Health check
    async healthCheck() {
      return await $fetch(`${baseURL}/api/health`)
    },

    // Watched items (files/folders)
    async getWatchedItems() {
      return await $fetch(`${baseURL}/api/files/`)
    },

    async addWatchedItem(data: {
      path: string
      name: string
      type: string
      recursive?: boolean
      file_types?: string[]
    }) {
      return await $fetch(`${baseURL}/api/files/`, {
        method: 'POST',
        body: data
      })
    },

    async deleteWatchedItem(itemId: number) {
      return await $fetch(`${baseURL}/api/files/${itemId}`, {
        method: 'DELETE'
      })
    },

    async updateWatchedItem(itemId: number, data: any) {
      return await $fetch(`${baseURL}/api/files/${itemId}`, {
        method: 'PUT',
        body: data
      })
    },

    async startIndexing(itemId: number) {
      return await $fetch(`${baseURL}/api/files/${itemId}/index`, {
        method: 'POST'
      })
    },

    async getIndexingStatus(itemId: number) {
      return await $fetch(`${baseURL}/api/files/${itemId}/indexing-status`)
    },

    // File browsing
    async browseFiles(path: string) {
      // Zajistíme, že cesta začíná s /
      const normalizedPath = path.startsWith('/') ? path : `/${path}`
      return await $fetch(`${baseURL}/api/files/browse${normalizedPath}`)
    },

    async validatePath(path: string) {
      return await $fetch(`${baseURL}/api/files/validate-path?path=${encodeURIComponent(path)}`)
    },

    // Stats
    async getFilesStats() {
      return await $fetch(`${baseURL}/api/files/stats`)
    },

    // Search
    async searchFiles(query: string, limit: number = 50) {
      return await $fetch(`${baseURL}/api/search/files`, {
        method: 'POST',
        body: {
          query,
          limit
        }
      })
    },

    async getSearchSuggestions(query: string, limit: number = 10) {
      return await $fetch(`${baseURL}/api/search/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`)
    },

    async getSearchStats() {
      return await $fetch(`${baseURL}/api/search/stats`)
    },

    // AI Search
    async aiSearch(data: {
      query: string
      limit?: number
      search_type?: string
      file_types?: string[]
      watched_items?: string[]
    }) {
      return await $fetch(`${baseURL}/api/ai-search/search`, {
        method: 'POST',
        body: data
      })
    },

    async getAiSuggestions(query: string, limit: number = 5) {
      return await $fetch(`${baseURL}/api/ai-search/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`)
    },

    async getAiStats() {
      return await $fetch(`${baseURL}/api/ai-search/stats`)
    },

    async reindexAi() {
      return await $fetch(`${baseURL}/api/ai-search/reindex`, {
        method: 'POST'
      })
    },

    async clearAiIndex() {
      return await $fetch(`${baseURL}/api/ai-search/clear`, {
        method: 'DELETE'
      })
    },

    // Ollama AI Search
    async ollamaSearch(data: {
      query: string
      limit: number
      search_type: string
      file_types?: string[]
    }) {
      return await $fetch(`${baseURL}/api/ollama-ai-search/search`, {
        method: 'POST',
        body: data
      })
    },

    async ollamaGenerateAnswer(data: {
      query: string
      context_documents: any[]
      max_length: number
    }) {
      return await $fetch(`${baseURL}/api/ollama-ai-search/generate-answer`, {
        method: 'POST',
        body: data
      })
    },

    async getOllamaSuggestions(query: string, limit: number = 5) {
      return await $fetch(`${baseURL}/api/ollama-ai-search/suggestions?query=${encodeURIComponent(query)}&limit=${limit}`)
    },

    async ollamaReindex() {
      return await $fetch(`${baseURL}/api/ollama-ai-search/index`, {
        method: 'POST'
      })
    },

    async ollamaClearIndex() {
      return await $fetch(`${baseURL}/api/ollama-ai-search/clear-index`, {
        method: 'POST'
      })
    },

    async getOllamaStats() {
      return await $fetch(`${baseURL}/api/ollama-ai-search/stats`)
    },

    // Generic methods for backward compatibility
    async get(url: string, options: any = {}) {
      return await $fetch(`${baseURL}${url}`, {
        method: 'GET',
        ...options
      })
    },

    async post(url: string, data: any = {}) {
      return await $fetch(`${baseURL}${url}`, {
        method: 'POST',
        body: data
      })
    },

    async delete(url: string) {
      return await $fetch(`${baseURL}${url}`, {
        method: 'DELETE'
      })
    }
  }

  return api
} 