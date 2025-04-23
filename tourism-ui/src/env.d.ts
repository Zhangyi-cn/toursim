/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module '*.vue' {
  import type { App, defineComponent } from 'vue'
  const component: ReturnType<typeof defineComponent>
  export default component
}

// 声明 ElementPlus 的全局组件类型
declare module '@vue/runtime-core' {
  export interface GlobalComponents {
    ElButton: typeof import('element-plus')['ElButton']
    ElInput: typeof import('element-plus')['ElInput']
    ElForm: typeof import('element-plus')['ElForm']
    ElFormItem: typeof import('element-plus')['ElFormItem']
    ElSelect: typeof import('element-plus')['ElSelect']
    ElOption: typeof import('element-plus')['ElOption']
    ElTable: typeof import('element-plus')['ElTable']
    ElTableColumn: typeof import('element-plus')['ElTableColumn']
    ElPagination: typeof import('element-plus')['ElPagination']
    ElDialog: typeof import('element-plus')['ElDialog']
    ElMessage: typeof import('element-plus')['ElMessage']
    ElMessageBox: typeof import('element-plus')['ElMessageBox']
    ElLoading: typeof import('element-plus')['ElLoading']
    ElIcon: typeof import('element-plus')['ElIcon']
    ElCarousel: typeof import('element-plus')['ElCarousel']
    ElCarouselItem: typeof import('element-plus')['ElCarouselItem']
    ElCard: typeof import('element-plus')['ElCard']
    ElTag: typeof import('element-plus')['ElTag']
    ElAvatar: typeof import('element-plus')['ElAvatar']
    ElDropdown: typeof import('element-plus')['ElDropdown']
    ElDropdownMenu: typeof import('element-plus')['ElDropdownMenu']
    ElDropdownItem: typeof import('element-plus')['ElDropdownItem']
    ElBreadcrumb: typeof import('element-plus')['ElBreadcrumb']
    ElBreadcrumbItem: typeof import('element-plus')['ElBreadcrumbItem']
    ElTabs: typeof import('element-plus')['ElTabs']
    ElTabPane: typeof import('element-plus')['ElTabPane']
    ElCheckbox: typeof import('element-plus')['ElCheckbox']
    ElRadio: typeof import('element-plus')['ElRadio']
    ElRadioGroup: typeof import('element-plus')['ElRadioGroup']
    ElRadioButton: typeof import('element-plus')['ElRadioButton']
    ElRate: typeof import('element-plus')['ElRate']
    ElUpload: typeof import('element-plus')['ElUpload']
    ElDatePicker: typeof import('element-plus')['ElDatePicker']
    ElTimePicker: typeof import('element-plus')['ElTimePicker']
    ElSwitch: typeof import('element-plus')['ElSwitch']
    ElSlider: typeof import('element-plus')['ElSlider']
    ElPopover: typeof import('element-plus')['ElPopover']
    ElTooltip: typeof import('element-plus')['ElTooltip']
    ElAlert: typeof import('element-plus')['ElAlert']
    ElEmpty: typeof import('element-plus')['ElEmpty']
  }
}

// 声明 .js 和 .jsx 文件的模块类型
declare module '*.js'
declare module '*.jsx'

// 声明图片等静态资源的模块类型
declare module '*.svg'
declare module '*.png'
declare module '*.jpg'
declare module '*.jpeg'
declare module '*.gif'
declare module '*.bmp'
declare module '*.tiff'
declare module '*.json' 