---
name: zw-taste
description: Unified visual taste and anti-generic design workflow for creating, improving, reviewing, auditing, redesigning, or studying web interfaces, dashboards, components, presentations, documents, infographics, social posts, book cards, and other visual deliverables. Use when a task needs art direction, information hierarchy, composition, typography, imagery, color, responsive behavior, interaction polish, structural variety, or removal of AI-generated visual patterns. Route by medium and task depth so simple work stays fast while major builds and redesigns receive deeper checks.
---

# ZW Taste

Produce visual work that is clear, specific, and made for its subject. Combine content-first art direction, strong web implementation, and anti-template discipline without forcing every task through the same heavy workflow.

## Route Before Loading References

Classify along two axes: **medium** and **depth**. Do not load every reference.

### Pick one primary medium

- **Web/product UI**: sites, landing pages, dashboards, apps, design systems, UI components. Read [web.md](references/web.md).
- **Visual content**: presentations, documents, reports, infographics, social posts, book cards, editorial graphics. Read [visual-content.md](references/visual-content.md).
- **Hybrid**: interactive reports, web-based decks, visual dashboards. Read both only when both implementation and page/slide composition materially matter.

### Pick the lightest sufficient depth

- **Quick**: one component, one slide/card, localized polish, or a straightforward review. Load only the primary medium reference. Use the compact quality pass below.
- **Standard**: a complete page, flow, deck, document, card series, dashboard, or meaningful redesign. Load the primary medium reference and run its full handoff checks.
- **Deep**: a greenfield identity-bearing experience, multi-page system, major redesign, explicit anti-AI-slop request, repeated outputs that risk sameness, or `audit`, `redesign`, `study`, `lock the system`. Also read [advanced.md](references/advanced.md).

Do not upgrade to Deep merely because the output should look premium. Complexity must earn its time and token cost.

## Establish Direction

Infer from the brief and existing files before asking questions. Identify:

1. Audience and viewing context.
2. One intended takeaway or primary action.
3. Medium, format, and real delivery size.
4. Existing brand, design system, template, or code constraints.
5. A short visual thesis: the idea or mood the work should leave behind.

Ask one concise question only when a missing choice would materially change the result. If inference is safe, proceed and briefly state only non-obvious assumptions.

## Core Rules

Apply these at every depth:

1. Preserve existing identity and implementation conventions unless redesign is requested.
2. Make hierarchy legible before adding decoration. Keep one primary message or action per page, slide, card, or viewport.
3. Make the structure fit the content. Do not default to hero → equal cards → CTA or repeat the same left/right split.
4. Use no more than three obvious hierarchy levels: primary, supporting evidence, utility detail.
5. Prefer fewer intentional modules. Avoid nested cards, accidental empty grid cells, badge clutter, and walls of equal-weight tiles.
6. Keep headings breathable and readable. Adjust width and type scale before accepting awkward wraps.
7. Treat whitespace as structure and vary rhythm deliberately; do not apply cinematic padding mechanically.
8. Use meaningful labels. Avoid decorative `SECTION 01`, `QUESTION 05`, or generic eyebrow text.
9. Start from existing type, color, spacing, assets, and motion. Add new visual language only when it clarifies the thesis.
10. Never fabricate metrics, testimonials, customers, logos, or product evidence. Use labelled placeholders or change the composition.
11. Use motion for feedback, transition, or pacing. Never add a library or spectacle merely to signal quality.
12. Verify the actual output at its intended size. Check hierarchy, alignment, crop, contrast, overflow, states, and small-size readability.

## Work Sequence

1. **Inspect** the source of truth: content, current implementation, brand files, assets, dependencies, and target format.
2. **Reduce** the brief to audience, action/takeaway, constraints, and visual thesis.
3. **Choose structure first**, then typography, color, imagery, and motion.
4. **Build or review** at the selected depth. Match effort to consequence.
5. **Render or run** the result when tools permit. Inspect the real artifact, not only source code.
6. **Revise once** when a material issue is visible. Do not create process theatre with unsupported scores.
7. **Hand off** the result and mention only tradeoffs the user needs to decide.

For reviews or audits, diagnose and rank issues without editing unless the user asked for changes.

## Compact Quality Pass

Use for Quick tasks and as the final pass for all others:

- Can the primary message or action be identified in a few seconds?
- Does the composition feel specific to this subject rather than reusable for anything?
- Are type, spacing, alignment, color, imagery, and interaction internally consistent?
- Are important text and controls legible, accessible, and unclipped at the target size?
- Is every decorative element earning its place?
- Did the result preserve relevant content, brand, routes, states, and implementation boundaries?

Fix failures before handoff. Do not claim a test passed unless it was actually inspected or executed.

## Efficiency Contract

- Read at most one primary medium reference for Quick and Standard work.
- Read `advanced.md` only for Deep work or explicit `audit`, `redesign`, `study`, and system-locking requests.
- Do not load external catalogues, all style examples, or unrelated reference files speculatively.
- Prefer existing project dependencies and assets. Do not install a motion or UI library without need and authorization.
- Do not generate a long design rationale before implementation. Surface a short direction note only when it helps the user redirect meaningful choices.
- Persist design history only when repeated outputs in the same project make it useful; otherwise keep the run stateless.

## Precedence

When rules conflict, apply this order:

1. User intent and supplied content.
2. Existing brand/design system and product conventions.
3. Accessibility, correctness, and delivery constraints.
4. Content hierarchy and task flow.
5. Structural specificity and anti-template variety.
6. Stylistic novelty and motion.

Restraint wins when novelty competes with clarity.
