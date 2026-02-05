/**
 * 统一的日志工具
 * 只在开发环境输出日志
 */

const isDev = import.meta.env.DEV

export const logger = {
  error: (message: string, error?: any) => {
    if (isDev) {
      console.error(message, error)
    }
  },
  warn: (message: string, error?: any) => {
    if (isDev) {
      console.warn(message, error)
    }
  },
  info: (message: string, ...args: any[]) => {
    if (isDev) {
      console.info(message, ...args)
    }
  },
  debug: (message: string, ...args: any[]) => {
    if (isDev) {
      console.log(message, ...args)
    }
  }
}
