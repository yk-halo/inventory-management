# Layout shell: sidebar + topbar + content

Reference implementation for step 3. It is written with `<script setup>`; if the project uses the Options API or a `setup()` function, port it to that style so the new files look native. Adapt names, paths and i18n calls to the project.

## Contents
1. Structure
2. App.vue (shell)
3. AppSidebar.vue
4. Icons
5. Shell CSS
6. Accessibility and behavior checklist

## 1. Structure

```
+-----------+------------------------------------------+
| Brand     | Topbar: page title | filters | actions   |
|-----------+------------------------------------------|
| Nav       |                                          |
|  Overview |  <main> (scrolls)                        |
|  Orders   |    page header                           |
|  ...      |    content, max-width ~1440px            |
|           |                                          |
|-----------|                                          |
| User menu |                                          |
| Collapse  |                                          |
+-----------+------------------------------------------+
```

Desktop: the sidebar is a sticky, full-height column; the content column scrolls with the page. Below 1024px, the sidebar is hidden off-canvas and slides in over an overlay when the topbar's menu button is pressed.

## 2. App.vue (shell)

Keep every component, prop, event and handler that the old header had; only their position changes.

```vue
<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed, 'is-drawer-open': drawerOpen }">
    <AppSidebar
      :collapsed="collapsed"
      :drawer-open="drawerOpen"
      @toggle-collapse="toggleCollapse"
      @close-drawer="drawerOpen = false"
    >
      <template #footer>
        <!-- moved from the old header, events unchanged -->
        <ProfileMenu @show-profile-details="showProfileDetails = true" @show-tasks="showTasks = true" />
      </template>
    </AppSidebar>

    <div class="sidebar-overlay" v-if="drawerOpen" @click="drawerOpen = false" aria-hidden="true" />

    <div class="app-main">
      <header class="topbar">
        <button
          class="icon-btn topbar-menu"
          type="button"
          :aria-expanded="drawerOpen"
          aria-controls="app-sidebar"
          aria-label="Open navigation"
          @click="drawerOpen = true"
        >
          <!-- menu icon svg -->
        </button>
        <h1 class="topbar-title">{{ currentTitle }}</h1>
        <div class="topbar-actions">
          <!-- e.g. LanguageSwitcher, search, notifications -->
        </div>
      </header>

      <!-- a global filter bar, if the app has one, stays full-width here -->

      <main class="content" id="main-content">
        <router-view />
      </main>
    </div>

    <!-- modals that were siblings of the old header stay here, unchanged -->
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

const STORAGE_KEY = 'sidebar-collapsed'
const route = useRoute()

const collapsed = ref(false)
try { collapsed.value = localStorage.getItem(STORAGE_KEY) === '1' } catch {}
const drawerOpen = ref(false)

function toggleCollapse() {
  collapsed.value = !collapsed.value
  try { localStorage.setItem(STORAGE_KEY, collapsed.value ? '1' : '0') } catch {}
}

// Close the mobile drawer whenever the route changes.
watch(() => route.fullPath, () => { drawerOpen.value = false })

function onKeydown(e) { if (e.key === 'Escape') drawerOpen.value = false }
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

// Prefer route meta; fall back to the nav config.
const currentTitle = computed(() => route.meta?.title ?? '')
</script>
```

If the topbar would only hold a title that duplicates each page's own header, drop the title and keep the topbar for actions; or drop the topbar on desktop entirely and show it only below 1024px for the menu button. Don't show the same page title twice.

## 3. AppSidebar.vue

