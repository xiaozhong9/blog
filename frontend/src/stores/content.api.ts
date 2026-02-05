/**
 * Content Store - 使用真实 API
 * 从 Mock 数据迁移到真实后端 API
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Post, PostSummary, ContentFilter } from '@/types/content'
import { articleService } from '@/api/services'
import { searchService } from '@/api/services'
import { articlesToPostSummaries } from '@/api/adapters'
import { notifyError, notifyWarning } from '@/utils/notification'
import { logger } from '@/utils/logger'

export const useContentStore = defineStore('content', () => {
  // All posts (从 API 加载)
  const posts = ref<PostSummary[]>([])

  // Current post being viewed
  const currentPost = ref<Post | null>(null)

  // Loading state
  const loading = ref(false)

  // Error state
  const error = ref<string | null>(null)

  // Get posts by category
  const postsByCategory = computed(() => {
    return (category: 'blog' | 'projects' | 'life' | 'notes') => {
      return posts.value.filter(post => post.category === category)
    }
  })

  // Get featured posts
  const featuredPosts = computed(() => {
    return posts.value.filter(post => post.featured)
  })

  // Get latest posts
  const latestPosts = computed(() => {
    return [...posts.value]
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  })

  // Get posts by locale
  const postsByLocale = computed(() => {
    return (locale: 'zh' | 'en') => {
      return posts.value.filter(post => post.locale === locale)
    }
  })

  // Get project stats
  const projectStats = computed(() => {
    const projectPosts = posts.value.filter(post => post.category === 'projects')
    return {
      total: projectPosts.length,
      totalStars: projectPosts.reduce((sum, post) => sum + (post as any).stars || 0, 0),
      totalForks: projectPosts.reduce((sum, post) => sum + (post as any).forks || 0, 0),
    }
  })

  /**
   * 从后端 API 加载所有文章
   */
  const loadAllContent = async () => {
    loading.value = true
    error.value = null

    try {
      // 从 API 加载所有已发布的文章
      const data = await articleService.getList({
        status: 'published',
        page: 1,
        page_size: 100,
      })

      // 转换为前端期望的格式
      posts.value = articlesToPostSummaries(data.results)
    } catch (e) {
      notifyError('加载内容失败，请刷新页面重试', '加载失败')
      error.value = e instanceof Error ? e.message : '加载内容失败'

      // 如果 API 失败，使用空数组
      posts.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 slug 获取文章详情（始终从 API 获取最新数据）
   */
  const getPostBySlug = async (slug: string): Promise<Post | null> => {
    loading.value = true
    error.value = null

    try {
      // 始终从 API 获取文章详情
      const article = await articleService.getDetail(slug)

      // 转换为 Post 格式
      const post: Post = {
        slug: article.slug,
        content: article.content || '# 文章内容\n\n暂无内容',
        frontmatter: {
          title: article.title,
          description: article.description,
          date: article.published_at || article.created_at,
          tags: article.tags.map(t => t.name),
          category: article.category_type as any,
          locale: article.locale,
          readingTime: article.reading_time,
          featured: article.featured,
          author: article.author?.nickname || article.author?.username || 'Nano Banana',
          draft: article.status === 'draft',
          image: article.cover_image || undefined,
          // 项目特殊字段
          ...(article.category_type === 'projects' && {
            stars: article.stars,
            forks: article.forks,
            repo: article.repo,
            demo: article.demo,
            techStack: article.tech_stack,
          }),
        },
      }

      currentPost.value = post
      return post
    } catch (e: any) {
      error.value = e.message || e.errors || '加载文章失败'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据类别获取文章（支持 API 过滤）
   */
  const fetchPostsByCategory = async (category: 'blog' | 'projects' | 'life' | 'notes') => {
    loading.value = true
    error.value = null

    try {
      // 映射前端 category 到后端 category_type
      const categoryTypeMap: Record<typeof category, string> = {
        blog: 'blog',
        projects: 'projects',
        life: 'life',
        notes: 'notes',
      }

      const data = await articleService.getList({
        page: 1,
        page_size: 100,
        category: categoryTypeMap[category],
      })

      const convertedPosts = articlesToPostSummaries(data.results)

      // 更新 posts（可选：也可以返回新数组）
      posts.value = convertedPosts

      return convertedPosts
    } catch (e) {
      logger.error(`加载 ${category} 文章失败`, e)
      notifyError(`加载${category}文章失败`, '加载失败')
      error.value = e instanceof Error ? e.message : '加载失败'
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取精选文章
   */
  const fetchFeaturedPosts = async () => {
    try {
      const data = await articleService.getFeatured()
      return articlesToPostSummaries(data)
    } catch (e) {
      logger.error('加载精选文章失败', e)
      notifyWarning('加载精选文章失败，使用缓存数据', '加载失败')
      return featuredPosts.value
    }
  }

  /**
   * 获取热门文章
   */
  const fetchPopularPosts = async (params?: { period?: string; limit?: number }) => {
    try {
      const data = await articleService.getPopular(params)
      return articlesToPostSummaries(data)
    } catch (e) {
      logger.error('加载热门文章失败', e)
      notifyError('加载热门文章失败', '加载失败')
      return []
    }
  }

  /**
   * Filter posts (客户端过滤，兼容原有逻辑)
   */
  const filterPosts = (filter: ContentFilter): PostSummary[] => {
    // 性能优化：单次遍历完成所有筛选，避免多次创建中间数组
    const filtered = posts.value.filter(post => {
      // 1. 按类别筛选
      if (filter.category && post.category !== filter.category) {
        return false
      }

      // 2. 按标签筛选
      if (filter.tags && filter.tags.length > 0) {
        if (!filter.tags.some(tag => post.tags.includes(tag))) {
          return false
        }
      }

      // 3. 按语言筛选
      if (filter.locale && post.locale !== filter.locale) {
        return false
      }

      // 4. 按精选状态筛选
      if (filter.featured && !post.featured) {
        return false
      }

      // 5. 草稿过滤
      if (filter.draft === false && post.draft) {
        return false
      }

      // 6. 搜索筛选
      if (filter.search) {
        const searchLower = filter.search.toLowerCase()
        const titleMatch = post.title.toLowerCase().includes(searchLower)
        const descMatch = post.description.toLowerCase().includes(searchLower)
        const tagMatch = post.tags.some(tag => tag.toLowerCase().includes(searchLower))
        if (!titleMatch && !descMatch && !tagMatch) {
          return false
        }
      }

      // 7. 日期范围筛选（使用 Date 对象比较，确保正确性）
      if (filter.dateFrom) {
        const postDate = new Date(post.date)
        const fromDate = new Date(filter.dateFrom)
        // 将时间设置为当天的开始（00:00:00）
        fromDate.setHours(0, 0, 0, 0)
        if (postDate < fromDate) {
          return false
        }
      }

      if (filter.dateTo) {
        const postDate = new Date(post.date)
        const toDate = new Date(filter.dateTo)
        // 将时间设置为当天的结束（23:59:59.999）
        toDate.setHours(23, 59, 59, 999)
        if (postDate > toDate) {
          return false
        }
      }

      return true
    })

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
          // 热度计算：stars * 2 + forks（仅适用于项目）
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

  /**
   * 增加文章浏览数（后端已自动处理，这里更新本地状态）
   */
  const incrementViews = (slug: string) => {
    const post = posts.value.find(p => p.slug === slug)
    if (post) {
      post.views = (post.views || 0) + 1
    }
  }

  /**
   * 使用 Elasticsearch 进行全文搜索
   * 如果搜索失败，降级到客户端过滤
   */
  const searchPosts = async (filter: ContentFilter): Promise<{
    results: PostSummary[]
    total: number
    highlights?: Map<string, { title?: string[]; description?: string[] }>
  }> => {
    // 如果有搜索关键词，使用 Elasticsearch
    if (filter.search) {
      try {
        const response = await searchService.search({
          q: filter.search,
          category: filter.category,
          tags: filter.tags?.join(','),
          locale: filter.locale,
          page: 1,
          page_size: 100,
        })

        // 转换搜索结果
        const results = response.items.map(item => ({
          slug: item.slug || '',
          title: item.title,
          description: item.description,
          date: item.published_at,
          tags: item.tags?.map(t => t.name) || [],
          category: item.category?.name as any || filter.category || 'blog',
          locale: item.locale,
          readingTime: item.reading_time,
          featured: item.featured,
          image: undefined,
          draft: false,
        }))

        // 提取高亮信息
        const highlights = new Map()
        response.items.forEach(item => {
          if (item.highlight) {
            highlights.set(String(item.id), item.highlight)
          }
        })

        return {
          results,
          total: response.total,
          highlights,
        }
      } catch (e) {
        logger.warn('Elasticsearch 搜索失败，使用客户端过滤', e)
        // 降级到客户端过滤
        const filtered = filterPosts(filter)
        return { results: filtered, total: filtered.length }
      }
    }

    // 没有搜索关键词，使用客户端过滤
    const filtered = filterPosts(filter)
    return { results: filtered, total: filtered.length }
  }

  return {
    posts,
    currentPost,
    loading,
    error,
    postsByCategory,
    featuredPosts,
    latestPosts,
    postsByLocale,
    projectStats,
    filterPosts,

    // 新增的 API 方法
    loadAllContent,
    getPostBySlug,
    fetchPostsByCategory,
    fetchFeaturedPosts,
    fetchPopularPosts,
    getAllTags,
    searchPosts,
    incrementViews,
  }
})

// ==================== 内容生成器（用于本地生成内容）====================

function generateBlogContent(post: PostSummary): string {
  return '# ' + post.title + '\n\n' +
    post.description + '\n\n' +
    '## 背景\n\n' +
    '作为一个开发者，写博客是分享知识、记录成长的重要方式。Nano Banana 是我打造的个人博客系统，旨在创造一个美观、快速、功能完整的博客平台。\n\n' +
    '## 主要特点\n\n' +
    '1. 技术栈: Vue 3 + TypeScript + Vite\n' +
    '2. 设计灵感: Josh Comeau、Lee Robinson\n' +
    '3. 性能优化: 按需加载、代码分割\n' +
    '4. 交互体验: 搜索、主题切换、动画\n\n' +
    '## 技术细节\n\n' +
    '### 响应式设计\n\n' +
    'Tailwind CSS 的功能类优先架构让响应式变得简单：\n\n' +
    '```vue\n' +
    '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n' +
    '  <!-- 内容 -->\n' +
    '</div>\n' +
    '```\n\n' +
    '### 状态管理\n\n' +
    '使用 Pinia 进行全局状态管理，让组件间通信更简单。\n\n' +
    '## 总结\n\n' +
    'Nano Banana 是一个持续迭代的项目，欢迎提供反馈和建议！\n'
}

function generateProjectContent(post: PostSummary): string {
  const project = post as any
  const techStack = project.techStack.map((tech: string) => `- \`${tech}\``).join('\n')
  const demoLink = project.demo ? `\n- 🚀 [在线演示](${project.demo})` : ''

  return '# ' + project.title + '\n\n' +
    project.description + '\n\n' +
    '## 项目简介\n\n' +
    '这个项目使用了现代化的技术栈，注重代码质量和用户体验。\n\n' +
    '## 技术栈\n\n' +
    techStack + '\n\n' +
    '## 功能特性\n\n' +
    '- ⭐ ' + project.stars + ' stars\n' +
    '- 🍴 ' + project.forks + ' forks\n' +
    '- 🔗 [仓库地址](' + project.repo + ')' +
    demoLink + '\n\n' +
    '## 安装使用\n\n' +
    '```bash\n' +
    '# Clone the repository\n' +
    'git clone ' + project.repo + '\n\n' +
    '# Install dependencies\n' +
    'npm install\n\n' +
    '# Start development server\n' +
    'npm run dev\n' +
    '```\n\n' +
    '## 开发历程\n\n' +
    '从 0 到 1 的过程，遇到的挑战和解决方案。\n\n' +
    '## 未来规划\n\n' +
    '- [ ] 添加新功能\n' +
    '- [ ] 性能优化\n' +
    '- [ ] 文档完善\n\n' +
    '## 相关链接\n\n' +
    '- [GitHub](https://github.com)\n' +
    '- [演示地址](' + (project.demo || 'https://example.com') + ')\n\n' +
    '---\n\n' +
    '感谢使用！如果觉得有帮助，请给个 Star ⭐\n'
}

function generateLifeContent(post: PostSummary): string {
  return '# ' + post.title + '\n\n' +
    post.description + '\n\n' +
    '## 生活随笔\n\n' +
    '记录生活中的点点滴滴，分享感悟和思考。\n\n' +
    '## 今日心情\n\n' +
    '😊 开心 | 📅 日期: ' + post.date + '\n\n' +
    '## 总结\n\n' +
    '生活不止眼前的苟且，还有诗和远方。\n'
}
