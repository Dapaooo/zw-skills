# Presentation QA checklist

## Content

- [ ] Audience, objective, and desired decision are clear.
- [ ] Slide order matches the approved page map.
- [ ] Every slide has one main job and a message title.
- [ ] Claims are supported, qualified, or labeled as hypotheses/examples.
- [ ] Sources are readable and connected to the correct claims.
- [ ] The conclusion and next action are explicit.
- [ ] Speaker notes add value instead of repeating slide text.
- [ ] Visible slide copy stays inside the subject matter; production commentary and speaking directions appear only in notes.
- [ ] Repeated case or portfolio pages use consistent classification labels.
- [ ] The ending gives the audience a usable decision or action path when the deck's purpose requires one.

## Visual

- [ ] Every slide has a clear focal point.
- [ ] Body and chart text remain readable at presentation scale.
- [ ] Important content is not crowded in one corner.
- [ ] Bottom whitespace is intentional rather than unfinished layout.
- [ ] Repeated components align precisely.
- [ ] Lines, nodes, arrows, labels, and curves visually connect.
- [ ] Images are relevant, sharp, properly cropped, and not unintentionally repeated.
- [ ] Color and typography remain coherent across chapters.
- [ ] Chapter transitions create pacing and preview the next section.
- [ ] On chapter transitions, the chapter title is visually dominant over its explanation.
- [ ] Mechanism diagrams show actors, handoffs, responsibility, and results clearly enough to explain in one sentence.
- [ ] No generic placeholders, broken images, or decorative charts remain.

## HTML

- [ ] All slides render at the intended 16:9 canvas.
- [ ] The stage is centered at several viewport sizes.
- [ ] Hash navigation, keyboard controls, notes, overview, and fullscreen work as intended.
- [ ] Core content remains visible before or without animation.
- [ ] No horizontal or vertical overflow is reported.
- [ ] No console/page errors affect the presentation.
- [ ] Clean export hides controls, help, progress, notes, and overview.
- [ ] Local/embedded assets work without network access when required.

Run:

```bash
node scripts/render_html_deck.cjs deck.html render
node scripts/render_html_deck.cjs deck.html clean-render --clean
```

Review `render-report.json`, then inspect all rendered pages or a contact sheet. Do not stop at automated overflow checks.

## PPTX

- [ ] Slide count and order are correct.
- [ ] Text, shapes, charts, and notes remain editable where promised.
- [ ] Fonts are available or substituted safely.
- [ ] No text is clipped after PowerPoint rendering.
- [ ] Images retain crop and resolution.
- [ ] Charts and diagrams remain aligned.
- [ ] Speaker notes exist on the intended slides.
- [ ] The file opens without repair warnings.
- [ ] The handoff states whether the PPTX is image-based or natively editable.

For an image-based high-fidelity PPTX:

- [ ] Every slide uses the corresponding clean HTML render edge-to-edge.
- [ ] Page order and count match the HTML/PDF source of truth.
- [ ] No controls, progress bars, notes panels, ghost frames, or black edges appear.
- [ ] Speaker notes are present when supplied.
- [ ] The file is not described as editable.

Render the PPTX to PDF or images and inspect every slide.

## PDF

- [ ] Page count matches the final deck.
- [ ] Page dimensions and orientation are consistent.
- [ ] No browser controls or export UI are visible.
- [ ] Images and text are sharp enough for display.
- [ ] Links and citations are preserved when required.
- [ ] Selected pages rendered back from the PDF match the source deck.

## Final handoff

- [ ] Final filenames are unambiguous.
- [ ] The user receives clickable links to the real files.
- [ ] The delivered directory contains no temporary renders unless useful.
- [ ] Any synced copy is byte-checked against the workspace final.
- [ ] Remaining limitations or assumptions are stated briefly.
- [ ] The high-fidelity source of truth and any editable derivative are named unambiguously.
- [ ] Page-number feedback was checked against the current rendered order, and source, notes, MD, PPTX, PDF, and HTML remain synchronized.
