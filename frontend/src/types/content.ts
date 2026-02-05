import { z } from 'zod'

// Frontmatter schema for blog posts
export const postSchema = z.object({
  title: z.string(),
  description: z.string(),
  date: z.string(), // ISO date string
  tags: z.array(z.string()).default([]),
  category: z.enum(['blog', 'projects', 'life', 'notes']),
  author: z.string().default('Nano Banana'),
  image: z.string().optional(),
  draft: z.boolean().default(false),
  featured: z.boolean().default(false),
  locale: z.enum(['zh', 'en']).default('zh'),
  readingTime: z.number().optional(),
  slug: z.string().optional(),
})

export type PostFrontmatter = z.infer<typeof postSchema>

// Post content with frontmatter
export interface Post {
  slug: string
  content: string
  frontmatter: PostFrontmatter
}

// Content filter options
export interface ContentFilter {
  category?: 'blog' | 'projects' | 'life' | 'notes'
  tags?: string[]
  locale?: 'zh' | 'en'
  draft?: boolean
  featured?: boolean
  search?: string

  // 新增排序字段
  sortBy?: 'date' | 'popularity' | 'readingTime' | 'title'
  sortOrder?: 'asc' | 'desc'

  // 新增日期范围筛选
  dateFrom?: string
  dateTo?: string
}

// Content summary for listings
export interface PostSummary {
  slug: string
  title: string
  description: string
  content?: string // 内容（可选，用于编辑）
  date: string
  tags: string[]
  category: 'blog' | 'projects' | 'life' | 'notes'
  locale: 'zh' | 'en'
  readingTime?: number
  image?: string
  featured: boolean
  draft?: boolean // 是否为草稿（可选，默认false）
  views?: number // 浏览次数
  author?: string // 作者

  // 项目特有字段
  stars?: number
  forks?: number
  repo?: string
  demo?: string
  techStack?: string[]
  status?: 'active' | 'maintenance' | 'archived'
}
