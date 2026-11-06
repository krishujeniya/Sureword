# Sureword design system

## Direction and evidence

Hybrid product introduction and working web app. Light theme, particle-led hero: existing blue/navy brand, white canvas, quiet gray surfaces, original voice orbit illustration. The main action opens the real workspace on the same document. No framework migration or new runtime dependency.

Browser references inspected 2026-11-06 at 1440×1000; captures in `artifacts/design-qa/reference-*.png`. [Antigravity](https://antigravity.google/): Observed compact navigation, white canvas, black pill, announcement strip, typing hero. [Flow](https://flow.google.com/about): Observed black canvas, oversized white title, white pill CTA, pause control. Inferred: duplicated Antigravity text supports animation layers; implementation not inspected. Recommended: Sureword uses blue particles and a three-stage explanation, not Google branding or footage. Exact reference timings and performance remain unverified. Official Canvas and IntersectionObserver API documentation checked on MDN; no animation libraries added.

## Contract

Reader: frontline workflow researcher or reviewer. Primary action: start a fictional visit. Hierarchy: value proposition → real workspace → workflow explanation → limitations. Target widths: 320, 360, 390, 768, 1024, 1280, 1440, 1920px. Required states: loading status; empty transcript/registry; partial recognized fields and targeted question; saved confirmation and exports; provider/network error; microphone permission denied. No invented pricing, product UI, or clinical performance claims.

## Tokens and tuned values

`static/design.css` is the canonical new theme/motion token layer over existing workflow styles. White #fff, navy #102c43, accent #0369a1, muted #536471; large stage text #64869c was darkened after Lighthouse contrast feedback. Existing shield logo retained. System sans and mono avoid font licensing and network costs. Hero 48–86px; compact English body 16–17px. Content max 1360px, gutters 48/28/20px; radii 8/16/24/pill; no new decorative shadows. Header 80px desktop/68px mobile. Mobile navigation keeps the primary action visible; secondary destinations remain available in content. No dropdown is needed for two section links.

Motion: 150/250/450/700ms, primary/reveal easings. Particle counts 80 desktop/36 mobile, DPR capped at 2, cached sprites, delta time capped at two normalized frames, negative gravity -.065, repulsion radius 100px, spring .006 and friction .95 (tuned down from supplied starting spring .06 for calmer movement). Wrap boundaries; pointer influence excludes touch. Pause offscreen/hidden tab and respect Save-Data. Reduced motion is read before scheduling and responds live; static field and instant panels/reveals, native instant anchors. Canvas fallback is the independent SVG orbit. No canvas blocks input.

## Styles and states (section 18.2–18.4)

Built: canvas/raised/alternate surfaces; hairline dividers; rounded media-like illustration and app panels; filled/outlined/text/segmented buttons; default/hover/focus/pressed/selected states; native select, readonly fields, status chips; scoped table horizontal scroll; error/status/empty styles; visible focus; text selection; themed scrollbar; favicon/theme-color; sticky header blur with solid fallback; print CSS. Native audio controls are exposed on explicit playback, including pause. No automatic speech request. Optional missing fields remain visible. Language selection applies only to workspace; overview remains English.

Skipped styles: dark surfaces/glows, overlay shadows, media scrims, edge masks/rails, video frames, syntax highlighting, plan comparisons, tooltips, skeleton shimmer, custom cursor, and a theme switch: no matching product content or workflow. Existing app emoji icons are retained as legacy UI; a complete SVG icon migration is skipped to avoid unrelated localization changes. FAQ indicator uses an SVG mask. Existing logo SVG has legacy gradients/shadows; retained to preserve identity. No press kit or logo-copy control because this is an app prototype with an existing image-based mark, not a press site.

State applicability: links have default/hover/focus/current destination; disabled/loading/error/success are not link actions. Stage tabs have default/hover/focus/selected, no network/loading/disabled state. Recording/save/sample controls use actual async statuses and disabled save until review-ready; success and failure messages are server driven. Sample-answer is available only for preset provenance and submits to the existing clarification endpoint. Native FAQ has closed/open/focus states; no asynchronous states. Particle controls have pressed/focus and reduced-motion disabled state. Registry has empty/populated/export states. No carousel, explorer, search, or video state matrix is applicable. Browser coverage and unrun states are recorded in QA_REPORT.md; no claim of full assistive technology conformance.

## Effects coverage (section 18.5)

Each row accounts for the requested effect; built rows describe the actual implementation even where simplified. O/I/D labels describe the supplied reference evidence; R describes recommended implementation. Browser QA exercised stages, particles, hover/focus/press, hash anchors, disclosures, actual request statuses, and reduced-motion mode. Live provider/audio states are unrun.

| ID | Effect | Trigger | Properties | Duration | Easing | Reduced motion | Status | Evidence | Where |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | Headline entrance | first view | opacity, translateY 24px | 700ms | reveal | instant; full content visible | built | O | hero heading; whole block reveal |
| L2 | Subcopy and CTA follow-up | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| L3 | Hero media diffusion | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| L4 | Particle fade-in | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| L5 | Announcement entrance | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| L6 | Header reveal | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| L7 | Scroll cue loop | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| A1 | Particle drift | visible hero | position, rotation | continuous | delta-time physics | static arrangement | built | O | hero canvas |
| A2 | Particle turbulence and rotation | visible hero | velocity, rotation | continuous | sin turbulence + damping | static arrangement | built | O | hero canvas |
| A3 | Orbital formation flow | mode control | spring target | continuous | spring .006; damping .95 | static arrangement | built | O | hero canvas |
| A4 | Halos arcs and waves | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| A5 | Floating chips | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| A6 | Dark atmosphere breathing | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| A7 | Ambient video loop | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| A8 | Content-derived color | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P1 | Particle pointer repulsion | fine pointer | repulsion, settle | continuous | damping .95 | disabled movement; retain feedback | built | O | hero canvas |
| P2 | Custom cursor | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P3 | Magnetic button | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P4 | Magnetic border | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P5 | Button hover lift | hover | translateY -2px, fill | 150ms | primary | disabled movement; retain feedback | built | I | buttons |
| P6 | Button press | press | scale .98 | 150ms | primary | disabled movement; retain feedback | built | R | buttons |
| P7 | Link underline | hover/focus | underline appears | instant | none | disabled movement; retain feedback | built | R | quiet links; no animated underline |
| P8 | Nav hover | hover/focus | underline | instant | none | disabled movement; retain feedback | built | I | header section links |
| P9 | Dropdown chevron | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P10 | Card emphasis | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P11 | Directory highlight | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P12 | Focus ring | focus-visible | 2px outline | instant | none | disabled movement; retain feedback | built | R | all controls |
| P13 | Variable font weight | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| P14 | Video thumbnail preview | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| S1 | Fade and rise once | first intersection | opacity, rise 24px | 700ms | reveal | instant; full content visible | built | R | headings; same shared reveal as L1 |
| S2 | Group stagger | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S3 | Heading line mask | — | — | — | — | static/native | skipped: one whole-heading reveal chosen; avoid duplicate text animation | R | — |
| S4 | Media entrance | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S5 | Media parallax | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S6 | Layered parallax | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S7 | Scroll scrub | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S8 | Traveling sine row | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S9 | Pinned stages | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S10 | Progress bar | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S11 | Active nav indicator | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S12 | Header surface | scroll >8px | divider color | instant | none | instant; full content visible | built | R | sticky header |
| S13 | Scroll cue fade | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S14 | Smooth scroll engine | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| S15 | Anchor scroll | hash navigation | native scroll | browser-defined | native | instant; full content visible | built | R | all section links; 100px offset |
| S16 | Docs TOC | — | — | — | — | static/native | skipped: API docs retained; not a public content docs portal | R | — |
| C1 | Carousel travel | — | — | — | — | static/native | skipped: one product; no carousel needed | R | — |
| C2 | Active card | — | — | — | — | static/native | skipped: one product; no carousel needed | R | — |
| C3 | Peeking neighbors | — | — | — | — | static/native | skipped: one product; no carousel needed | R | — |
| C4 | Carousel arrows | — | — | — | — | static/native | skipped: one product; no carousel needed | R | — |
| C5 | Pagination | — | — | — | — | static/native | skipped: one product; no carousel needed | R | — |
| C6 | Auto-rotate | — | — | — | — | static/native | skipped: one product; no carousel needed | R | — |
| C7 | Stage indicator slide | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| C8 | Stage panel transition | select stage | opacity, rise 16px | 450ms | reveal | instant; full content visible | built | O | stage panels; fixed reading height, split layout |
| C9 | Stage word transition | select stage | opacity with parent | 450ms | reveal | instant; full content visible | built | O | oversized stage word |
| C10 | Use-case switcher | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| C11 | Showcase selector | — | — | — | — | static/native | skipped: no multi-product explorer, stories, or paid plans | R | — |
| C12 | Pricing entrance | — | — | — | — | static/native | skipped: no multi-product explorer, stories, or paid plans | R | — |
| C13 | Accordion open close | summary activation | native disclosure, icon rotate | instant | native | instant; full content visible | built | O | FAQ; native details open state |
| C14 | Code tabs | — | — | — | — | static/native | skipped: API docs retained; not a public content docs portal | R | — |
| O1 | Mobile menu | — | — | — | — | static/native | skipped: compact navigation/native select fits; no menu overlay needed | R | — |
| O2 | Search dialog | — | — | — | — | static/native | skipped: API docs retained; not a public content docs portal | R | — |
| O3 | Video modal | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| O4 | Dropdown panel | — | — | — | — | static/native | skipped: compact navigation/native select fits; no menu overlay needed | R | — |
| O5 | Toast copied feedback | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| O6 | Tooltip | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| M1 | Poster-video fade | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| M2 | Controls auto-hide | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| M3 | Play hover | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| M4 | Lazy video and pause | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| M5 | Image blur-up | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| M6 | Image reserved ratio | — | — | — | — | static/native | skipped: no current product video/media workflow | R | — |
| T1 | Character stagger | — | — | — | — | static/native | skipped: one whole-heading reveal chosen; avoid duplicate text animation | R | — |
| T2 | Whole-line reveal | — | — | — | — | static/native | skipped: one whole-heading reveal chosen; avoid duplicate text animation | R | — |
| T3 | Typewriter | — | — | — | — | static/native | skipped: one whole-heading reveal chosen; avoid duplicate text animation | R | — |
| T4 | Count-up | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| T5 | Staged async status | async request | status text | instant | none | instant; full content visible | built | O | workspace status region |
| R1 | View transition | — | — | — | — | static/native | skipped: single-document app; native route navigation retained | R | — |
| R2 | Shared element | — | — | — | — | static/native | skipped: single-document app; native route navigation retained | R | — |
| R3 | Persistent header | same-page workflow switch | header retained | n/a | none | instant; full content visible | built | R | single document header |
| R4 | Subchapter preview | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R5 | Explorer reflow | — | — | — | — | static/native | skipped: no multi-product explorer, stories, or paid plans | R | — |
| R6 | Explorer empty | — | — | — | — | static/native | skipped: no multi-product explorer, stories, or paid plans | R | — |
| R7 | Skeleton | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R8 | Loading spinner | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R9 | Success stroke | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R10 | Form error | request/permission failure | message, error surface | instant | none | instant; full content visible | built | R | workspace alert/status |
| R11 | Switch toggle | mode/pause switch | aria-pressed, label, color | 150ms | primary | instant; full content visible | built | R | particle controls |
| R12 | Particle mode indicator blend | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R13 | Theme switch | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R14 | Guided demo controls | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R15 | SVG stroke | — | — | — | — | static/native | skipped: optional decoration omitted to protect reading and app performance | R | — |
| R16 | Logo copy | — | — | — | — | static/native | skipped: existing logo is image SVG; no press workflow | R | — |
| R17 | Language download expansion | — | — | — | — | static/native | skipped: native 11-language select retained; no download expansion | R | — |

**Coverage: 20 built, 73 skipped, 93 total effects.** Skipped does not mean missing working app behavior.
