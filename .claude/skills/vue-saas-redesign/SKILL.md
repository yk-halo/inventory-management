---
name: vue-saas-redesign
description: Redesign a Vue 3 application's UI into a modern, polished SaaS-style interface - replace the top navigation bar with a collapsible vertical sidebar on the left, introduce a design-token system (spacing scale, type scale, radii, shadows, colors), and restyle every view (page headers, cards, KPI tiles, tables, buttons, forms, badges, modals) for consistent spacing and a professional look, without changing app behavior. Use this skill whenever someone wants a Vue / Vite / vue-router app to "look more modern", "look like a SaaS product", "look professional", "feel like Linear/Stripe/Vercel", get a "sidebar nav" or "left nav" instead of a header/top nav/tab bar, "clean up the spacing", "make the UI consistent", "give the dashboard a facelift", or "redesign the layout", even if they don't say "SaaS" or "sidebar". Not for building new features, React/Angular/Svelte apps, or restyling one isolated component.
---

# Vue 3 SaaS Redesign

Turn a Vue 3 app with a top nav into a modern SaaS-style app: a left sidebar shell, a token-based design system, and every view restyled to match - while every route, filter, modal, translation and API call keeps working exactly as before.

The user is asking for a *visual* change. The fastest way to lose their trust is to break something that worked, so behavior preservation outranks polish at every step.

## What "done" looks like

- A **sidebar** on the left (about 240px wide) holding the brand, the primary nav with icons, and the user/account area at the bottom. It collapses to an icon rail (about 64px) on desktop and becomes an off-canvas drawer with a hamburger toggle below 1024px.
- A slim **top bar** inside the content column for page-level things (page title or breadcrumb, global filters, search, secondary actions). Anything that lived in the old header but isn't navigation goes here or into the sidebar footer - nothing is dropped.
- **Design tokens** as CSS custom properties (or the Tailwind theme, if the app uses Tailwind) that every style references: a 4px-based spacing scale, a type scale, radii, shadows, border and surface colors, and the app's existing brand/status colors.
- **Every view restyled** with the same page-header pattern, card treatment, table style, button and form styles, and vertical rhythm, so moving between pages feels like one product.
- The app **builds**, every route renders with no new console errors, and the layout holds at desktop (1440px) and mobile (390px) widths.

## Workflow

### 1. Survey before touching anything

Read enough to answer these, and write the answers down in a short scratch note (they drive every later step):

- **Project rules.** Read `CLAUDE.md` / `AGENTS.md` / `README` for design-system constraints (colors, "no emojis", fonts) and workflow rules (e.g. "delegate .vue edits to the vue-expert subagent", "use Playwright MCP for browser testing"). Follow them; they override this skill's defaults.
- **Routing.** Find the router (`src/router/index.*`, `src/main.*`). List every route, its path, name and `meta`. Note nested routes and route-level layouts.
- **Current shell.** Find where the top nav lives (`App.vue`, `layouts/*.vue`, `components/*Nav*`/`*Header*`). List everything inside it: links, logo, language switchers, profile menus, notification bells, search, global filter bars, and the events they emit. Each one needs a new home.
- **Styling approach.** Global CSS in `App.vue` or `src/assets/*.css`? Scoped styles per component? Tailwind (`tailwind.config.*`)? A component library (Vuetify, PrimeVue, Element Plus, Quasar, Naive UI)? Work *with* what's there: with Tailwind, put tokens in the theme and use utilities; with a component library, use its theming/layout primitives (e.g. `v-navigation-drawer`) instead of hand-rolling; with plain CSS, use custom properties.
- **Component style.** Options API, `setup()` function, or `<script setup>`? TypeScript? Match the project's style in new components so they look like they belong.
- **i18n.** If nav labels go through `t(...)` / `$t(...)`, keep using the same keys.
- **Icons.** Does the app already depend on an icon library? If yes, use it. If not, use inline SVG (see `references/layout-shell.md`) rather than adding a dependency - never emojis.

Then run the style audit to get a baseline you can compare against at the end:

```bash
python <skill-dir>/scripts/audit_styles.py <app-src-dir>
```

