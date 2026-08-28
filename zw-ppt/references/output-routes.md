# Output routes

## Route selection

| Need | Preferred route |
|---|---|
| Client-facing, executive, proposal, keynote, or visually demanding deck | HTML master -> clean images -> PDF + image-based PPTX |
| User asks for “PPT” without saying it must be editable | HTML-first high-fidelity route |
| Fully editable Office deck is explicitly required | Native PPTX |
| High-fidelity browser presentation | HTML-first high-fidelity route |
| Reliable review or handoff | PDF |
| Both visual fidelity and editability | High-fidelity HTML master plus separately named native editable PPTX derivative |
| Social or image slides | Rendered PNG/JPG pages |

Do not choose a route only because it is technically convenient.

Do not infer that “做PPT” means native editability. Unless the user explicitly prioritizes editable elements or Office-native collaboration, prefer the high-fidelity HTML-first route.

## High-fidelity presentation route

Use HTML as the visual source of truth, then render clean 16:9 pages. Assemble both the PDF and PowerPoint delivery from the same verified page images.

Requirements:

- read `high-fidelity-html-first.md`;
- design and verify the HTML master before packaging downstream formats;
- keep all downstream formats visually identical to the approved HTML;
- use `scripts/images_to_pptx.py` for the PowerPoint package;
- clearly label the PPTX as image-based and internally non-editable;
- preserve speaker notes when a notes JSON is available.

## Native PPTX

Use the installed presentation-generation capability when the user needs editable text, shapes, charts, notes, themes, or corporate Office compatibility. Use `ppt-master` when its SVG-to-PPTX workflow is the better fit for bespoke editable slide systems.

Requirements:

- preserve editability where feasible;
- use slide masters or reusable layout functions;
- keep text as text and diagrams as shapes/SVG when possible;
- add speaker notes when requested or useful;
- render the PPTX to images/PDF for inspection;
- open or parse the produced file to verify slide count and structure.

Do not use native PPTX merely because the requested filename ends in `.pptx`. Do not create an image-only PPTX without stating the limitation.

## HTML presentation

Use HTML when the deck benefits from precise web typography, responsive scaling, custom interaction, embedded media, or rapid visual iteration.

Start from `assets/html-deck/deck-template.html` and replace:

- content;
- visual tokens;
- page layouts;
- images and diagrams;
- metadata and notes.

Technical requirements:

- fixed 16:9 design canvas, recommended 1600×900;
- stage centered with `left:50%`, `top:50%`, and `translate(-50%,-50%) scale(...)`;
- slides use DOM order unless there is a compelling reason otherwise;
- core content visible without animation JavaScript;
- keyboard navigation and hash-based page address;
- speaker-note panel or embedded note content when useful;
- `?clean=1` or equivalent to hide controls during export;
- print/static styles that do not crop or offset pages;
- all local assets embedded or packaged reliably for delivery.

Use `scripts/render_html_deck.cjs` to render and audit every page.

## PDF

Prefer exporting from the verified final artifact. For HTML decks:

1. render clean 16:9 PNG pages;
2. confirm controls are absent;
3. assemble with `scripts/images_to_pdf.py`;
4. inspect PDF metadata and page count;
5. render selected or all PDF pages back to PNG for comparison.

For PPTX, use the available office/PDF conversion route, then inspect the PDF.

## Multiple formats

Maintain a single content specification containing:

- ordered slide list;
- titles and body copy;
- citations;
- visual description;
- notes;
- asset mapping.

For the high-fidelity route, derive HTML, PNG, PDF, and image-based PPTX from one approved visual master. For a native editable derivative, build separately from the shared specification and allow format-specific layout changes. Verify every output independently.

Do not assume HTML-to-PPTX or PPTX-to-HTML conversion preserves editability, fonts, image cropping, notes, or animation.

## Asset packaging

- Use descriptive asset names.
- Avoid duplicate images unless repetition is intentional.
- Keep generated-image prompts or provenance notes when useful for later revision.
- Embed assets in a single HTML only when portability outweighs file size.
- Otherwise deliver a clearly structured folder with relative paths.
- Never expose credentials or local secrets in source files or exported notes.
