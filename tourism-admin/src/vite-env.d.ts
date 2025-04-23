/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

// 声明@kangc/v-md-editor模块
declare module '@kangc/v-md-editor';
declare module '@kangc/v-md-editor/lib/theme/vuepress.js';

// Element Plus语言包声明
declare module 'element-plus/dist/locale/zh-cn.mjs';
