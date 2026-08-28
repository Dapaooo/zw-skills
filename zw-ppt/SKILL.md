---
name: zw-ppt
description: Create, redesign, edit, and validate general-purpose presentations across high-fidelity HTML, image-based PPTX, editable PPTX, PDF, and rendered slide images. Use when the user asks to 做PPT、制作演示文稿、把材料变成幻灯片、改版现有PPT、优化叙事或视觉、增加图表与配图、生成讲稿，或导出并检查演示文件。Default visually demanding or client-facing work to an HTML-first master with page-specific image integration and rendered PPTX/PDF delivery; use native editable PPTX only when editability is explicitly important. Never assume a fixed industry, topic, palette, or deck type.
---

# ZW PPT

Build presentations as communication systems, not paginated documents. Start from audience, purpose, evidence, and speaking context; then design narrative, pages, visuals, and deliverables around them.

## Load the right guidance

- For every new deck or major redesign, read [content-workflow.md](references/content-workflow.md) and [visual-system.md](references/visual-system.md).
- Before choosing or implementing a file format, read [output-routes.md](references/output-routes.md).
- For visually demanding, client-facing, or image-rich work, also read [high-fidelity-html-first.md](references/high-fidelity-html-first.md).
- For client-facing decks, management communication, or iterative redesign from page-specific feedback, also read [client-facing-expression.md](references/client-facing-expression.md).
- Before delivery, read and execute [qa-checklist.md](references/qa-checklist.md).
- For HTML-first work, copy and adapt [deck-template.html](assets/html-deck/deck-template.html). Do not preserve its neutral sample theme by default.

## Core rules

1. Infer the presentation type from the request. Do not force every deck into a business proposal, training course, keynote, investor pitch, or report pattern.
2. Establish one audience, one desired outcome, and one speaking situation before designing pages.
3. Make each slide perform one clear job. Split a slide when it contains multiple competing conclusions.
4. Write direct, specific titles that state the page's message. Avoid vague labels and habitual contrast formulas such as “不是……而是……”.
5. Treat public facts, source facts, inference, and proposal as different evidence levels. Never disguise speculation as fact.
6. Use visual structure to explain relationships. Do not decorate text with unrelated icons, generic gradients, or repeated AI images.
7. Make body text readable in a real room. A slide that only works when zoomed in is not finished.
8. Verify the rendered artifact page by page. Successful file generation is not proof of a usable presentation.
9. Keep visible slide language inside the subject matter. Put production commentary, speaking directions, and phrases such as “this deck will” or “next we look at” in notes, not on the slide.
10. Make every mechanism diagram speakable. The audience should be able to trace who supplies what, who acts, and what result changes without decoding an abstract framework.

## Default quality policy

Treat “make a PPT” as a request for a presentation outcome, not automatically as a request for editable Office objects.

- Default client-facing, executive, keynote, brand, proposal, and visually demanding decks to the **high-fidelity HTML-first route**.
- Use HTML as the visual source of truth, render it to clean 16:9 images, assemble the PDF from those images, and package the same images into a PPTX when the user asks for PowerPoint.
- State clearly that this high-fidelity PPTX is image-based and not internally editable.
- Choose native editable PPTX only when the user explicitly prioritizes editing, templates, Office-native charts, collaboration, or downstream reuse of individual elements.
- If both fidelity and editability matter, deliver two clearly named files: a high-fidelity presentation version and an editable derivative. Do not silently lower the visual standard to preserve editability.

## Workflow

### 1. Understand the assignment

Identify or reasonably infer:

- audience and decision level;
- desired action after the presentation;
- live presentation, self-reading, or both;
- source materials and research needs;
- target length and speaking time;
- required outputs: PPTX, HTML, PDF, images, notes;
- brand assets, tone, language, and deadline.

Ask only for choices that materially change the result. State non-blocking assumptions and continue.

If the user asks to review the plan before production, stop after the page map and art direction. Do not build the final deck until approved.

### 2. Build an evidence base

Read every supplied source before outlining. For current, external, high-stakes, or attribution-sensitive claims, research with primary and authoritative sources.

Classify content as:

- verified fact;
- source interpretation;
- working hypothesis;
- recommendation;
- illustrative example.

Keep citations close to the claim when the medium allows it. For live slides, use compact sources and place fuller references in notes or an appendix.

### 3. Design the narrative

