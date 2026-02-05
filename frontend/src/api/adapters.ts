/**
 * 数据转换工具 - 将后端 API 数据转换为前端期望的格式
 *
 * 支持两种数据源：
 * 1. Article - MySQL 完整数据（详情接口使用）
 * 2. ArticleListItem - ES 扁平化数据（列表接口使用）
 */

import type { Article, ArticleListItem } from './types'
import type { PostSummary, PostFrontmatter } from '@/types/content'

/**
 * 联合类型：支持 MySQL 完整数据 和 ES 扁平化数据
 */
type ArticleSource = Article | ArticleListItem

/**
 * 判断是否为 ES 返回的扁平化数据
 * 通过检查是否存在 ES 特有的扁平字段，同时排除嵌套结构
 */
function isEsArticleHit(data: ArticleSource): data is ArticleListItem {
  const hasEsFields = 'tags_names' in data && 'category_slug' in data
  const hasNestedStructure = 'author' in data && typeof data.author === 'object'
  // ES 数据有扁平字段但没有嵌套的 author 对象
  return hasEsFields && !hasNestedStructure
}

/**
 * 提取标签名称数组
 */
function extractTagsNames(article: ArticleSource): string[] {
  if (isEsArticleHit(article)) {
    return article.tags_names ?? []
  }
  return article.tags?.map((tag) => tag.name) ?? []
}

/**
 * 提取分类类型
 */
function extractCategoryType(article: ArticleSource): PostFrontmatter['category'] {
  const categoryType = isEsArticleHit(article)
    ? article.category_slug
    : article.category_type
  return mapBackendTypeToCategory(categoryType)
}

/**
 * 提取发布日期
 */
function extractPublishedDate(article: ArticleSource): string {
  return article.published_at || article.created_at
}

/**
 * 提取图片 URL
 */
function extractImage(article: ArticleSource): string | undefined {
  return article.cover_image || undefined
}

/**
 * 提取阅读量
 */
function extractViewCount(article: ArticleSource): number {
  return article.view_count ?? 0
}

/**
 * 提取技术栈
 */
function extractTechStack(article: ArticleSource): string[] | undefined {
  if (isEsArticleHit(article)) {
    return article.tech_stack
  }
  return article.tech_stack
}

/**
 * 将后端文章数据转换为前端 PostSummary 格式
 * 支持 MySQL 完整数据 和 ES 扁平化数据
 */
export function articleToPostSummary(article: ArticleSource): PostSummary {
  return {
    slug: article.slug,
    title: article.title,
    description: article.description,
    date: extractPublishedDate(article),
    tags: extractTagsNames(article),
    category: extractCategoryType(article),
    locale: article.locale,
    readingTime: article.reading_time,
    image: extractImage(article),
    featured: article.featured,
    views: extractViewCount(article),
    draft: article.status === 'draft',
    // 项目特殊字段
    stars: article.stars,
    forks: article.forks,
    repo: article.repo,
    demo: article.demo,
    techStack: extractTechStack(article),
  }
}

/**
 * 将后端文章数组转换为前端 PostSummary 数组
 */
export function articlesToPostSummaries(articles: ArticleSource[]): PostSummary[] {
  return articles.map(articleToPostSummary)
}

/**
 * 根据前端 category 类型映射到后端 category_type
 */
export function mapCategoryToBackendType(
  category: PostFrontmatter['category']
): string {
  const mapping: Record<PostFrontmatter['category'], string> = {
    blog: 'blog',
    projects: 'projects',
    life: 'life',
    notes: 'notes',
  }
  return mapping[category] || 'blog'
}

/**
 * 根据后端 category_type 映射到前端 category
 */
export function mapBackendTypeToCategory(
  categoryType: string
): PostFrontmatter['category'] {
  const mapping: Record<string, PostFrontmatter['category']> = {
    blog: 'blog',
    projects: 'projects',
    life: 'life',
    notes: 'notes',
  }
  return mapping[categoryType] || 'blog'
}
