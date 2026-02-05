/**
 * Markdown rendering utilities
 * This is a placeholder for markdown-it or similar
 */
import { shikiToHtml } from 'shiki'

/**
 * Parse markdown to HTML (placeholder)
 * In production, integrate markdown-it or unified/remark with Shiki for syntax highlighting
 */
export async function parseMarkdown(markdown: string): Promise<string> {
  // This is a simplified version - replace with actual markdown parser
  let html = markdown

  // Headers with id generation
  html = html.replace(/^#### (.*$)/gim, '#### <a id="$1" class="header-anchor"></a>$1')
  html = html.replace(/^### (.*$)/gim, '### <a id="$1" class="header-anchor"></a>$1')
  html = html.replace(/^## (.*$)/gim, '## <a id="$1" class="header-anchor"></a>$1')
  html = html.replace(/^# (.*$)/gim, '# <a id="$1" class="header-anchor"></a>$1')

  // Bold and italic
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>')
  html = html.replace(/~~(.*?)~~/gim, '<del>$1</del>')

  // Code blocks (basic - replace with Shiki)
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/gim, (match, lang, code) => {
    return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre>`
  })

  // Inline code
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>')

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2">$1</a>')

  // Images
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/gim, '<img src="$2" alt="$1" loading="lazy" />')

  // Blockquotes
  html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')

  // Horizontal rules
  html = html.replace(/^---$/gim, '<hr />')

  // Line breaks and paragraphs
  html = html.replace(/\n\n/g, '</p><p>')
  html = `<p>${html}</p>`

  // Clean up empty paragraphs
  html = html.replace(/<p><(h[1-6]|ul|ol|blockquote|pre|hr)/g, '<$1')
  html = html.replace(/<\/(h[1-6]|ul|ol|blockquote|pre|hr)><\/p>/g, '</$1>')

  return html
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }
  return text.replace(/[&<>"']/g, m => map[m])
}

/**
 * Extract headings from markdown
 */
export function extractHeadings(markdown: string) {
  const regex = /^(#{1,6})\s+(.+)$/gm
  const headings: { id: string; text: string; level: number }[] = []
  let match

  while ((match = regex.exec(markdown)) !== null) {
    const level = match[1].length
    const text = match[2].trim()
    const id = text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')

    headings.push({ id, text, level })
  }

  return headings
}

/**
 * Extract excerpt from markdown
 */
export function extractExcerpt(markdown: string, maxLength = 200): string {
  // Remove frontmatter
  const withoutFrontmatter = markdown.replace(/^---[\s\S]*?---/g, '')

  // Remove markdown syntax
  const plainText = withoutFrontmatter
    .replace(/#{1,6}\s+/g, '')
    .replace(/\*\*/g, '')
    .replace(/\*/g, '')
    .replace(/`/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')

  // Truncate
  if (plainText.length <= maxLength) {
    return plainText.trim()
  }

  return plainText.substring(0, maxLength).trim() + '...'
}
