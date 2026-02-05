<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { onClickOutside } from '@vueuse/core'
import { useSearchStore } from '@/stores/search'
import { Icon } from '@iconify/vue'

const router = useRouter()
const { t } = useI18n()
const searchStore = useSearchStore()

const searchInput = ref<HTMLInputElement>()
const selectedIndex = ref(0)

// Keyboard navigation
const handleKeydown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      searchStore.navigate('down')
      selectedIndex.value = searchStore.selectedIndex
      break
    case 'ArrowUp':
      e.preventDefault()
      searchStore.navigate('up')
      selectedIndex.value = searchStore.selectedIndex
      break
    case 'Enter':
      e.preventDefault()
      const slug = searchStore.selectResult()
      if (slug) {
        router.push(`/blog/${slug}`)
      }
      break
    case 'Escape':
      searchStore.close()
      break
  }
}

// Focus input when modal opens
watch(() => searchStore.isOpen, (isOpen) => {
  if (isOpen) {
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})

// Close on click outside
const modalRef = ref<HTMLElement>()
onClickOutside(modalRef, () => {
  searchStore.close()
})

// Select result
const selectResult = (slug: string) => {
  searchStore.addToHistory(searchStore.query)
  searchStore.close()
  router.push(`/blog/${slug}`)
}

// Clear query
const clearQuery = () => {
  searchStore.setQuery('')
  searchInput.value?.focus()
}
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="searchStore.isOpen"
        class="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]
               bg-black/50 backdrop-blur-sm"
      >
        <div
          ref="modalRef"
          class="w-full max-w-2xl mx-4 overflow-hidden
                 bg-light-surface dark:bg-dark-surface
                 rounded-2xl shadow-soft-lg
                 border border-light-border dark:border-dark-border"
          @keydown="handleKeydown"
        >
          <!-- Search Input -->
          <div class="flex items-center gap-3 px-4 py-3 border-b border-light-border dark:border-dark-border">
            <Icon icon="lucide:search" class="w-5 h-5 text-light-text-muted dark:text-dark-text-muted" />
            <input
              ref="searchInput"
              :value="searchStore.query"
              @input="searchStore.setQuery($event.target?.value ?? '')"
              type="text"
              :placeholder="t('nav.searchPlaceholder')"
              class="flex-1 bg-transparent border-none outline-none
                     text-light-text-primary dark:text-dark-text-primary
                     placeholder:text-light-text-muted dark:placeholder:text-dark-text-muted"
            />
            <button
              v-if="searchStore.query"
              @click="clearQuery"
              class="p-1 rounded text-light-text-muted dark:text-dark-text-muted
                     hover:bg-light-bg dark:hover:bg-dark-bg
                     transition-colors duration-150"
            >
              <Icon icon="lucide:x" class="w-4 h-4" />
            </button>
            <kbd class="hidden sm:inline-block px-2 py-1 text-xs
                         bg-light-bg dark:bg-dark-bg
                         text-light-text-muted dark:text-dark-text-muted
                         border border-light-border dark:border-dark-border
                         rounded">ESC</kbd>
          </div>

          <!-- Results -->
          <div class="max-h-[60vh] overflow-y-auto">
            <!-- Search Results -->
            <div v-if="searchStore.results.length > 0" class="p-2">
              <div class="text-xs font-semibold uppercase tracking-wider
                          text-light-text-muted dark:text-dark-text-muted
                          px-3 py-2">
                {{ t('search.results', { count: searchStore.results.length }) }}
              </div>
              <button
                v-for="(result, index) in searchStore.results"
                :key="result.id"
                @click="selectResult(result.slug)"
                class="w-full flex items-start gap-3 px-3 py-2 rounded-lg
                       text-left transition-colors duration-150
                       hover:bg-light-bg dark:hover:bg-dark-bg"
                :class="{
                  'bg-light-bg dark:bg-dark-bg': index === searchStore.selectedIndex,
                }"
              >
                <Icon
                  :icon="result.category === 'blog' ? 'lucide:file-text' :
                         result.category === 'projects' ? 'lucide:folder' : 'lucide:heart'"
                  class="w-5 h-5 mt-0.5 text-light-text-muted dark:text-dark-text-muted"
                />
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-light-text-primary dark:text-dark-text-primary">
                    {{ result.title }}
                  </div>
                  <div class="text-sm text-light-text-secondary dark:text-dark-text-secondary
                              line-clamp-1 mt-0.5">
                    {{ result.description }}
                  </div>
                  <div class="flex items-center gap-2 mt-1">
                    <span
                      v-for="tag in result.tags.slice(0, 3)"
                      :key="tag"
                      class="text-xs px-1.5 py-0.5 rounded
                             bg-light-bg dark:bg-dark-bg
                             text-light-text-muted dark:text-dark-text-muted"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
              </button>
            </div>

            <!-- No Results -->
            <div v-else-if="searchStore.query" class="p-8 text-center">
              <Icon
                icon="lucide:search-x"
                class="w-12 h-12 mx-auto mb-4
                       text-light-text-muted dark:text-dark-text-muted"
              />
              <p class="text-light-text-secondary dark:text-dark-text-secondary">
                {{ t('search.noResults') }}
              </p>
            </div>

            <!-- Recent & Popular -->
            <div v-else class="p-4">
              <!-- Recent Searches -->
              <div v-if="searchStore.recentSearches.length > 0" class="mb-6">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-semibold text-light-text-muted dark:text-dark-text-muted">
                    {{ t('search.recent') }}
                  </h3>
                  <button
                    @click="searchStore.clearHistory()"
                    class="text-xs text-light-text-muted dark:text-dark-text-muted
                           hover:text-primary-from transition-colors duration-150"
                  >
                    Clear
                  </button>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="item in searchStore.recentSearches"
                    :key="item.query"
                    @click="searchStore.setQuery(item.query)"
                    class="px-3 py-1.5 text-sm rounded-lg
                           bg-light-bg dark:bg-dark-bg
                           text-light-text-secondary dark:text-dark-text-secondary
                           hover:bg-light-border dark:hover:bg-dark-border
                           transition-colors duration-150"
                  >
                    {{ item.query }}
                  </button>
                </div>
              </div>

              <!-- Popular Searches -->
              <div>
                <h3 class="text-sm font-semibold text-light-text-muted dark:text-dark-text-muted mb-2">
                  {{ t('search.popular') }}
                </h3>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="query in searchStore.popularSearches"
                    :key="query"
                    @click="searchStore.setQuery(query)"
                    class="px-3 py-1.5 text-sm rounded-lg
                           bg-light-bg dark:bg-dark-bg
                           text-light-text-secondary dark:text-dark-text-secondary
                           hover:bg-light-border dark:hover:bg-dark-border
                           transition-colors duration-150"
                  >
                    {{ query }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between px-4 py-2 border-t
                        border-light-border dark:border-dark-border">
            <div class="flex items-center gap-4 text-xs text-light-text-muted dark:text-dark-text-muted">
              <span class="flex items-center gap-1">
                <kbd class="px-1.5 py-0.5 bg-light-bg dark:bg-dark-bg rounded">↵</kbd>
                to select
              </span>
              <span class="flex items-center gap-1">
                <kbd class="px-1.5 py-0.5 bg-light-bg dark:bg-dark-bg rounded">↑↓</kbd>
                to navigate
              </span>
            </div>
            <span class="text-xs text-light-text-muted dark:text-dark-text-muted">
              ⌘K to open
            </span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
