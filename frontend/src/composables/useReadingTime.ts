/**
 * Calculate reading time for text content
 * Based on average reading speed of 200-250 words per minute
 */
export function useReadingTime(text: string): number {
  const wordsPerMinute = 225
  const words = text.trim().split(/\s+/).length
  const minutes = Math.ceil(words / wordsPerMinute)
  return minutes
}

/**
 * Calculate reading time for markdown content
 */
export function useMarkdownReadingTime(markdown: string): number {
  // Remove code blocks for estimation
  const withoutCodeBlocks = markdown.replace(/```[\s\S]*?```/g, '')

  // Remove inline code
  const withoutInlineCode = withoutCodeBlocks.replace(/`[^`]+`/g, '')

  // Count words
  const words = withoutInlineCode.trim().split(/\s+/).filter(w => w.length > 0).length

  const wordsPerMinute = 225
  const minutes = Math.ceil(words / wordsPerMinute)

  return minutes
}
