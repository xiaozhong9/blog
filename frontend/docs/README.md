# Nano Banana 🍌

A world-class personal blog system built with Vue 3, TypeScript, and Tailwind CSS.

## Features

- ✨ **Modern Design** - Josh Comeau-inspired design with soft gradients and smooth animations
- 🌓 **Theme System** - Light/Dark/System mode with persistent preferences
- 🌍 **Internationalization** - Built-in Chinese (default) and English support
- 🔍 **Full-text Search** - Cmd+K search with keyboard navigation
- 📝 **Markdown Content** - Write posts in Markdown with frontmatter validation
- 🎯 **Type Safety** - Full TypeScript with Zod validation
- ⚡ **Fast Performance** - Vite for instant HMR and optimized builds
- 📱 **Responsive Design** - Mobile-first approach

## Tech Stack

- **Framework**: Vue 3 (Composition API + Script Setup + TypeScript)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: unplugin-vue-router (file-based)
- **i18n**: vue-i18n
- **Icons**: Iconify (Lucide)
- **Content**: Markdown + gray-matter + Zod
- **Code Highlighting**: Shiki

## Project Structure

```
src/
├── components/      # Reusable UI components
│   ├── home/        # Homepage sections
│   ├── layout/      # Layout components (navbar, footer)
│   ├── content/     # Content-related components
│   ├── projects/    # Project cards
│   ├── life/        # Life journal cards
│   ├── search/      # Search modal
│   └── ui/          # Base UI components
├── composables/     # Vue composables
├── content/         # Markdown content files
├── design-tokens/   # Design system tokens
├── layouts/         # Page layouts
├── locales/         # i18n translations
├── pages/           # File-based routing pages
├── stores/          # Pinia stores
├── styles/          # Global styles
├── types/           # TypeScript type definitions
├── utils/           # Utility functions
├── App.vue          # Root component
└── main.ts          # Entry point
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm, yarn, or pnpm

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Development

```bash
# Run dev server
npm run dev

# Type check
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## Content Management

Content is stored as Markdown files in `src/content/`. Each file must have frontmatter:

```markdown
---
title: "Your Post Title"
description: "A brief description"
date: "2024-01-15"
tags: ["vue", "typescript"]
category: "blog"
locale: "zh"
featured: false
draft: false
---

Your content here...
```

### Content Categories

- `blog` - Technical articles and tutorials
- `projects` - Project showcase
- `life` - Personal journal
- `notes` - Quick notes and snippets

## Design Tokens

### Colors

```css
/* Primary Gradient */
from: #60A5FA (blue)
to: #A78BFA (purple)

/* Light Theme */
background: #F8FAFC
surface: #FFFFFF
text-primary: #0F172A
text-secondary: #475569
border: #E2E8F0

/* Dark Theme */
background: #0B1120
surface: #111827
text-primary: #E2E8F0
text-secondary: #94A3B8
border: #1E293B
```

### Motion

```css
fast: 150ms
normal: 300ms
spring: cubic-bezier(0.22, 1, 0.36, 1)
```

## Keyboard Shortcuts

- `Cmd/Ctrl + K` - Open search
- `ESC` - Close modals
- `↑/↓` - Navigate search results
- `Enter` - Select search result

## License

MIT © Nano Banana
