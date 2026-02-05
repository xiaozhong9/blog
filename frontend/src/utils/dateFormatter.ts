/**
 * 统一的日期格式化工具
 */

/**
 * 格式化日期为长格式（年月日）
 * @param dateStr - ISO 日期字符串
 * @param locale - 语言区域（zh-CN 或 en-US）
 * @returns 格式化后的日期字符串
 */
export function formatDate(
  dateStr: string,
  locale: 'zh-CN' | 'en-US' = 'zh-CN'
): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * 格式化日期时间（相对时间）
 * @param dateStr - ISO 日期字符串
 * @returns 相对时间字符串（如"3分钟前"）
 */
export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`
  return formatDate(dateStr)
}

/**
 * 格式化日期为 YYYY-MM-DD 格式（用于 input type="date"）
 * @param dateStr - ISO 日期字符串
 * @returns YYYY-MM-DD 格式的日期字符串
 */
export function formatISODate(dateStr: string): string {
  const date = dateStr ? new Date(dateStr) : new Date()
  return date.toISOString().split('T')[0]
}

/**
 * 格式化日期为 YYYY-MM-DD HH:mm 格式
 * @param dateStr - ISO 日期字符串
 * @returns 格式化后的日期时间字符串
 */
export function formatFullDateTime(dateStr: string): string {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}
