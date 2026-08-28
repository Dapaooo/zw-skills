# High-fidelity HTML-first route

Use this route when the deck must look polished, direct, cinematic, editorial, brand-specific, or client-ready and the user has not explicitly made native editability the priority.

## Deliverable model

Maintain one visual source of truth:

`content spec -> HTML master -> clean PNG pages -> PDF + image-based PPTX`

The HTML master owns typography, layout, image crops, masks, diagrams, chapter rhythm, and notes. The PNG, PDF, and PPTX outputs must derive from the verified HTML pages rather than being redesigned independently.

If editable slides are also needed, build a separately named native PPTX derivative after the high-fidelity version is approved. Treat it as a second implementation, not an automatic conversion.

## Production sequence

1. Lock the audience, outcome, evidence, and page map.
2. Define an art-direction sentence and image language.
3. Build the cover, one dense content page, and one diagram or transition page.
4. Confirm that the images, type, spacing, and information structure feel like one composition.
5. Produce the complete HTML deck from the same system.
6. Embed local assets when a portable single-file HTML is useful.
7. Render normal and clean-export pages at 1600x900.
8. Inspect every page and a contact sheet; repair system-level problems first.
9. Assemble the PDF from clean pages.
10. Package the same clean pages into an image-based PPTX.
11. Render the PPTX and PDF back to images and compare them with the HTML source.

## Image integration

Give each important image a specific slide job: establish place, explain a mechanism, visualize a future state, mark a chapter change, or supply evidence.

- Generate page-specific scenes; do not recycle one hero image throughout the deck.
- Reserve negative space in the prompt for the planned title or annotation area.
- Avoid generated text inside images unless it is intentionally part of the scene.
- Use CSS crops, masks, soft overlays, foreground overlap, tonal grading, and annotations to fuse the image with the page.
- Match lighting, perspective, palette, and realism across the deck without forcing identical compositions.
- Reject generic AI brains, holograms, handshakes, and decorative technology motifs that do not explain the subject.

## HTML constraints

- Use a fixed 1600x900 design canvas.
- Center the stage at multiple viewport sizes; target zero center offset.
- Keep core content visible without animation.
- Disable translation-based page motion in clean export to avoid residual frames or compositor edges.
- Hide controls, progress, notes, overview, and help in clean export.
- Ensure local assets work offline; embed them when portability outweighs file size.
- Do not rely on browser zoom to make small text readable.

## PPTX packaging

Use `scripts/images_to_pptx.py` to place each clean 16:9 page image edge-to-edge on a blank slide. Add speaker notes through `--notes-json` when available.

This PPTX preserves the approved appearance but its internal page content is flattened. Name or describe it as “high-fidelity” or “presentation version,” never “editable.”

When an editable derivative is required:

- preserve the approved narrative, page jobs, image language, and hierarchy;
- rebuild text and simple diagrams natively;
- accept and disclose small rendering differences;
- validate it independently rather than assuming parity.

## Acceptance criteria

- The cover establishes the deck's specific world rather than looking like a template.
- Images and text form one composition instead of occupying unrelated rectangles.
- Chapter pages create visual breathing room and preview the next reasoning mode.
- Dense slides remain readable in a room.
- Bottom whitespace is purposeful.
- Repeated points, lines, curves, labels, and cards align precisely.
- Normal HTML, clean PNG, PDF, and high-fidelity PPTX show the same page order and composition.
- Exported pages contain no controls, residual animation, clipping, offset, black edges, or previous-page ghosting.
