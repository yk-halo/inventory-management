<template>
  <aside id="app-sidebar" class="sidebar" :class="{ collapsed, open: drawerOpen }">
    <div class="sidebar-brand">
      <span class="brand-mark" aria-hidden="true">C</span>
      <div class="brand-text">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </div>
      <button
        class="icon-btn sidebar-close"
        type="button"
        :aria-label="t('nav.closeMenu')"
        @click="$emit('close-drawer')"
      >
        <span v-html="ICONS.close" />
      </button>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.mainNavigation')">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ 'is-active': isActive(item) }"
        :title="collapsed ? t(item.labelKey) : undefined"
      >
        <span class="nav-icon" aria-hidden="true" v-html="item.icon" />
        <span class="nav-label">{{ t(item.labelKey) }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" />
      <button
        class="nav-item collapse-toggle"
        type="button"
        :aria-pressed="collapsed"
        :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        :title="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        @click="$emit('toggle-collapse')"
      >
        <span class="nav-icon" aria-hidden="true" v-html="ICONS.chevronLeft" />
        <span class="nav-label">{{ t('nav.collapse') }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'

defineProps({ collapsed: Boolean, drawerOpen: Boolean })
defineEmits(['toggle-collapse', 'close-drawer'])

const { t } = useI18n()
const route = useRoute()

const svg = (body) =>
  `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`

// Constant strings from source, not user data
const ICONS = {
  home: svg('<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>'),
  box: svg('<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>'),
  cart: svg('<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.5 12h12L22 7H6"/>'),
  dollar: svg('<path d="M12 2v20M17 6.5C17 4.6 14.8 3.5 12 3.5S7 4.8 7 7s2.2 3 5 3.5 5 1.5 5 4-2.2 3.5-5 3.5-5-1.1-5-3"/>'),
  trend: svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/>'),
  file: svg('<path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>'),
  close: svg('<path d="M6 6l12 12M18 6 6 18"/>'),
  chevronLeft: svg('<path d="m15 18-6-6 6-6"/>')
}

const items = [
  { to: '/', labelKey: 'nav.overview', icon: ICONS.home, exact: true },
  { to: '/inventory', labelKey: 'nav.inventory', icon: ICONS.box },
  { to: '/orders', labelKey: 'nav.orders', icon: ICONS.cart },
  { to: '/spending', labelKey: 'nav.finance', icon: ICONS.dollar },
  { to: '/demand', labelKey: 'nav.demandForecast', icon: ICONS.trend },
  { to: '/reports', labelKey: 'nav.reports', icon: ICONS.file }
]

const isActive = (item) => (item.exact ? route.path === item.to : route.path.startsWith(item.to))
</script>
