import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface Widget {
  id: string
  type: string
  title: string
  grid: { x: number; y: number; w: number; h: number }
  status: 'active' | 'hidden' | 'closed'
  snapshot: any
}

interface ChartItem {
  type: string
  name: string
  icon: string
  group: string
}

/**
 * Dashboard store for managing widgets and their states
 */
export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const widgets = ref<Widget[]>([])

  const chartLibrary = ref<ChartItem[]>([
    {
      type: 'CoreSearchMap',
      name: '古茶树地图探索',
      icon: 'map',
      group: '核心'
    },
    {
      type: 'BaseDiameterBar',
      name: '直径分析图表',
      icon: 'bar-chart',
      group: '分析'
    },
    {
      type: 'AIAssistant',
      name: 'AI 助手',
      icon: 'robot',
      group: '工具'
    }
  ])

  // Getters
  /**
   * Get all active widgets (not closed) for the "已打开" list
   */
  const activeWidgets = computed(() => {
    return widgets.value.filter(widget => widget.status !== 'closed')
  })

  /**
   * Get all visible widgets (status: 'active') for central canvas rendering
   */
  const visibleWidgets = computed(() => {
    return widgets.value.filter(widget => widget.status === 'active')
  })

  // Actions
  /**
   * Add a new widget based on type from chartLibrary
   * @param type - The widget type to add
   */
  const addWidget = (type: string) => {
    const config = chartLibrary.value.find(item => item.type === type)
    if (!config) {
      console.warn(`Widget type '${type}' not found in chartLibrary`)
      return
    }

    const id = `${type}_${Date.now()}`
    const newWidget: Widget = {
      id,
      type,
      title: config.name,
      grid: { x: 0, y: Infinity, w: 8, h: 6 },
      status: 'active',
      snapshot: null
    }

    widgets.value.push(newWidget)
  }

  /**
   * Hide a widget by setting its status to 'hidden'
   * @param id - The widget ID to hide
   */
  const hideWidget = (id: string) => {
    const widget = widgets.value.find(w => w.id === id)
    if (widget) {
      widget.status = 'hidden'
    }
  }

  /**
   * Activate a widget by setting its status to 'active'
   * @param id - The widget ID to activate
   */
  const activateWidget = (id: string) => {
    const widget = widgets.value.find(w => w.id === id)
    if (widget) {
      widget.status = 'active'
    }
  }

  /**
   * Close a widget by removing it from the widgets array
   * @param id - The widget ID to close
   */
  const closeWidget = (id: string) => {
    const index = widgets.value.findIndex(w => w.id === id)
    if (index !== -1) {
      widgets.value.splice(index, 1)
    }
  }

  /**
   * Update the layout (grid) of a widget
   * @param id - The widget ID
   * @param layout - The new layout object
   */
  const updateWidgetLayout = (id: string, layout: { x: number; y: number; w: number; h: number }) => {
    const widget = widgets.value.find(w => w.id === id)
    if (widget) {
      widget.grid = { ...layout }
    }
  }

  return {
    // State
    widgets,
    chartLibrary,
    // Getters
    activeWidgets,
    visibleWidgets,
    // Actions
    addWidget,
    hideWidget,
    activateWidget,
    closeWidget,
    updateWidgetLayout
  }
})
