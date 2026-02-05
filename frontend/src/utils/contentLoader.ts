/**
 * Content Loader - Load and validate markdown files from /src/content/
 * Uses gray-matter for frontmatter parsing and Zod for validation
 */
import matter from 'gray-matter'
import { postSchema, type Post, type PostSummary } from '@/types/content'

// Virtual module imports - these will be handled by Vite
const contentModules = import.meta.glob('/src/content/**/*.md', {
  query: '?raw',
  import: 'default',
})

/**
 * Load all content files
 */
export async function loadAllContent(): Promise<PostSummary[]> {
  const posts: PostSummary[] = []

  for (const [filePath, content] of Object.entries(contentModules)) {
    try {
      const markdown = await (content() as Promise<string>)
      const { data, content: markdownContent } = matter(markdown)

      // Validate frontmatter with Zod
      const validatedData = postSchema.parse(data)

      // Generate slug from filename if not provided
      const slug = validatedData.slug || filePath.split('/').pop()?.replace('.md', '') || ''

      // Calculate reading time if not provided
      const readingTime = validatedData.readingTime || calculateReadingTime(markdownContent)

      posts.push({
        slug,
        title: validatedData.title,
        description: validatedData.description,
        date: validatedData.date,
        tags: validatedData.tags,
        category: validatedData.category,
        locale: validatedData.locale,
        readingTime,
        image: validatedData.image,
        featured: validatedData.featured,
      })
    } catch (error) {
      console.error(`Error loading ${filePath}:`, error)
    }
  }

  return posts
}

/**
 * Load a single post by slug
 */
export async function loadPostBySlug(slug: string): Promise<Post | null> {
  for (const [filePath, content] of Object.entries(contentModules)) {
    const fileSlug = filePath.split('/').pop()?.replace('.md', '') || ''

    if (fileSlug === slug) {
      try {
        const markdown = await (content() as Promise<string>)
        const { data, content: markdownContent } = matter(markdown)

        // Validate frontmatter
        const validatedData = postSchema.parse(data)

        return {
          slug,
          content: markdownContent,
          frontmatter: validatedData,
        }
      } catch (error) {
        console.error(`Error loading ${slug}:`, error)
        return null
      }
    }
  }

  return null
}

/**
 * Calculate reading time for markdown content
 * Supports both Chinese (characters) and English (words)
 */
function calculateReadingTime(markdown: string): number {
  // Remove code blocks
  const withoutCodeBlocks = markdown.replace(/```[\s\S]*?```/g, '')

  // Chinese characters (including CJK)
  const chineseChars = withoutCodeBlocks.match(/[\u4e00-\u9fa5]/g)
  const chineseCount = chineseChars ? chineseChars.length : 0

  // English words (split by spaces/punctuation)
  const englishText = withoutCodeBlocks.replace(/[\u4e00-\u9fa5]/g, ' ')
  const englishWords = englishText.trim().split(/\s+/).filter(w => w.length > 0 && /[a-zA-Z]/.test(w))
  const englishCount = englishWords.length

  // Reading speeds: Chinese ~400 chars/min, English ~225 words/min
  const chineseTime = chineseCount / 400
  const englishTime = englishCount / 225

  // Total reading time in minutes
  const totalTime = chineseTime + englishTime

  // Return at least 1 minute, rounded up
  return Math.max(1, Math.ceil(totalTime))
}

/**
 * Get posts by category
 */
export async function getPostsByCategory(
  category: 'blog' | 'projects' | 'life' | 'notes'
): Promise<PostSummary[]> {
  const allPosts = await loadAllContent()
  return allPosts.filter(post => post.category === category)
}

/**
 * Get posts by locale
 */
export async function getPostsByLocale(locale: 'zh' | 'en'): Promise<PostSummary[]> {
  const allPosts = await loadAllContent()
  return allPosts.filter(post => post.locale === locale)
}

/**
 * Get featured posts
 */
export async function getFeaturedPosts(): Promise<PostSummary[]> {
  const allPosts = await loadAllContent()
  return allPosts.filter(post => post.featured)
}

/**
 * Search posts by query
 */
export async function searchPosts(query: string): Promise<PostSummary[]> {
  const allPosts = await loadAllContent()
  const queryLower = query.toLowerCase()

  return allPosts.filter(post =>
    post.title.toLowerCase().includes(queryLower) ||
    post.description.toLowerCase().includes(queryLower) ||
    post.tags.some(tag => tag.toLowerCase().includes(queryLower))
  )
}

/**
 * Get all unique tags
 */
export async function getAllTags(): Promise<string[]> {
  const allPosts = await loadAllContent()
  const tags = new Set<string>()

  allPosts.forEach(post => {
    post.tags.forEach(tag => tags.add(tag))
  })

  return Array.from(tags).sort()
}
