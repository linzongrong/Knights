// src/types/vue-grid-layout.d.ts
declare module 'vue-grid-layout' {
  import { DefineComponent } from 'vue'

  export const GridLayout: DefineComponent<{
    layout: Array<{
      i: string
      x: number
      y: number
      w: number
      h: number
      minW?: number
      minH?: number
      maxW?: number
      maxH?: number
      static?: boolean
      moved?: boolean
    }>
    colNum?: number
    rowHeight?: number
    isDraggable?: boolean
    isResizable?: boolean
    verticalCompact?: boolean
    margin?: [number, number]
    useCssTransforms?: boolean
    // 可根据需要扩展更多 props
  }, {}, any>

  export const GridItem: DefineComponent<{
    i: string
    x: number
    y: number
    w: number
    h: number
    minW?: number
    minH?: number
    maxW?: number
    maxH?: number
    static?: boolean
  }, {}, any>
}