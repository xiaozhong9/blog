import { createI18n } from 'vue-i18n'
import zh_CN from './zh-CN.json'
import en_US from './en-US.json'

export const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  messages: {
    zh: zh_CN,
    en: en_US,
  },
  compositionOnly: true,
  globalInjection: true,
})