```vue
<template>
  <aside id="app-sidebar" class="sidebar" :class="{ collapsed, open: drawerOpen }">
    <div class="sidebar-brand">
      <span class="brand-mark" aria-hidden="true">A</span>
      <span class="brand-name" v-if="!collapsed">Acme</span>
      <button class="icon-btn sidebar-close" type="button" aria-label="Close navigation" @click="$emit('close-drawer')">
        <!-- x icon -->
      </button>
    </div>

    <nav class="sidebar-nav" aria-label="Main">
      <div v-for="group in groups" :key="group.label" class="nav-group">
        <div v-if="group.label && !collapsed" class="nav-group-label">{{ group.label }}</div>
        <router-link
          v-for="item in group.items"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          :class="{ 'is-active': isActive(item) }"
          :title="collapsed ? item.label : undefined"
        >
          <span class="nav-icon" aria-hidden="true" v-html="item.icon" />
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" />
      <button
        class="nav-item collapse-toggle"
        type="button"
        :aria-pressed="collapsed"
        :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        @click="$emit('toggle-collapse')"
      >
        <!-- chevron icon, rotate when collapsed -->
        <span class="nav-label">Collapse</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRoute } from 'vue-router'
defineProps({ collapsed: Boolean, drawerOpen: Boolean })
defineEmits(['toggle-collapse', 'close-drawer'])

const route = useRoute()
// One array drives the nav. Labels may be i18n keys: use t(item.labelKey) in the template.
const groups = [
  { label: '', items: [
    { to: '/', label: 'Overview', icon: ICONS.home, exact: true },
    // ...
  ]},
]
// `/` must match exactly, otherwise it's active on every page.
function isActive(item) {
  return item.exact ? route.path === item.to : route.path.startsWith(item.to)
}
</script>
```

`v-html` is fine here because the icon strings are constants in the source, not user data. If the project prefers, make each icon a tiny component instead.

If labels come from i18n (`t('nav.orders')`), store the key in the array and translate in the template, so a language switch updates the sidebar reactively.

## 4. Icons

Use the project's icon library if it has one. Otherwise, inline 20x20 stroke SVGs with `stroke="currentColor"` so they pick up the nav item's color. A consistent set (same stroke width, 1.75 or 2, same viewBox 24x24, round caps and joins) matters more than the specific glyphs. Example:

```js
const ICONS = {
  home: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>',
  box: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/></svg>',
  cart: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.5 12h12L22 7H6"/></svg>',
  dollar: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 6.5C17 4.6 14.8 3.5 12 3.5S7 4.8 7 7s2.2 3 5 3.5 5 1.5 5 4-2.2 3.5-5 3.5-5-1.1-5-3"/></svg>',
  trend: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8"/><path d="M14 7h7v7"/></svg>',
  file: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>',
  list: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>',
  settings: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
  menu: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
  close: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  chevronLeft: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>',
}
```

Pick the glyph that matches what the page is about (orders -> cart or list, finance -> dollar, forecast -> trend, reports -> file).

## 5. Shell CSS

Global (unscoped), since the grid spans components. Uses tokens from `assets/tokens.css`.

