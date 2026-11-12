# Component patterns for the restyle

Recipes for step 4. They describe *what polished SaaS UI does*; map them onto the class names the app already uses (rename only when a name is actively misleading). Define shared patterns once in the global stylesheet; in scoped styles, keep only what is truly specific to that component.

## Contents
1. Principles
2. Page header
3. Cards and sections
4. KPI / stat tiles
5. Tables
6. Buttons
7. Forms and filters
8. Badges and status
9. Modals and dropdowns
10. Loading, empty and error states
11. Charts
12. Common mistakes

## 1. Principles

- **Rhythm.** 32px between major page sections, 24px between cards in a grid, 16-24px padding inside cards, 8-12px between related items. When unsure, pick the larger value on the scale: cramped looks amateur sooner than airy does.
- **Hierarchy through type and color, not boxes.** One page title (24-30px, bold, tight tracking), section titles at 16px semibold, body at 14px, meta text at 12-13px in a muted color. Avoid nesting bordered boxes inside bordered boxes.
- **Quiet surfaces.** White cards on a very light gray background, 1px `--color-border` borders, at most `--shadow-xs` at rest. Stronger shadows are for things that float (dropdowns, modals, drawer).
- **Color is for meaning.** Brand color on primary actions, active nav and links; status colors on status. Everything else is neutral.
- **Numbers line up.** `font-variant-numeric: tabular-nums` on KPI values and numeric table columns; right-align numeric columns.

## 2. Page header

```html
<div class="page-header">
  <div>
    <h1 class="page-title">Orders</h1>
    <p class="page-description">Track open, shipped and delayed orders.</p>
  </div>
  <div class="page-actions"><!-- buttons --></div>
</div>
```

```css
.page-header { display: flex; align-items: flex-end; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; margin-bottom: var(--space-6); }
.page-title { font-size: var(--text-2xl); font-weight: var(--weight-bold); letter-spacing: var(--tracking-tight); line-height: var(--leading-tight); color: var(--color-text); }
.page-description { margin-top: var(--space-1); font-size: var(--text-base); color: var(--color-text-muted); }
.page-actions { display: flex; gap: var(--space-2); }
```

Keep the view's existing heading element and text; if it's an `h2` because the old header used `h1` for the brand, it can stay `h2` - what matters is that every page uses the same pattern.

## 3. Cards and sections

```css
.card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-xl); box-shadow: var(--shadow-xs); padding: var(--space-6); }
.card + .card, .card-grid + .card { margin-top: var(--space-6); }
.card-header { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-4); }
.card-title { font-size: var(--text-md); font-weight: var(--weight-semibold); color: var(--color-text); }
.card-subtitle { font-size: var(--text-sm); color: var(--color-text-muted); margin-top: 2px; }
.card-grid { display: grid; gap: var(--space-6); grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }
```

A card that contains only a table can drop its inner padding (`padding: 0`) and let the table run edge to edge, with the card header padded on its own. That looks cleaner than a table floating inside a padded box.

## 4. KPI / stat tiles

```css
.stats-grid { display: grid; gap: var(--space-4); grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin-bottom: var(--space-8); }
.stat-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-xl); padding: var(--space-5); box-shadow: var(--shadow-xs); }
.stat-label { font-size: var(--text-sm); font-weight: var(--weight-medium); color: var(--color-text-muted); }
.stat-value { margin-top: var(--space-2); font-size: var(--text-3xl); font-weight: var(--weight-semibold); letter-spacing: var(--tracking-tight); font-variant-numeric: tabular-nums; color: var(--color-text); }
.stat-meta { margin-top: var(--space-2); font-size: var(--text-xs); color: var(--color-text-muted); }
```

Prefer sentence-case labels over shouty uppercase. Keep status modifiers (`.stat-card.warning`) but make them subtle, e.g. color the value or add a small colored dot, not a full colored background.

## 5. Tables

```css
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: var(--text-base); }
th { position: sticky; top: 0; background: var(--color-surface-muted); text-align: left; font-size: var(--text-xs); font-weight: var(--weight-semibold); text-transform: uppercase; letter-spacing: var(--tracking-wide); color: var(--color-text-muted); padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--color-border); white-space: nowrap; }
td { padding: var(--space-3) var(--space-4); border-bottom: 1px solid var(--color-border); color: var(--color-text-secondary); }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover td { background: var(--color-surface-muted); }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
```

Row height around 44-48px reads as "comfortable" SaaS density. Clickable rows get `cursor: pointer`.

## 6. Buttons

