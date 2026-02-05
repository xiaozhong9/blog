/**
 * SEO Utilities - Generate meta tags for social sharing and search engines
 */
import type { MetaDescriptor } from '@unhead/vue'

export interface SEOProps {
  title?: string
  description?: string
  image?: string
  url?: string
  type?: 'website' | 'article'
  publishedTime?: string
  modifiedTime?: string
  tags?: string[]
  author?: string
}

/**
 * Generate SEO meta tags
 */
export function generateMetaTags(props: SEOProps): MetaDescriptor[] {
  const {
    title = 'Nano Banana - Personal Blog & Knowledge Sharing',
    description = 'A world-class personal blog system built with Vue 3.',
    image = '/og-image.png',
    url = window.location.href,
    type = 'website',
    publishedTime,
    modifiedTime,
    tags,
    author = 'Nano Banana',
  } = props

  const meta: MetaDescriptor[] = []

  // Primary Meta Tags
  meta.push({ name: 'title', content: title })
  meta.push({ name: 'description', content: description })

  // Open Graph / Facebook
  meta.push({ property: 'og:type', content: type })
  meta.push({ property: 'og:url', content: url })
  meta.push({ property: 'og:title', content: title })
  meta.push({ property: 'og:description', content: description })
  meta.push({ property: 'og:image', content: image })

  if (type === 'article') {
    if (publishedTime) {
      meta.push({ property: 'article:published_time', content: publishedTime })
    }
    if (modifiedTime) {
      meta.push({ property: 'article:modified_time', content: modifiedTime })
    }
    if (author) {
      meta.push({ property: 'article:author', content: author })
    }
    if (tags && tags.length > 0) {
      tags.forEach(tag => {
        meta.push({ property: 'article:tag', content: tag })
      })
    }
  }

  // Twitter Card
  meta.push({ name: 'twitter:card', content: 'summary_large_image' })
  meta.push({ name: 'twitter:url', content: url })
  meta.push({ name: 'twitter:title', content: title })
  meta.push({ name: 'twitter:description', content: description })
  meta.push({ name: 'twitter:image', content: image })

  return meta
}

/**
 * Generate JSON-LD structured data
 */
export function generateJsonLd(props: SEOProps & { type: 'article' | 'website' | 'person' }): string {
  const base = {
    '@context': 'https://schema.org',
  }

  if (props.type === 'article') {
    return JSON.stringify({
      ...base,
      '@type': 'BlogPosting',
      headline: props.title,
      description: props.description,
      image: props.image,
      url: props.url,
      datePublished: props.publishedTime,
      dateModified: props.modifiedTime,
      author: {
        '@type': 'Person',
        name: props.author,
      },
      keywords: props.tags?.join(', '),
    })
  }

  if (props.type === 'website') {
    return JSON.stringify({
      ...base,
      '@type': 'WebSite',
      name: props.title,
      description: props.description,
      url: props.url,
    })
  }

  if (props.type === 'person') {
    return JSON.stringify({
      ...base,
      '@type': 'Person',
      name: props.author,
      url: props.url,
    })
  }

  return JSON.stringify(base)
}

/**
 * Generate canonical URL
 */
export function generateCanonicalUrl(path?: string): string {
  const baseUrl = 'https://nanobanana.dev'
  return path ? `${baseUrl}${path}` : baseUrl
}

/**
 * Page title template
 */
export function getPageTitle(pageTitle?: string): string {
  return pageTitle ? `${pageTitle} | Nano Banana` : 'Nano Banana - Personal Blog & Knowledge Sharing'
}

/**
 * Composable for using SEO in components
 */
export function useSEO(props: SEOProps) {
  const meta = generateMetaTags(props)
  const jsonLd = generateJsonLd({ ...props, type: props.type || 'website' })
  const canonical = generateCanonicalUrl(props.url)

  return {
    meta,
    jsonLd,
    canonical,
    title: getPageTitle(props.title),
  }
}