```css
body { background: var(--color-bg); color: var(--color-text); font-family: var(--font-sans); font-size: var(--text-base); line-height: var(--leading-normal); }

.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  transition: grid-template-columns var(--duration-normal) var(--ease);
}
.app-shell.is-collapsed { grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr); }

.sidebar {
  position: sticky; top: 0; height: 100vh;
  display: flex; flex-direction: column;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  overflow-y: auto; overflow-x: hidden;
  z-index: var(--z-sidebar);
}
.sidebar-brand { display: flex; align-items: center; gap: var(--space-3); height: var(--topbar-height); padding: 0 var(--space-4); border-bottom: 1px solid var(--sidebar-border); }
.brand-mark { display: grid; place-items: center; width: 32px; height: 32px; border-radius: var(--radius-lg); background: var(--color-primary); color: #fff; font-weight: var(--weight-bold); flex-shrink: 0; }
.brand-name { font-weight: var(--weight-semibold); font-size: var(--text-md); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.sidebar-nav { flex: 1; padding: var(--space-3); display: flex; flex-direction: column; gap: var(--space-4); }
.nav-group { display: flex; flex-direction: column; gap: var(--space-1); }
.nav-group-label { padding: 0 var(--space-3); margin-bottom: var(--space-1); font-size: var(--text-xs); font-weight: var(--weight-semibold); letter-spacing: var(--tracking-wide); text-transform: uppercase; color: var(--color-text-muted); }

.nav-item {
  display: flex; align-items: center; gap: var(--space-3);
  height: 36px; padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--sidebar-item-fg); text-decoration: none;
  font-size: var(--text-base); font-weight: var(--weight-medium);
  white-space: nowrap;
  border: 0; background: none; cursor: pointer; width: 100%; text-align: left;
  transition: background var(--duration-fast) var(--ease), color var(--duration-fast) var(--ease);
}
.nav-item:hover { background: var(--sidebar-item-hover-bg); color: var(--color-text); }
.nav-item.is-active { background: var(--sidebar-item-active-bg); color: var(--sidebar-item-active-fg); }
.nav-item:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.nav-icon { display: inline-flex; flex-shrink: 0; }

.sidebar.collapsed .nav-label,
.sidebar.collapsed .brand-name,
.sidebar.collapsed .nav-group-label { display: none; }
.sidebar.collapsed .nav-item { justify-content: center; padding: 0; }
.sidebar.collapsed .collapse-toggle .nav-icon { transform: rotate(180deg); }

.sidebar-footer { padding: var(--space-3); border-top: 1px solid var(--sidebar-border); display: flex; flex-direction: column; gap: var(--space-2); }

.app-main { display: flex; flex-direction: column; min-width: 0; }
.topbar {
  position: sticky; top: 0; z-index: var(--z-topbar);
  display: flex; align-items: center; gap: var(--space-4);
  height: var(--topbar-height); padding: 0 var(--space-8);
  background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
}
.topbar-title { font-size: var(--text-md); font-weight: var(--weight-semibold); }
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-2); }
/* Prefix with .icon-btn so these win over .icon-btn's display (same specificity, declared later) */
.icon-btn.topbar-menu, .icon-btn.sidebar-close { display: none; }

.content { width: 100%; max-width: var(--content-max-width); margin: 0 auto; padding: var(--space-8); }

.icon-btn { display: inline-grid; place-items: center; width: 36px; height: 36px; border-radius: var(--radius-md); border: 0; background: none; color: var(--color-text-secondary); cursor: pointer; }
.icon-btn:hover { background: var(--color-surface-hover); color: var(--color-text); }
.icon-btn:focus-visible { outline: none; box-shadow: var(--focus-ring); }

.sidebar-overlay { display: none; }

@media (max-width: 1023px) {
  .app-shell, .app-shell.is-collapsed { grid-template-columns: minmax(0, 1fr); }
  .sidebar {
    position: fixed; inset: 0 auto 0 0; width: var(--sidebar-width);
    transform: translateX(-100%); transition: transform var(--duration-normal) var(--ease);
    z-index: var(--z-drawer); box-shadow: var(--shadow-lg);
  }
  .sidebar.open { transform: none; }
  /* The rail mode is desktop-only: always show labels in the drawer */
  .sidebar.collapsed .nav-label, .sidebar.collapsed .brand-name, .sidebar.collapsed .nav-group-label { display: revert; }
  .sidebar.collapsed .nav-item { justify-content: flex-start; padding: 0 var(--space-3); }
  .collapse-toggle { display: none; }
  .sidebar-overlay { display: block; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); z-index: var(--z-overlay); }
  .icon-btn.topbar-menu, .icon-btn.sidebar-close { display: inline-grid; }
  .icon-btn.sidebar-close { margin-left: auto; }
  .topbar { padding: 0 var(--space-4); }
  .content { padding: var(--space-4); }
}
```

## 6. Accessibility and behavior checklist

- `<nav aria-label="Main">` wraps the links; `router-link` sets `aria-current="page"` on the exact-active link.
- Every icon-only control (menu, close, collapse, rail-mode links) has an accessible name (`aria-label` or `title` plus visually hidden text).
- Focus is visible on every interactive element (`:focus-visible` ring), and the tab order goes sidebar -> topbar -> content.
- The drawer closes on Escape, overlay click and route change; the menu button exposes `aria-expanded`.
- Collapsed state survives a reload; reading/writing `localStorage` is wrapped in `try/catch` so private mode can't crash the app.
- Dropdowns that used to open *downward* from a top header may now sit at the bottom of the sidebar: make sure they open upward/right and aren't clipped by `overflow: hidden` on the sidebar (use `position: fixed` or teleport if needed).
- With the sidebar collapsed, nothing in the sidebar overflows horizontally.
