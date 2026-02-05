export type Theme = 'light' | 'dark' | 'system'

export interface ThemeConfig {
  theme: Theme
  resolvedTheme: 'light' | 'dark'
}