Create a page map with, at minimum:

- slide number;
- slide job;
- message title;
- key evidence or content;
- visual form;
- speaker-note intent;
- source status.

Choose the opening, sequence, and conclusion for the audience. Do not automatically lead with a conclusion or delay it; use the structure that best supports the decision.

When the material contains cases at different levels of complexity, order them by the reasoning path the audience needs—often `specific problem -> small closed loop -> connected processes -> system capability`—rather than by company prestige or size alone.

For enterprise enablement decks, finish with a usable decision path when appropriate: select a worthwhile business problem, confirm data/owner/execution entry, run a bounded real-work pilot, and judge whether to continue by business results. Adapt the steps to the topic; do not force them onto unrelated deck types.

Add chapter transitions when they create useful pacing, especially in decks longer than about 12 slides. A transition page should reset attention and preview the next reasoning step, not merely display “Chapter 2”.

### 4. Set art direction

Choose a visual system from the topic and situation:

- palette and contrast;
- typography and density;
- grid and recurring page chrome;
- image language;
- diagram and chart language;
- chapter rhythm;
- motion policy.

Use light or dark pages according to the content and environment. Keep a coherent system, but allow structural variety across slides.

Use image generation when a bespoke scene, metaphor, background, or cutout materially improves understanding. Generate each important scene for its specific page, avoid repeated hero images, and ensure image prompts reserve usable space for text.

For high-fidelity decks, treat generated imagery as part of the composition rather than a rectangular decoration. Compose text, crops, masks, gradients, annotations, and negative space together in HTML. Generate different scenes for different slide jobs.

### 5. Choose the output route

Follow [output-routes.md](references/output-routes.md):

- choose HTML-first rendered delivery by default when visual quality and client impact dominate;
- package verified rendered pages into an image-based PPTX when PowerPoint delivery is requested;
- choose native PPTX when editability and Office compatibility are explicitly important;
- export PDF for reliable review and presentation handoff;
- when multiple formats are requested, keep one visual source of truth and verify each format separately.

Never call a screenshot-based PPTX editable. Label the tradeoff before or at handoff; do not hide it in fine print.

### 6. Build in passes

Work in this order:

1. content lock: story and factual claims;
2. structure lock: page map and slide roles;
3. design lock: visual system and representative pages;
4. production: complete all slides;
5. polish: alignment, density, imagery, sources, notes;
6. export and validation.

When feedback exposes a system problem—small text, weak transitions, repeated images, uneven whitespace, unclear diagrams—fix the underlying rule across the deck, then repair individual slides.

When the user gives page-number feedback, map every comment to the current rendered order before editing. Update the content specification, source document, slide master, speaker notes, and downstream outputs together. Re-render the affected pages first, then the whole deck; do not patch only the exported PPTX.

For visually important work, design at least three representative pages before full production: the cover, a dense content page, and a diagram or chapter transition. When user review is available and the user has not asked for uninterrupted completion, show these pages for direction approval before producing the whole deck.

### 7. Validate before delivery

Execute the full [qa-checklist.md](references/qa-checklist.md). At minimum:

- render every slide;
- inspect every slide visually;
- confirm slide order and count;
- check overflow, clipping, blank content, and centering;
- verify fonts, images, links, notes, and citations;
- confirm export controls are absent from PDF;
- compare the final PDF/PPTX/HTML against the approved structure.

## HTML-first utilities

Use the bundled scripts when the HTML route is selected:

```bash
node scripts/render_html_deck.cjs deck.html render-dir
node scripts/render_html_deck.cjs deck.html clean-render-dir --clean
python3 scripts/images_to_pdf.py clean-render-dir deck.pdf
python3 scripts/images_to_pptx.py clean-render-dir deck.pptx --title "Presentation title"
```

If Playwright or Python packages are not on the default path, load the workspace dependency paths and run the same scripts with the bundled runtimes.

The renderer writes `render-report.json` and flags slide overflow, missing active slides, page errors, and visible export controls. The PPTX packager creates a visually identical image-based deck; use `--notes-json` when speaker notes are available.

## Handoff

Lead with what was completed. Link the actual final files. Briefly report:

- slide count and formats;
- the chosen narrative and visual direction;
- validation performed;
- any remaining assumptions or editability limitations;
- which file is the high-fidelity source of truth and whether a separate editable derivative exists.

Do not make the user infer which file is final.
