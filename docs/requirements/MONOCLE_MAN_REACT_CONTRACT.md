# Monocle Man React Contract

**Status:** required before the next Monocle Man implementation round  
**Purpose:** convert the Monocle Man SPA from an aesthetic page into a deterministic React surface that GitHub Actions can verify.

## Why this exists

ChatGPT must not begin another Monocle Man coding round from prose alone. If a complete implementation plan is not supplied, ChatGPT must create and commit one first.

The page is simple. The hard part is preventing vague execution, false-green screenshots, and untestable UI. This contract defines the exact React components, stable selectors, actions, and CI checks that must exist before a pass can be claimed.

## External references to check before implementation

A Monocle Man implementation round must use current web references before patching, at minimum:

1. React documentation for component, event, and accessibility behavior.
2. W3C WAI-ARIA Authoring Practices for the modal dialog pattern.
3. The current `grahama1970/agent-skills` `best-practices-react` skill.

The WAI-ARIA modal dialog pattern requires focus to move inside the dialog when it opens, Tab and Shift+Tab to stay inside the dialog, Escape to close it, a visible close button in the tab sequence, and a dialog container labelled by visible title or aria-label. Those requirements are part of this contract.

## Governing best-practices-react rule

Every interactive React element must have all four items at write time:

1. `data-qid` using `component:element:qualifier` format.
2. `data-qs-action` using uppercase action format.
3. `title` as a human-readable label.
4. `useRegisterAction` call at the top level of the owning component.

A component missing this instrumentation is not shippable.

## Required React components

The Monocle Man SPA must be split into these components:

1. `MonocleManApp`
2. `SkipLink`
3. `HeaderNav`
4. `HeroSection`
5. `FilmSection`
6. `RulesSection`
7. `QuoteGallery`
8. `VerdictSection`
9. `VideoModal`
10. `Footer`

No extra app framework, database, chat surface, login, or agent UI is allowed in this slice.

## Required static element IDs

These elements must exist in the live DOM and be visible where applicable:

| Component | Element | `data-qid` | Check |
|---|---|---|---|
| `MonocleManApp` | app root | `monocle:app:root` | exists |
| `MonocleManApp` | main landmark | `monocle:main:content` | focusable target for skip link |
| `MonocleManApp` | scroll progress | `monocle:progress:scroll` | width updates on scroll |
| `HeroSection` | section | `monocle:hero:section` | visible in first viewport |
| `HeroSection` | eyebrow | `monocle:hero:eyebrow` | visible |
| `HeroSection` | heading | `monocle:hero:heading` | contains `The Monocle Man` |
| `HeroSection` | quote | `monocle:hero:quote` | contains `monocle` |
| `HeroSection` | image frame | `monocle:hero:image-frame` | no missing fallback |
| `HeroSection` | hero image | `monocle:hero:image` | complete, visible, naturalWidth >= 100, naturalHeight >= 75 |
| `FilmSection` | section | `monocle:film:section` | visible after nav |
| `FilmSection` | embed frame | `monocle:film:embed-frame` | aspect ratio preserved |
| `FilmSection` | note | `monocle:film:note` | visible prose |
| `FilmSection` | metadata | `monocle:film:metadata` | visible source metadata |
| `RulesSection` | section | `monocle:rules:section` | visible |
| `RulesSection` | heading | `monocle:rules:heading` | visible |
| `RulesSection` | rule one | `monocle:rules:item:one-side` | visible |
| `RulesSection` | rule two | `monocle:rules:item:never-waver` | visible |
| `RulesSection` | rule three | `monocle:rules:item:etiquette` | visible |
| `QuoteGallery` | gallery | `monocle:quotes:gallery` | visible after scroll |
| `QuoteGallery` | card one | `monocle:quotes:card:inspection` | visible |
| `QuoteGallery` | image one | `monocle:quotes:image:inspection` | complete and visible |
| `QuoteGallery` | card two | `monocle:quotes:card:adjustment` | visible |
| `QuoteGallery` | image two | `monocle:quotes:image:adjustment` | complete and visible |
| `QuoteGallery` | card three | `monocle:quotes:card:final-warning` | visible |
| `QuoteGallery` | image three | `monocle:quotes:image:final-warning` | complete and visible |
| `VerdictSection` | section | `monocle:verdict:section` | visible |
| `VerdictSection` | background image | `monocle:verdict:image:background` | complete and visible |
| `VerdictSection` | quote | `monocle:verdict:quote` | contains final consistency joke |
| `VerdictSection` | heading | `monocle:verdict:heading` | visible |
| `VideoModal` | dialog | `monocle:modal:video` | opens and closes by action, button, and Escape |
| `VideoModal` | iframe | `monocle:modal:iframe` | `src` includes `youtube-nocookie` only when open |
| `Footer` | credit | `monocle:footer:credit` | mentions editorial tribute |
| `Footer` | evidence note | `monocle:evidence:slice-note` | benchmark mode only |

## Required interactive elements and actions

Every row in this table must have `data-qid`, `data-qs-action`, `title`, and a top-level `useRegisterAction` registration in the owning component.

