# Client-facing expression and revision

Use this reference for management-facing decks, client communication, case-based reports, and page-specific redesign feedback.

## 1. Keep slide language inside the subject

The slide should speak about the business, idea, evidence, or decision—not about the deck as an artifact.

Replace presentation commentary with content language:

| Avoid on the slide | Prefer on the slide |
|---|---|
| 整场演示围绕三个问题展开 | 先回答三个问题 |
| 先看中小企业，再看大型企业 | 从中小企业小闭环到大型企业系统协同 |
| 从技术能力到经营结果 | 怎样进入制造业务 |
| 这一页说明三者关系 | 系统供数据，AI作判断，业务把判断变成结果 |

Put “how to say this,” “what comes next,” caveats, and transitions in speaker notes.

Run a visible-language lint before delivery. Search for phrases such as `本页`、`这一页`、`整场演示`、`接下来`、`后面将`、`我们先看`、`本PPT` and rewrite them unless the slide is explicitly an agenda or navigation page.

## 2. Build the reasoning sequence, not a prestige sequence

Order cases and chapters by the audience's learning or decision path. A useful enterprise-AI progression is:

`AI capability -> advantage and conditions -> business embedding -> value areas -> policy or market context -> bounded business cases -> system cases -> common operating logic -> how to start -> result-based decision`

When comparing smaller and larger enterprises, a useful progression is:

`specific loss -> small closed loop -> connected processes -> system collaboration -> repeatable capability`

Do not automatically put famous or large companies first. Use size only when it supports the reasoning.

## 3. Control title roles

Define visible text roles before styling:

- **Eyebrow**: classification, chapter number, evidence level, or step label.
- **Title**: the page's main content message.
- **Subtitle**: one sentence that narrows or explains the title.
- **Speaker note**: delivery guidance, nuance, caveat, or transition.

Do not place speaking instructions in the title or subtitle.

For a chapter transition:

1. Make the chapter name or central question the largest or most prominent text.
2. Make the explanatory statement clearly smaller.
3. Keep the supporting paragraph short.
4. Verify the hierarchy in a contact sheet; the chapter title should remain readable there.

## 4. Keep repeated-page labels consistent

Define a label taxonomy before producing repeated case pages. The label should explain why the case is in this group.

Examples:

- `中小企业小闭环`
- `大型企业系统协同`
- `经营响应案例`
- `设备持续服务`

Do not mix a meaningful taxonomy with generic fallbacks such as `真实企业案例` inside the same group.

## 5. Make mechanisms easy to speak

Prefer a role or flow model when the audience needs to understand execution:

`input/data owner -> AI action -> business user/system action -> review/responsibility -> changed result`

For each node, answer:

- What enters?
- What does AI do?
- Who receives the output?
- Who acts or reviews?
- What result changes?

Avoid abstract layer diagrams when the layer relationship does not explain a handoff. If the presenter cannot explain the diagram in one sentence or trace it with one finger, redesign it.

## 6. End with a usable path

For enterprise enablement, the last pages should usually help the audience act rather than repeat general conclusions. A practical sequence is:

1. Select a specific, measurable, frequent or complex business problem with a clear owner.
2. Confirm the data source, responsible user/reviewer, and execution entry.
3. Run a bounded pilot in real work; establish a baseline and record exceptions.
4. Compare technical and business results, then decide to continue, adjust, narrow, or stop.

Technical metrics answer whether the system works. Business metrics answer whether it is worth continuing.

## 7. Apply page-number feedback safely

Page numbers refer to the rendered order, which may drift after insertions or deletions.

1. Render or inspect the current deck and map each page number to its title.
2. Convert each comment into a content rule, visual rule, or page-local edit.
3. Fix the system rule first when the problem repeats across pages.
4. Keep MD/source content, HTML or native slide source, speaker notes, and exported formats synchronized.
5. Re-render representative affected pages, then the full deck.
6. Re-run overflow, contact-sheet, PPTX/PDF, notes, and offline-asset checks.

Do not edit only the flattened PPTX or only the MD when both are part of the requested deliverable.
