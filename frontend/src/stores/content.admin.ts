/**
 * Admin Content Store - 管理端内容 Store
 * 使用真实后端 API 进行 CRUD 操作
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PostSummary, ContentFilter } from '@/types/content'
import { articleService, categoryService, tagService } from '@/api/services'
import { articlesToPostSummaries } from '@/api/adapters'
import { apiClient } from '@/api/client'

export const useAdminContentStore = defineStore('adminContent', () => {
  // State
  const posts = ref<PostSummary[]>([])
  const currentPost = ref<PostSummary | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Categories & Tags for forms
  const categories = ref<any[]>([])
  const tags = ref<any[]>([])

  // Category type to ID mapping
  const categoryIdMap = computed(() => {
    const map: Record<string, number> = {}
    categories.value.forEach((cat: any) => {
      map[cat.category_type] = cat.id
    })
    return map
  })

  // Computed
  const postsByCategory = computed(() => {
    return (category: 'blog' | 'projects' | 'life' | 'notes') => {
      return posts.value.filter(post => post.category === category)
    }
  })

  const draftPosts = computed(() => {
    return posts.value.filter(post => post.draft)
  })

  const publishedPosts = computed(() => {
    return posts.value.filter(post => !post.draft)
  })

  /**
   * 加载所有文章（包括草稿）
   */
  const loadAllContent = async (includeDraft = true) => {
    loading.value = true
    error.value = null

    try {
      const data = await articleService.getList({
        page: 1,
        page_size: 100,
        ...(includeDraft ? {} : { status: 'published' }),
      })

      posts.value = articlesToPostSummaries(data.results)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载内容失败'
      posts.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据分类加载文章
   */
  const loadPostsByCategory = async (category: 'blog' | 'projects' | 'life' | 'notes') => {
    loading.value = true
    error.value = null

    try {
      const data = await articleService.getList({
        page: 1,
        page_size: 100,
        category,
      })

      const convertedPosts = articlesToPostSummaries(data.results)
      posts.value = convertedPosts

      return convertedPosts
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载失败'
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 slug 获取文章
   */
  const getPostBySlug = async (slug: string): Promise<PostSummary | null> => {
    loading.value = true
    error.value = null

    try {
      const article = await articleService.getDetail(slug)

      // 转换为 PostSummary 格式
      const post: PostSummary = {
        slug: article.slug,
        title: article.title,
        description: article.description,
        content: article.content, // 包含内容
        date: article.published_at || article.created_at,
        tags: article.tags.map(t => t.name),
        category: article.category_type as any,
        locale: article.locale,
        readingTime: article.reading_time,
        featured: article.featured,
        author: article.author?.nickname || article.author?.username || 'Admin',
        draft: article.status === 'draft',
        image: article.cover_image || undefined,
        // 项目特殊字段
        ...(article.category_type === 'projects' && {
          stars: article.stars,
          forks: article.forks,
          repo: article.repo,
          demo: article.demo,
          techStack: article.tech_stack || [],
        }),
      }

      currentPost.value = post
      return post
    } catch (e) {
      error.value = e instanceof Error ? e.message : '加载文章失败'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 将标签名称数组转换为标签 ID 数组
   */
  const getTagIdsByNames = (tagNames: string[]): number[] => {
    if (!tagNames || tagNames.length === 0) return []

    return tagNames
      .map(name => {
        const tag = tags.value.find((t: any) => t.name === name)
        return tag ? tag.id : null
      })
      .filter((id): id is number => id !== null)
  }

  /**
   * 创建文章
   */
  const createPost = async (postData: Partial<PostSummary> & { content?: string }): Promise<PostSummary> => {
    loading.value = true
    error.value = null

    try {
      // 获取 category_id
      const categoryId = postData.category ? categoryIdMap.value[postData.category] : null

      // 获取 tag_ids
      const tagIds = getTagIdsByNames(postData.tags || [])

      // 准备数据
      const createData: any = {
        title: postData.title,
        slug: postData.slug,
        description: postData.description,
        content: (postData as any).content || '',
        category_id: categoryId, // 使用 category_id 而不是 category
        tag_ids: tagIds, // 使用 tag_ids 而不是 keywords
        locale: postData.locale || 'zh',
        reading_time: postData.readingTime,
        status: postData.draft ? 'draft' : 'published',
        featured: postData.featured || false,
        cover_image: (postData as any).image || '',
        keywords: postData.tags?.join(','), // SEO keywords (optional)
        // 日期字段：将前端的 date (YYYY-MM-DD) 转换为后端的 published_at (ISO datetime)
        ...((postData as any).date !== undefined && {
          published_at: new Date((postData as any).date + 'T12:00:00').toISOString()
        }),
        // 项目特殊字段
        ...(postData.category === 'projects' && {
          stars: (postData as any).stars || 0,
          forks: (postData as any).forks || 0,
          repo: (postData as any).repo || '',
          demo: (postData as any).demo || '',
          tech_stack: (postData as any).techStack || [],
        }),
      }

      // 调用 API
      const newArticle = await articleService.create(createData)

      // 转换为 PostSummary
      const newPost: PostSummary = {
        slug: newArticle.slug,
        title: newArticle.title,
        description: newArticle.description,
        date: newArticle.published_at || newArticle.created_at,
        tags: newArticle.tags.map(t => t.name),
        category: newArticle.category_type as any || postData.category || 'blog',
        locale: newArticle.locale,
        readingTime: newArticle.reading_time,
        featured: newArticle.featured,
        author: newArticle.author?.nickname || 'Admin',
        draft: newArticle.status === 'draft',
        image: newArticle.cover_image || undefined,
        ...(newArticle.category_type === 'projects' && {
          stars: newArticle.stars,
          forks: newArticle.forks,
          repo: newArticle.repo,
          demo: newArticle.demo,
          techStack: newArticle.tech_stack || [],
        }),
      }

      // 添加到列表
      posts.value.unshift(newPost)

      return newPost
    } catch (e) {
      error.value = e instanceof Error ? e.message : '创建文章失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新文章
   */
  const updatePost = async (slug: string, postData: Partial<PostSummary> & { content?: string }): Promise<PostSummary> => {
    loading.value = true
    error.value = null

    try {
      // 查找文章 ID
      const post = posts.value.find(p => p.slug === slug)
      if (!post) {
        throw new Error('文章不存在')
      }

      // 获取 category_id
      const categoryId = postData.category ? categoryIdMap.value[postData.category] : undefined

      // 处理标签：创建新标签并获取所有标签 ID（只在明确提供 tags 时处理）
      let tagIds: number[] = []
      const failedTags: string[] = []

      if (postData.tags !== undefined) {
        // 只在需要处理标签时才加载标签列表
        if (tags.value.length === 0) {
          await loadTags()
        }

        for (const tagName of postData.tags) {
          // 查找标签
          const existingTag = tags.value.find((t: any) => t.name === tagName)
          if (existingTag) {
            tagIds.push(existingTag.id)
          } else {
            // 创建新标签
            try {
              // 生成 slug (简单地将名称转换为小写并替换空格为连字符)
              const slug = tagName.toLowerCase()
                .replace(/\s+/g, '-')
                .replace(/[^\w\-]+/g, '')
                .substring(0, 100)

              const response = await fetch(`${apiClient.baseURL}/tags/`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  ...apiClient.getAuthHeaders()
                },
                body: JSON.stringify({
                  name: tagName,
                  slug: slug
                })
              })
              if (response.ok) {
                const data = await response.json()
                const newTag = data.data || data
                // 注意：这里保持容错因为 tag 创建可能直接返回对象
                tagIds.push(newTag.id)
                // 刷新标签列表
                await loadTags()
              } else {
                failedTags.push(tagName)
              }
            } catch (e) {
              failedTags.push(tagName)
            }
          }
        }

        // 如果有标签创建失败，抛出错误
        if (failedTags.length > 0) {
          throw new Error(`以下标签创建失败: ${failedTags.join(', ')}`)
        }
      }

      // 准备更新数据 - 只包含提供的字段
      const updateData: any = {}

      // 只有当字段存在且不为 undefined 时才添加
      if (postData.title !== undefined) updateData.title = postData.title
      if (postData.description !== undefined) updateData.description = postData.description
      if ((postData as any).content !== undefined) updateData.content = (postData as any).content
      if (categoryId !== undefined) updateData.category_id = categoryId
      // 标签处理：明确提供 tags 时才更新
      if (postData.tags !== undefined) {
        updateData.tag_ids = tagIds
      }
      if (postData.locale !== undefined) updateData.locale = postData.locale
      if (postData.readingTime !== undefined) updateData.reading_time = postData.readingTime
      if (postData.featured !== undefined) updateData.featured = postData.featured
      // 统一使用 image 字段
      if ((postData as any).image !== undefined) {
        updateData.cover_image = (postData as any).image || ''
      }
      // 日期字段：将前端的 date (YYYY-MM-DD) 转换为后端的 published_at (ISO datetime)
      if ((postData as any).date !== undefined) {
        // 将 YYYY-MM-DD 转换为 ISO 8601 格式，设置为当天的中午时间
        const publishedAt = new Date((postData as any).date + 'T12:00:00').toISOString()
        updateData.published_at = publishedAt
      }

      // 状态处理：如果 draft 被明确设置
      if (postData.draft !== undefined) {
        updateData.status = postData.draft ? 'draft' : 'published'
      }

      // 项目特殊字段
      if (postData.category === 'projects') {
        if ((postData as any).stars !== undefined) updateData.stars = (postData as any).stars
        if ((postData as any).forks !== undefined) updateData.forks = (postData as any).forks
        if ((postData as any).repo !== undefined) updateData.repo = (postData as any).repo
        if ((postData as any).demo !== undefined) updateData.demo = (postData as any).demo
        if ((postData as any).techStack !== undefined) updateData.tech_stack = (postData as any).techStack
      }

      // 调用 API
      let updatedArticle
      try {
        updatedArticle = await articleService.update(post.slug || slug, updateData)
      } catch (updateError: any) {
        throw updateError
      }

      // 转换为 PostSummary
      const updatedPost: PostSummary = {
        slug: updatedArticle.slug,
        title: updatedArticle.title,
        description: updatedArticle.description,
        date: updatedArticle.published_at || updatedArticle.created_at,
        tags: updatedArticle.tags.map(t => t.name),
        category: updatedArticle.category_type as any || postData.category,
        locale: updatedArticle.locale,
        readingTime: updatedArticle.reading_time,
        featured: updatedArticle.featured,
        author: updatedArticle.author?.nickname || 'Admin',
        draft: updatedArticle.status === 'draft',
        image: updatedArticle.cover_image || undefined,
        ...(updatedArticle.category_type === 'projects' && {
          stars: updatedArticle.stars,
          forks: updatedArticle.forks,
          repo: updatedArticle.repo,
          demo: updatedArticle.demo,
          techStack: updatedArticle.tech_stack || [],
        }),
      }

      // 更新列表中的数据（直接替换以确保响应式更新）
      const index = posts.value.findIndex(p => p.slug === slug)
      if (index !== -1) {
        // 直接替换整个对象以触发响应式更新
        posts.value[index] = updatedPost
      }

      currentPost.value = updatedPost

      return updatedPost
    } catch (e: any) {
      error.value = e.message || e.errors || '更新文章失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除文章
   */
  const deletePost = async (slug: string): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      // 直接调用 API 删除
      await articleService.delete(slug)

      // API 删除成功后从本地列表中移除（乐观更新）
      const index = posts.value.findIndex(p => p.slug === slug)
      if (index !== -1) {
        posts.value.splice(index, 1)
      }

      return true
    } catch (e: any) {
      // API 删除失败，不从本地移除
      const errorMessage = e?.message || e?.detail || '删除文章失败'
      error.value = errorMessage
      throw new Error(errorMessage)
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载分类列表
   */
  const loadCategories = async () => {
    try {
      const data = await categoryService.getAll()
      // API 返回格式: { code, message, data }
      categories.value = Array.isArray(data) ? data : (data as any).data || []
    } catch (e) {
      // 静默失败
    }
  }

  /**
   * 加载标签列表
   */
  const loadTags = async () => {
    try {
      const data = await tagService.getAll()
      // API 返回格式: { code, message, data }
      tags.value = Array.isArray(data) ? data : (data as any).data || []
    } catch (e) {
      // 静默失败
    }
  }

  /**
   * Filter posts (客户端过滤，用于快速筛选)
   */
  const filterPosts = (filter: ContentFilter): PostSummary[] => {
    let filtered = [...posts.value]

    // 1. 按类别筛选
    if (filter.category) {
      filtered = filtered.filter(post => post.category === filter.category)
    }

    // 2. 按标签筛选
    if (filter.tags && filter.tags.length > 0) {
      filtered = filtered.filter(post =>
        filter.tags!.some(tag => post.tags.includes(tag))
      )
    }

    // 3. 按语言筛选
    if (filter.locale) {
      filtered = filtered.filter(post => post.locale === filter.locale)
    }

    // 4. 按精选状态筛选
    if (filter.featured) {
      filtered = filtered.filter(post => post.featured)
    }

    // 5. 草稿过滤
    if (filter.draft === false) {
      filtered = filtered.filter(post => !post.draft)
    }

    // 6. 搜索筛选
    if (filter.search) {
      const searchLower = filter.search.toLowerCase()
      filtered = filtered.filter(post =>
        post.title.toLowerCase().includes(searchLower) ||
        post.description.toLowerCase().includes(searchLower) ||
        post.tags.some(tag => tag.toLowerCase().includes(searchLower))
      )
    }

    // 7. 日期范围筛选
    if (filter.dateFrom) {
      const fromDate = new Date(filter.dateFrom).getTime()
      filtered = filtered.filter(post => new Date(post.date).getTime() >= fromDate)
    }

    if (filter.dateTo) {
      const toDate = new Date(filter.dateTo).getTime()
      filtered = filtered.filter(post => new Date(post.date).getTime() <= toDate)
    }

    // 8. 排序
    const sortBy = filter.sortBy || 'date'
    const sortOrder = filter.sortOrder || 'desc'

    filtered.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'date':
          comparison = new Date(a.date).getTime() - new Date(b.date).getTime()
          break
        case 'popularity':
          const getPopularity = (post: PostSummary) => {
            if ('stars' in post && 'forks' in post) {
              return (post as any).stars * 2 + (post as any).forks
            }
            return 0
          }
          comparison = getPopularity(a) - getPopularity(b)
          break
        case 'readingTime':
          const aTime = a.readingTime || 0
          const bTime = b.readingTime || 0
          comparison = aTime - bTime
          break
        case 'title':
          comparison = a.title.localeCompare(b.title, 'zh-CN')
          break
        default:
          comparison = 0
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }

  // Get all tags
  const getAllTags = computed(() => {
    const tags = new Set<string>()
    posts.value.forEach(post => {
      post.tags.forEach(tag => tags.add(tag))
    })
    return Array.from(tags).sort()
  })

  return {
    // State
    posts,
    currentPost,
    loading,
    error,
    categories,
    tags,

    // Computed
    postsByCategory,
    draftPosts,
    publishedPosts,
    getAllTags,

    // Methods
    loadAllContent,
    loadPostsByCategory,
    getPostBySlug,
    createPost,
    updatePost,
    deletePost,
    filterPosts,
    loadCategories,
    loadTags,
  }
})
