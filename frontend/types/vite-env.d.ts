/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@iconify/vue' {
  import type { DefineComponent } from 'vue'
  const Icon: DefineComponent<{
    icon: string
  }, {}, any>
  export { Icon }
}

declare module 'virtual:vue-i18n-routes' {
  const routes: Record<string, string>
  export default routes
}
