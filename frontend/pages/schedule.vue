<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Plánování</h1>
      <p class="text-gray-600 dark:text-gray-400">
        Nastavte kdy a jak se má provádět indexace dokumentů
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Schedule configuration -->
      <UCard>
        <template #header>
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-clock" class="w-5 h-5 text-blue-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Nastavení plánování</h3>
          </div>
        </template>

        <form @submit.prevent="saveSchedule" class="space-y-4">
          <!-- Enable/disable -->
          <div>
            <label class="flex items-center space-x-2">
              <UCheckbox v-model="scheduleConfig.enabled" />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Aktivní plánování
              </span>
            </label>
          </div>

          <!-- Time window -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Začátek časového okna
              </label>
              <UInput
                v-model="scheduleConfig.time_window_start"
                type="time"
                placeholder="23:00"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Konec časového okna
              </label>
              <UInput
                v-model="scheduleConfig.time_window_end"
                type="time"
                placeholder="07:00"
              />
            </div>
          </div>

          <!-- Idle settings -->
          <div>
            <label class="flex items-center space-x-2">
              <UCheckbox v-model="scheduleConfig.idle_only" />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                Pouze při nečinnosti systému
              </span>
            </label>
          </div>

          <!-- Thresholds -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                CPU threshold (%)
              </label>
              <UInput
                v-model="scheduleConfig.cpu_threshold"
                type="number"
                min="0"
                max="100"
                placeholder="30"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                RAM threshold (%)
              </label>
              <UInput
                v-model="scheduleConfig.ram_threshold"
                type="number"
                min="0"
                max="100"
                placeholder="50"
              />
            </div>
          </div>

          <!-- Save button -->
          <UButton
            label="Uložit nastavení"
            icon="i-heroicons-check"
            @click="saveSchedule"
            :loading="saving"
            class="w-full"
          />
        </form>
      </UCard>

      <!-- System status -->
      <UCard>
        <template #header>
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-cpu-chip" class="w-5 h-5 text-green-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Stav systému</h3>
          </div>
        </template>

        <div class="space-y-4">
          <!-- CPU Usage -->
          <div>
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">CPU využití</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ systemStatus.cpu_usage }}%</span>
            </div>
            <UProgress
              :value="systemStatus.cpu_usage"
              :color="getCpuColor(systemStatus.cpu_usage)"
              size="sm"
            />
          </div>

          <!-- RAM Usage -->
          <div>
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">RAM využití</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ systemStatus.ram_usage }}%</span>
            </div>
            <UProgress
              :value="systemStatus.ram_usage"
              :color="getRamColor(systemStatus.ram_usage)"
              size="sm"
            />
          </div>

          <!-- Disk Usage -->
          <div>
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Disk využití</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ systemStatus.disk_usage }}%</span>
            </div>
            <UProgress
              :value="systemStatus.disk_usage"
              :color="getDiskColor(systemStatus.disk_usage)"
              size="sm"
            />
          </div>

          <!-- Idle status -->
          <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Systém je idle</span>
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full" :class="systemStatus.is_idle ? 'bg-green-500' : 'bg-red-500'"></div>
              <span class="text-sm text-gray-500 dark:text-gray-400">
                {{ systemStatus.is_idle ? 'Ano' : 'Ne' }}
              </span>
            </div>
          </div>

          <!-- Current time -->
          <div class="text-center text-sm text-gray-500 dark:text-gray-400">
            Aktuální čas: {{ currentTime }}
          </div>
        </div>
      </UCard>
    </div>

    <!-- Schedule status -->
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <UIcon name="i-heroicons-calendar" class="w-5 h-5 text-purple-500" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Status plánování</h3>
          </div>
          <div class="flex items-center space-x-2">
            <UButton
              label="Test plánování"
              icon="i-heroicons-play"
              color="blue"
              variant="soft"
              size="sm"
              @click="testSchedule"
              :loading="testing"
            />
            <UButton
              :label="scheduleStatus.schedule_enabled ? 'Pozastavit' : 'Obnovit'"
              :icon="scheduleStatus.schedule_enabled ? 'i-heroicons-pause' : 'i-heroicons-play'"
              :color="scheduleStatus.schedule_enabled ? 'yellow' : 'green'"
              variant="soft"
              size="sm"
              @click="toggleSchedule"
            />
          </div>
        </div>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ scheduleStatus.schedule_enabled ? 'Aktivní' : 'Neaktivní' }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">Plánování</div>
        </div>
        
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ scheduleStatus.time_window }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">Časové okno</div>
        </div>
        
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ scheduleStatus.is_idle ? 'Ano' : 'Ne' }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">Systém idle</div>
        </div>
        
        <div class="text-center">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ scheduleStatus.should_process_now ? 'Ano' : 'Ne' }}
          </div>
          <div class="text-sm text-gray-500 dark:text-gray-400">Zpracovávat nyní</div>
        </div>
      </div>
    </UCard>

    <!-- Recent schedule activity -->
    <UCard>
      <template #header>
        <div class="flex items-center space-x-2">
          <UIcon name="i-heroicons-clock" class="w-5 h-5 text-gray-500" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Poslední aktivita</h3>
        </div>
      </template>

      <div class="space-y-4">
        <div v-for="activity in recentActivity" :key="activity.id" class="flex items-center space-x-3">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="activity.color">
              <UIcon :name="activity.icon" class="w-4 h-4 text-white" />
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 dark:text-white">{{ activity.title }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ activity.description }}</p>
          </div>
          <div class="flex-shrink-0">
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ activity.time }}</p>
          </div>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup>