It reports off-scale spacing values, off-scale font sizes, and raw hex colors per file. You don't need to reach zero - but the redesign should cut these sharply.

### 2. Build the token layer

Start from `assets/tokens.css` and adapt it:

- **Keep the brand.** Pull the app's existing primary/accent color, status colors (success/warning/danger/info) and font stack into the tokens. A redesign that swaps the brand blue for a different blue reads as a mistake, not a polish. If the project's docs name design colors, those win.
- Put the tokens where global styles already load (a new `src/styles/tokens.css` imported in `main.js`, or the top of the existing global stylesheet).
- Keep the spacing scale on the 4px grid (4, 8, 12, 16, 20, 24, 32, 40, 48, 64). Consistent spacing is mostly the discipline of only using these values.

### 3. Build the shell

Read `references/layout-shell.md` for the component structure, CSS and the accessibility details. In short:

- Create `AppSidebar.vue` (brand, nav groups, footer slot for the user menu) and, if the old header had page-level tools, `AppTopbar.vue`.
- Drive nav items from a single array (path, label key, icon) rather than repeated `<router-link>` blocks. If routes carry `meta.title`/`meta.icon`, read from the router instead.
- Use `router-link`'s own active classes (`router-link-active` / `router-link-exact-active`) and `aria-current`; the root route `/` needs exact matching or it will look active everywhere.
- Rewrite `App.vue` (or the layout) as a CSS grid: `sidebar | content`, where content = topbar + scrollable `<main>`. Move, don't rewrite, the components that were in the header - keep their props, events and handlers byte-for-byte where possible.
- Collapse state: a ref, persisted to `localStorage` inside `try/catch`. Mobile drawer: closes on route change, on overlay click and on Escape.
- Delete the old top-nav markup and its now-dead CSS, so it can't fight the new layout.

### 4. Restyle every view

Read `references/component-patterns.md` for the recipes. Work view by view through *every* routed view and every modal/dialog, not only the dashboard:

- Give each page the same header pattern (title, optional description, actions on the right).
- Replace hard-coded spacing, font sizes, radii, shadows and colors with tokens. Shared classes (`.card`, `.stat-card`, `table`, `.badge`, `.btn`) should be defined once globally; remove scoped duplicates that only re-declare them with slightly different numbers.
- Leave `<script>` logic, props, emits, computed properties, API calls, `v-for` keys and template data bindings alone. Only change template structure where the layout needs it (e.g. wrapping a page header), and keep every binding when you do.
- Charts: restyle containers, axes and gridlines with tokens; don't change the data or chart math.

### 5. Verify

Do all of these and report what you saw - don't claim success you didn't observe:

1. `npm run build` (or the project's build script) passes.
2. Start the app (or use the running one), and visit **every** route at 1440x900 and at 390x844. Use Playwright MCP if available, otherwise any headless browser. Check for console errors, horizontal scrolling, overlapping elements, clipped text and nav items that wrap badly.
3. Click the things that moved: each nav link, the collapse toggle, the mobile hamburger, the profile/language/notification menus, global filters, and at least one modal per view.
4. Re-run `audit_styles.py` and compare with the baseline.
5. Save screenshots of each route (desktop and mobile) if the user or caller wants to review them.

### 6. Report

Finish with a short summary for the user: the new layout in one or two sentences, files added and changed, where the tokens live, the before/after audit numbers, what you verified (and how), and anything you couldn't verify or deliberately left alone.

## Judgment calls

- **Many nav items (8+)?** Group them under small uppercase section labels ("Operations", "Finance", "Settings").
- **Global filter bar under the old header?** Keep it full-width at the top of the content column (inside or just below the topbar), not in the sidebar - filters scope the page content, so they belong next to it.
- **Existing layout system (e.g. `layouts/DefaultLayout.vue`, Nuxt layouts)?** Put the shell there instead of `App.vue`, and leave auth/blank layouts untouched.
- **Dark mode?** Only if the app already has it or the user asks. If it does, define the tokens for both themes.
- **Big app (20+ views)?** Do the shell and tokens first, verify, then restyle views in batches, building after each batch so a mistake is caught near its cause.