```css
.btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); height: 36px; padding: 0 var(--space-4); border-radius: var(--radius-md); font-size: var(--text-base); font-weight: var(--weight-medium); border: 1px solid transparent; cursor: pointer; transition: background var(--duration-fast) var(--ease), border-color var(--duration-fast) var(--ease); }
.btn:focus-visible { outline: none; box-shadow: var(--focus-ring); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-primary); color: #fff; }
.btn-primary:hover { background: var(--color-primary-hover); }
.btn-secondary { background: var(--color-surface); color: var(--color-text); border-color: var(--color-border-strong); box-shadow: var(--shadow-xs); }
.btn-secondary:hover { background: var(--color-surface-hover); }
.btn-ghost { background: none; color: var(--color-text-secondary); }
.btn-ghost:hover { background: var(--color-surface-hover); color: var(--color-text); }
.btn-sm { height: 30px; padding: 0 var(--space-3); font-size: var(--text-sm); }
```

If buttons already have class names (`.add-btn`, `.submit-button`), either add the shared classes alongside them or point the existing names at the same declarations. Don't rename classes that script code queries.

## 7. Forms and filters

```css
.input, select, input[type="text"], input[type="search"], input[type="number"], input[type="date"], textarea {
  height: 36px; padding: 0 var(--space-3); border: 1px solid var(--color-border-strong); border-radius: var(--radius-md);
  background: var(--color-surface); color: var(--color-text); font: inherit; font-size: var(--text-base);
  transition: border-color var(--duration-fast) var(--ease), box-shadow var(--duration-fast) var(--ease);
}
textarea { height: auto; padding: var(--space-2) var(--space-3); }
.input:focus, select:focus, input:focus, textarea:focus { outline: none; border-color: var(--color-focus); box-shadow: var(--focus-ring); }
label, .field-label { display: block; font-size: var(--text-sm); font-weight: var(--weight-medium); color: var(--color-text-secondary); margin-bottom: var(--space-1); }
.filter-bar { display: flex; flex-wrap: wrap; align-items: flex-end; gap: var(--space-3); padding: var(--space-3) var(--space-8); background: var(--color-surface); border-bottom: 1px solid var(--color-border); }
```

Be careful scoping element selectors (`input`, `select`) globally if the app uses a component library - its inputs carry their own styles.

## 8. Badges and status

```css
.badge { display: inline-flex; align-items: center; gap: var(--space-1); height: 22px; padding: 0 var(--space-2); border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: var(--weight-medium); white-space: nowrap; }
.badge.success { background: var(--success-bg); color: var(--success-fg); }
.badge.warning { background: var(--warning-bg); color: var(--warning-fg); }
.badge.danger  { background: var(--danger-bg);  color: var(--danger-fg); }
.badge.info    { background: var(--info-bg);    color: var(--info-fg); }
```

Keep every existing badge modifier the templates use (e.g. `.badge.high`, `.badge.stable`) and map each to one of the four status pairs (or neutral gray), so no badge loses its color. Search the templates for the dynamic class bindings that produce them before deleting any.

## 9. Modals and dropdowns

- Overlay: `rgba(15, 23, 42, 0.45)`, optional `backdrop-filter: blur(2px)`.
- Panel: `--color-surface`, `--radius-xl`, `--shadow-lg`, max-width 560-720px, header/body/footer separated by spacing or a single 1px border, footer actions right-aligned (secondary then primary).
- Dropdown menus: `--radius-lg`, `--shadow-md`, 1px border, items 32-36px tall with `--space-3` horizontal padding.
- z-index from the token layer (`--z-modal`) so modals sit above the sidebar and drawer.

## 10. Loading, empty and error states

- Loading: a muted, centered message or skeleton blocks in `--gray-100`; never a layout jump when data arrives (reserve height where practical).
- Empty: short muted sentence plus, if relevant, a primary action.
- Error: `--danger-bg` background, `--danger-fg` text, `--radius-lg`, 12-16px padding.

## 11. Charts

Restyle, don't rebuild. Gridlines `--gray-200`, axis labels `--text-xs` in `--color-text-muted`, series colors from the brand/status tokens, chart titles as `.card-title`. Leave scales, data mapping and SVG geometry logic untouched.

## 12. Common mistakes

- Restyling the dashboard and forgetting the other views and the modals.
- Deleting a CSS class that a template still binds dynamically (`:class="item.status"`), silently stripping color from badges.
- Leaving the old `max-width` + `margin: 0 auto` wrapper and padding in place inside the new content area, so content gets double padding.
- Sticky table headers or topbars ending up underneath the sidebar because of z-index.
- Global `button { ... }` rules that restyle every button in the app, including icon buttons in third-party components.
- Changing the brand color "because it looks better".
- Large KPI numbers wrapping mid-figure ("$31,166,85 / 3"): give `.stat-value` `white-space: nowrap` and a fluid size such as `clamp(1.25rem, 2.2vw, 1.875rem)`, or widen the tile's minimum.
- Wide charts and tables overflowing at 390px: wrap them in a container with `overflow-x: auto` so they scroll inside their card, and confirm `document.documentElement.scrollWidth <= 390` on every route in the browser check.