// Page metadata
useHead({
  title: 'Plánování - Dex Search'
})

// Reactive data
const saving = ref(false)
const testing = ref(false)
const currentTime = ref('')

const scheduleConfig = ref({
  time_window_start: '23:00',
  time_window_end: '07:00',
  idle_only: true,
  cpu_threshold: 30,
  ram_threshold: 50,
  enabled: true
})

const systemStatus = ref({
  cpu_usage: 0,
  ram_usage: 0,
  disk_usage: 0,
  is_idle: false
})

const scheduleStatus = ref({
  schedule_enabled: true,
  time_window: '23:00 - 07:00',
  is_idle: false,
  should_process_now: false
})

const recentActivity = ref([
  {
    id: 1,
    title: 'Plánovaná indexace spuštěna',
    description: 'Systém byl idle, spouštím indexaci',
    time: '2 minuty zpět',
    icon: 'i-heroicons-play',
    color: 'bg-green-500'
  },
  {
    id: 2,
    title: 'Indexace dokončena',
    description: 'Všechny složky byly úspěšně indexovány',
    time: '1 hodina zpět',
    icon: 'i-heroicons-check-circle',
    color: 'bg-blue-500'
  },
  {
    id: 3,
    title: 'Systém není idle',
    description: 'CPU využití příliš vysoké (45%)',
    time: '3 hodiny zpět',
    icon: 'i-heroicons-pause',
    color: 'bg-yellow-500'
  }
])

// Methods
const saveSchedule = async () => {
  saving.value = true
  try {
    await $fetch('/api/schedule/config', {
      method: 'PUT',
      body: scheduleConfig.value
    })
    
    // Refresh status
    await loadScheduleStatus()
  } catch (error) {
    console.error('Chyba při ukládání plánování:', error)
  } finally {
    saving.value = false
  }
}

const testSchedule = async () => {
  testing.value = true
  try {
    await $fetch('/api/schedule/test', {
      method: 'POST'
    })
    
    // Refresh status
    await loadScheduleStatus()
  } catch (error) {
    console.error('Chyba při testování plánování:', error)
  } finally {
    testing.value = false
  }
}

const toggleSchedule = async () => {
  try {
    if (scheduleStatus.value.schedule_enabled) {
      await $fetch('/api/schedule/pause', { method: 'POST' })
    } else {
      await $fetch('/api/schedule/resume', { method: 'POST' })
    }
    
    // Refresh status
    await loadScheduleStatus()
  } catch (error) {
    console.error('Chyba při přepínání plánování:', error)
  }
}

const loadScheduleConfig = async () => {
  try {
    const config = await $fetch('/api/schedule/config')
    scheduleConfig.value = config
  } catch (error) {
    console.error('Chyba při načítání konfigurace:', error)
  }
}

const loadSystemStatus = async () => {
  try {
    const status = await $fetch('/api/schedule/system')
    systemStatus.value = status
  } catch (error) {
    console.error('Chyba při načítání systémového statusu:', error)
  }
}

const loadScheduleStatus = async () => {
  try {
    const status = await $fetch('/api/schedule/status')
    scheduleStatus.value = status
  } catch (error) {
    console.error('Chyba při načítání statusu plánování:', error)
  }
}

const getCpuColor = (usage) => {
  if (usage < 30) return 'green'
  if (usage < 70) return 'yellow'
  return 'red'
}

const getRamColor = (usage) => {
  if (usage < 50) return 'green'
  if (usage < 80) return 'yellow'
  return 'red'
}

const getDiskColor = (usage) => {
  if (usage < 70) return 'green'
  if (usage < 90) return 'yellow'
  return 'red'
}

const updateCurrentTime = () => {
  currentTime.value = new Date().toLocaleTimeString('cs-CZ')
}

// Load data on mount
onMounted(async () => {
  await Promise.all([
    loadScheduleConfig(),
    loadSystemStatus(),
    loadScheduleStatus()
  ])
  
  // Update current time every second
  updateCurrentTime()
  setInterval(updateCurrentTime, 1000)
  
  // Refresh system status every 30 seconds
  setInterval(loadSystemStatus, 30000)
})
</script> 