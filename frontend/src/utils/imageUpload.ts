/**
 * 图片上传工具函数
 */
import { apiClient } from '@/api/client'
import { API_BASE_URL } from '@/api/config'

/**
 * 上传图片到服务器
 * @param file 图片文件对象
 * @param category 分类（blog、projects、life 等），用于按目录保存图片
 * @returns Promise<{ url: string; alt: string; href: string }>
 */
export async function uploadImage(file: File, category: string = 'general'): Promise<{
  url: string
  alt: string
  href: string
}> {
  // 创建 FormData
  const formData = new FormData()
  formData.append('file', file)
  formData.append('category', category)

  try {
    // 使用原生 fetch 而不是 apiClient，因为需要处理文件上传
    const response = await fetch(`${API_BASE_URL}/articles/upload-image/`, {
      method: 'POST',
      headers: {
        // 不要设置 Content-Type，让浏览器自动设置 multipart/form-data
        ...(localStorage.getItem('access_token') && {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        }),
      },
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || '上传失败')
    }

    const data = await response.json()

    if (data.code !== 200) {
      throw new Error(data.message || '上传失败')
    }

    return data.data
  } catch (error) {
    console.error('图片上传失败:', error)
    throw error
  }
}

/**
 * 将文件转换为 Data URL（用于粘贴的图片）
 * @param file 图片文件对象
 * @returns Promise<string>
 */
export function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()

    reader.onload = () => {
      resolve(reader.result as string)
    }

    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }

    reader.readAsDataURL(file)
  })
}

/**
 * 从剪贴板获取图片
 * @param clipboardData ClipboardTransfer 对象
 * @returns Promise<File | null>
 */
export async function getImageFromClipboard(
  clipboardData: DataTransfer
): Promise<File | null> {
  const items = clipboardData.items

  for (let i = 0; i < items.length; i++) {
    const item = items[i]

    if (item.kind === 'file') {
      const file = item.getAsFile?.(file => file.type.startsWith('image/'))
      if (file) {
        return file
      }
    }
  }

  return null
}

/**
 * 创建图片对象的预览 URL
 * @param file 图片文件对象
 * @returns string Blob URL
 */
export function createPreviewUrl(file: File): string {
  return URL.createObjectURL(file)
}

/**
 * 撤销预览 URL
 * @param url Blob URL
 */
export function revokePreviewUrl(url: string): void {
  URL.revokeObjectURL(url)
}
