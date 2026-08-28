# Web and Product UI

Use this reference for websites, apps, dashboards, design systems, and components.

## Inspect Before Designing

Read the relevant project files before changing code:

- framework, routes, component ownership, styling system, and build commands;
- font loading, color and spacing tokens, breakpoints, and existing design primitives;
- assets already supplied by the project;
- motion dependencies and established interaction patterns;
- nearby components and states that the change must preserve.

Default to in-place or additive changes. Do not remove route trees, production components, or broad sections unless the user requested that scope.

## Choose a Page Shape

Choose the structure from the content and task rather than applying a universal landing-page formula. Useful structural families include:

- **Narrative/editorial**: a strong reading sequence with changing pace and evidence embedded in prose.
- **Workbench/product**: persistent controls or navigation around the main task surface.
- **Evidence-led**: proof, data, comparison, or demonstration establishes value before claims.
- **Catalogue/grid**: browsing and comparison are the primary job; grid rhythm reflects priority.
- **Manifesto/poster**: one position or idea dominates; supporting content is deliberately sparse.
- **Demo-led**: the real product interaction or media is the hero.
- **Split/asymmetric**: two complementary ideas need simultaneous presence.
- **Utility/document**: search, tables, filters, docs, or dense information outrank spectacle.

Vary section rhythm, alignment, density, and image treatment. Centered, split, bento, and card-based layouts are options, never defaults.

## Hierarchy and Responsive Layout

- Keep the dominant heading broad enough to avoid a narrow wall of text. Size it according to copy length and language.
- Validate grid spans at every relevant breakpoint. Use `minmax(0, 1fr)` for tracks containing shrinkable media or long text when appropriate.
- Prevent horizontal overflow without hiding content bugs. Prefer `overflow-x: clip` only when off-canvas decoration or animation requires it.
- Preserve meaningful DOM and keyboard order; visual density must not reorder the task incoherently.
- Check at representative mobile, tablet, and desktop widths. For public responsive pages, include narrow widths around 320–414 px when the environment permits.
- Keep clickable labels readable and avoid cramped wrapping in primary actions and navigation.

## Components and States

For interactive components, implement all applicable states:

- default, hover, focus-visible, active;
- disabled and loading when the action can be unavailable or asynchronous;
- error and success when the component owns validation or completion feedback;
- empty, selected, expanded, or skeleton states when the product flow requires them.

Do not manufacture irrelevant states for static components. Focus indicators must be immediate and visible. Success feedback should not duplicate a result the user can already see.

## Typography, Color, and Assets

- Preserve existing font and token systems. For a new system, use a limited set of type roles and named color/spacing tokens.
- Avoid choosing a font because it signals “startup,” “editorial,” or “premium” in isolation. Pair it with the content voice and rendering needs.
- Ensure essential text and controls meet accessible contrast; do not rely on opacity alone for disabled or secondary information.
- Use real product screenshots, supplied images, licensed assets, CSS/SVG craft, or clearly marked placeholders.
- Never redraw fake browser, phone, IDE, or code-window chrome merely to make a screenshot look impressive.

## Motion and Interaction

Use the project’s existing motion approach. If none exists, prefer restrained CSS transitions.

- Animate opacity and transforms when possible; avoid layout-thrashing properties.
- Specify transition properties rather than `transition: all`.
- Give one element one primary hover response; do not pile on scale, rotation, translation, color, and shadow.
- Avoid applying the same `scale(1.05)` effect across unrelated elements.
- Respect reduced-motion preferences.
- Use scroll pinning, scrubbing, parallax, or card stacking only when they make the story or task easier to understand.

## Marketing Pages

Stage a progression from attention to understanding, evidence, and action, but do not force AIDA labels or a fixed section sequence. Hero imagery is optional. Typography-only, product-demo, editorial, or asymmetric heroes may be stronger than a cinematic centered composition.

Keep CTA quantity proportional to the real decision. Do not invent proof bars, logo walls, metrics, or testimonials to fill a template.

## Product and Dashboard Interfaces

Prioritize task flow, data hierarchy, empty/error/loading states, responsive behavior, and accessibility. Keep ornament subordinate to scanning and decision-making. Dense interfaces benefit from restrained motion and stable placement more than dramatic chapter spacing.

## Web Handoff Checks

Run the project’s relevant checks and visually inspect when possible:

1. Routes, component boundaries, copy intent, and data behavior remain correct.
2. Heading wraps, grids, media, navigation, and controls work at target widths.
3. Interactive states and keyboard focus are present and legible.
4. Color contrast, alt text, semantics, and reduced motion are appropriate.
5. No accidental horizontal scroll, clipping, layout shift, or empty grid cells remain.
6. Motion and decoration reinforce hierarchy rather than competing with it.