| Component | Element | `data-qid` | `data-qs-action` | `title` |
|---|---|---|---|---|
| `SkipLink` | skip to main | `monocle:skip:main` | `MONOCLE_SKIP_MAIN` | `Skip to main content` |
| `HeaderNav` | brand top link | `monocle:nav:brand-top` | `MONOCLE_NAV_TOP` | `Return to top` |
| `HeaderNav` | film link | `monocle:nav:film` | `MONOCLE_NAV_FILM` | `Jump to the film section` |
| `HeaderNav` | rules link | `monocle:nav:rules` | `MONOCLE_NAV_RULES` | `Jump to monocle rules` |
| `HeaderNav` | lines link | `monocle:nav:lines` | `MONOCLE_NAV_LINES` | `Jump to quoted lines` |
| `HeaderNav` | mobile menu button | `monocle:nav:menu-toggle` | `MONOCLE_MENU_TOGGLE` | `Open navigation menu` |
| `HeaderNav` | header watch button | `monocle:nav:watch-film` | `MONOCLE_VIDEO_OPEN_HEADER` | `Open the film modal` |
| `HeroSection` | hero watch button | `monocle:hero:watch-film` | `MONOCLE_VIDEO_OPEN_HERO` | `Watch the original monocle film` |
| `FilmSection` | original film link | `monocle:film:external-original` | `MONOCLE_ORIGINAL_OPEN_FILM` | `Open the original film on YouTube` |
| `VerdictSection` | final film link | `monocle:verdict:watch-original` | `MONOCLE_ORIGINAL_OPEN_FINAL` | `Watch the original film` |
| `VideoModal` | close button | `monocle:modal:close` | `MONOCLE_VIDEO_CLOSE` | `Close film modal` |
| `Footer` | top link | `monocle:footer:top` | `MONOCLE_FOOTER_TOP` | `Return to top` |
| `Footer` | film link | `monocle:footer:film` | `MONOCLE_FOOTER_FILM` | `Jump to film section` |
| `Footer` | lines link | `monocle:footer:lines` | `MONOCLE_FOOTER_LINES` | `Jump to quoted lines` |

## Required action registry

The implementation must expose the following actions through the action registry used by `useRegisterAction`:

```ts
const MONOCLE_ACTIONS = [
  "MONOCLE_SKIP_MAIN",
  "MONOCLE_NAV_TOP",
  "MONOCLE_NAV_FILM",
  "MONOCLE_NAV_RULES",
  "MONOCLE_NAV_LINES",
  "MONOCLE_MENU_TOGGLE",
  "MONOCLE_VIDEO_OPEN_HEADER",
  "MONOCLE_VIDEO_OPEN_HERO",
  "MONOCLE_VIDEO_CLOSE",
  "MONOCLE_ORIGINAL_OPEN_FILM",
  "MONOCLE_ORIGINAL_OPEN_FINAL",
  "MONOCLE_FOOTER_TOP",
  "MONOCLE_FOOTER_FILM",
  "MONOCLE_FOOTER_LINES"
] as const;
```

## Deterministic CI checks

The GitHub Actions benchmark must fail unless all of the following pass in the live DOM:

1. All required `data-qid` elements exist.
2. Every interactive element has `data-qid`, `data-qs-action`, `title`, and a matching registered action.
3. Hero, quote, and verdict images are complete, visible, and have natural dimensions.
4. Desktop navigation moves to Film, Rules, Lines, and Top targets.
5. Mobile menu opens, sets `aria-expanded=true`, navigates, and closes with `aria-expanded=false`.
6. Hero watch button opens the modal.
7. Header watch button opens the modal.
8. Modal iframe source includes `youtube-nocookie` only while open.
9. Escape closes the modal.
10. Close button closes the modal.
11. Focus returns to the invoking button after modal close.
12. Skip link moves focus to `monocle:main:content`.
13. Keyboard tab can reach every interactive element.
14. Focus-visible style is present on keyboard focus.
15. Reduced-motion mode disables decorative looping animations.
16. External YouTube links include the expected video id, `target="_blank"`, and `rel` containing `noopener`.
17. Axe has no critical or serious violations with color contrast enabled.
18. No unexpected console errors remain.
19. No same-origin network failures remain.
20. The artifact contains desktop, mobile, hero, modal/menu, full-page, and section screenshots.
21. The artifact contains `source/index.html`, `interactions.json`, `image-status.json`, `accessibility.json`, and `verdict.json`.
22. `verdict.json` is computed from the evidence and cannot report `PASS` when any of the above fails.

## Implementation order

1. Create React scaffold only if the benchmark branch does not already have one.
2. Implement components and data contract before visual refinements.
3. Add `useRegisterAction` shim or real hook before adding interactions.
4. Port the existing editorial design into React components.
5. Update Playwright to assert this contract from the live DOM, not source grep.
6. Capture screenshots and rendered source from the same built artifact.
7. Record the iteration in `chatgpt-lab` only after CI evidence exists.
8. Stop after one merge or one blocker.

## Non-goals

- Do not add chat, login, database, personalization, or agent UI.
- Do not broaden into the full PhatGPT controller.
- Do not claim a live website without Netlify deployment metadata.
- Do not accept screenshot presence as visual proof.
- Do not start another coding round without this contract or a stricter replacement.
