# Skill: ui-ux

> Comprehensive UI/UX principles for web, mobile, and PWA development.
> Hard mechanical gates enforce critical rules in gatekeeper.py for frontend files.
> Activate when working on: UI components, CSS, HTML, React/Vue/Svelte, mobile interfaces, PWA features, design systems, accessibility.

---

## Mechanical Gates (Enforced by gatekeeper.py)

When writing frontend files (`.html`, `.css`, `.scss`, `.js`, `.jsx`, `.ts`, `.tsx`, `.vue`, `.svelte`, `.tpl`, `.blade.php`), the gatekeeper enforces:

### BLOCKED (Exit 2)
| Violation | Pattern | Principle |
|---|---|---|
| `<img>` without `alt` | `<img[^>]*>(?!.*alt=)` | Accessibility — Perceivability |
| Positive `tabindex` | `tabindex="[1-9]"` | Accessibility — Operability |
| `user-scalable=no` | `user-scalable\s*=\s*no` | Mobile — Accessibility |
| `maximum-scale=1.0` | `maximum-scale\s*=\s*1` | Mobile — Accessibility |
| Missing `type` on `<input>` | `<input(?!.*type=)` | Mobile — Form Design |

### WARNED (Stderr)
| Violation | Pattern | Principle |
|---|---|---|
| `outline: none` without focus replacement | `outline:\s*none` | Accessibility — Operability |
| Missing `lang` on `<html>` | `<html(?!.*lang=)` | Accessibility — Understandability |
| Missing viewport meta | No `<meta name="viewport"` | Mobile — Viewport |
| Click handler on non-interactive element | `onClick.*div\|span` | Interaction — Affordance |
| Autoplay video without muted | `<video.*autoplay(?!.*muted)` | Accessibility — Cognitive |
| `font-size` below 12px | `font-size:\s*\d+px` where < 12 | Visual Design — Typography |
| Touch target below 44px | `width\|height.*\d+px` where < 44 | Mobile — Touch Targets |

---

## Quick Reference: The 4 Principles Applied to UI/UX

| Principle | UI/UX Rule |
|---|---|
| **Think Before Coding** | Define the user journey, information architecture, and interaction model before writing markup. Sketch the flow. |
| **Simplicity First** | One primary action per screen. Remove elements that don't serve the user's current goal. |
| **Surgical Changes** | Touch only the component/file related to the UX issue. Don't refactor unrelated design system tokens. |
| **Goal-Driven Execution** | Define success criteria: "User can complete checkout in <3 clicks" not "Add checkout page." |

---

## Domain 1: Cognitive Psychology Laws

### 1.1 Fitts's Law
> Larger, closer targets are faster to hit.

- Minimum touch target: **44×44 px** (Apple HIG), ideally **48×48 dp** (Material)
- Primary CTAs in thumb-friendly zones (bottom-center mobile)
- Infinite edges: elements flush with screen edges are infinitely large in one direction

### 1.2 Hick's Law
> Decision time grows with the number of choices.

- Cap top-level navigation at **≤7 items** (ideally 5)
- Progressive disclosure for advanced options
- Pre-select recommended defaults

### 1.3 Miller's Law
> Working memory holds 7±2 items.

- Chunk information into labeled groups
- Multi-step forms for >7 fields
- Auto-format numbers: `4532 1234 5678 9010`

### 1.4 Jakob's Law
> Users expect your site to work like others they've used.

- Logo top-left → homepage
- Cart top-right
- Hamburger = mobile menu
- Only deviate with measured evidence

### 1.5 Goal-Gradient Effect
> Motivation increases near goal completion.

- Progress bars: `Step 2 of 4`
- "Almost there!" microcopy at penultimate steps
- Partially filled completion meters

### 1.6 Peak-End Rule
> Experience is judged by peak intensity and ending.

- Delightful endings: animated success screens
- Address peak stress points with reassurance
- Error recovery should feel positive

### 1.7 Serial Position Effect
> Best recall of first and last items.

- Most important nav items first and last
- Best pricing plan first or last, never middle
- Strongest differentiator first in feature lists

### 1.8 Von Restorff Effect
> The visually different item is noticed first.

- Primary CTA must be most visually distinct
- One accent color for interactive elements
- Recommended plan highlighted with badge/border

### 1.9 Zeigarnik Effect
> Incomplete tasks are recalled more readily.

- "Continue where you left off" cards
- Auto-save drafts
- Progress indicators showing done + remaining

### 1.10 Doherty Threshold
> Productivity spikes when response < 400ms.

- Target <100ms for UI interactions
- Target <1000ms for data loading (skeleton loaders)
- Optimistic UI updates before server confirmation

### 1.11 Tesler's Law
> Complexity is conserved — absorb it into the system, not the user.

- Auto-format inputs (dates, credit cards, phones)
- Accept multiple formats, normalize server-side
- Smart defaults; expose advanced settings only to power users

### 1.12 Aesthetic-Usability Effect
> Aesthetic designs are perceived as more usable.

- Visual polish directly affects trust
- Consistent spacing, typography, color = competence signals
- Beautiful design buys tolerance for minor friction

---

## Domain 2: Gestalt & Visual Perception

- **Proximity**: Near elements = related. Labels directly above inputs.
- **Similarity**: Same style = same group. One icon set, consistent links.
- **Common Region**: Enclosed elements = group. Cards, borders, background fills.
- **Prägnanz**: Mind simplifies complex input. Simple icons, unambiguous states.
- **Uniform Connectedness**: Lines/color connect elements. Breadcrumbs, step indicators.
- **Figure-Ground**: Separate foreground from background. Modal overlays, sufficient contrast.
- **Continuity**: Eye follows smooth paths. Peek effects in carousels, aligned grids.

---

## Domain 3: Interaction Design Principles

- **Direct Manipulation**: Drag shows item moving, pinch zooms in real time
- **Affordance**: Buttons look clickable, inputs have borders, drag handles show grips
- **Feedback**: Every action produces visible response. Buttons change on hover/press.
- **Constraint**: Disable submit until valid, prevent invalid dates, use input masks
- **Mapping**: Volume left = quieter, scroll down = content up, brightness right = lighter
- **Consistency**: Same component = same style. Same action = same name.
- **Error Prevention > Recovery**: Real-time validation, confirm destructive actions
- **Reversibility**: Undo for 5–10 seconds, auto-save drafts, soft delete before permanent

---

## Domain 4: Information Architecture & Navigation

- **3-Click Rule (Revised)**: ≤3 interactions to key content; clarity > click count
- **Information Scent**: Labels describe content, not internal taxonomy
- **Progressive Disclosure**: Show only what's needed; reveal more on request
- **Wayfinding**: Breadcrumbs, active states, page titles, working back button
- **Search**: Partial matches, synonyms, typos, recent searches, faceted filters

---

## Domain 5: Visual Design Systems

### 5.1 Visual Hierarchy
- One H1 per page maximum
- Primary CTA > Secondary > Tertiary in visual weight
- Dominant / Subordinate / Accent: one dominant element per screen

### 5.2 Typography
- Minimum body: **16px** web, **14px** secondary
- Line length: **60–80 characters**
- Line height: **1.4–1.6×** for body
- Max **2 typefaces**
- System fonts preferred (Inter, SF Pro, Roboto)

### 5.3 Color
- Contrast: **4.5:1** text (AA), **3:1** UI components, **7:1** for AAA
- **60-30-10 rule**: 60% neutral, 30% secondary, 10% accent
- Never color as **only** signal — pair with icon/shape/text
- Dark mode: **#121212** background, not pure black; desaturate colors

### 5.4 Spacing & Layout
- **4px or 8px base grid**
- Breakpoints: 320px, 768px, 1024px, 1440px
- Max-width: 1200–1440px
- CSS Grid for pages; Flexbox for components

### 5.5 Iconography
- Pair icons with text labels for non-universal icons
- Single icon set throughout
- Minimum: **24×24px** interactive, **16×16px** decorative
- SVG preferred

### 5.6 Design Tokens
- Three levels: Global → Semantic → Component
- Semantic names: `--color-action` not `--color-blue`
- Enables theming (light/dark, brand variants)

---

## Domain 6: Motion & Animation

- **Purpose**: Every animation serves communication — state transitions, loading, focus
- **Duration**: Micro 100–200ms, transitions 200–400ms, sequences 400–700ms
- **Easing**: Never linear. `cubic-bezier(0.4, 0, 0.2, 1)` for standard motion
- **Reduced Motion**: Respect `@media (prefers-reduced-motion: reduce)`
- **Loading**: Skeleton screens > spinners. Optimistic UI > waiting.

---

## Domain 7: Accessibility (A11Y)

WCAG 2.2 AA is the minimum.

- **Perceivability**: All images have `alt` text. Captions on videos. Text resizable to 200%.
- **Operability**: All elements reachable by Tab. Focus indicators visible (3:1 contrast). Touch targets ≥44×44px. No keyboard traps.
- **Understandability**: Plain language (Grade 8). Error messages identify what, where, and how to fix. Consistent navigation.
- **Robustness**: Semantic HTML first (`<button>`, `<nav>`, `<main>`). Valid ARIA. `aria-live` for dynamic updates.
- **Cognitive**: Avoid jargon, auto-advancing carousels, and double negatives. Allow turning off animations/sounds.

---

## Domain 8: Mobile & PWA

- **Mobile-First**: Start at 320px. `min-width` media queries.
- **Thumb Zones**: Primary actions in bottom ~40% of screen.
- **PWA**: Valid `manifest.json`, Service Worker caching, installable, offline functionality.
- **Touch Gestures**: Follow platform conventions. Provide non-gesture alternatives.
- **Mobile Forms**: Correct `input type`, `autocomplete`, `enterkeyhint`, single-column, labels above inputs.
- **Safe Areas**: `env(safe-area-inset-*)` for notch, home indicator.
- **Offline**: Queue actions, show offline indicator, never blank screens.

---

## Domain 9: Performance as UX

| Metric | Good | Poor |
|---|---|---|
| **LCP** | ≤2.5s | >4s |
| **INP** | ≤200ms | >500ms |
| **CLS** | ≤0.1 | >0.25 |

- Preload hero images, `fetchpriority="high"`
- Skeleton screens for all async content
- Lazy load below-fold images
- JS budget: ≤300kb compressed initial load

---

## Domain 10: Modern UX Patterns

- **Dark Mode**: Separate palette, not inverted. #121212 background.
- **AI Interfaces**: Show generation states, provide sources, allow undo/regenerate.
- **Microinteractions**: Trigger → Rules → Feedback → Loops. Under 300ms.
- **Empty States**: Illustration + headline + description + CTA. Never blank.
- **Notifications**: High bar for interruption. Queue toasts. Contextual permission requests.
- **Loading Hierarchy**: Instant (<100ms) → Skeleton (100ms–1s) → Progress bar (1–10s) → Detailed progress (>10s)
- **Data Viz**: Right chart type, remove chart junk, annotate key points, colorblind-safe.
- **Trust Signals**: Specific numbers, real names/photos, security badges near decision points.
- **Onboarding**: Shortest path to activation event. Teach by doing. Allow skip.
- **Ethical Design**: No dark patterns. Cancellation = sign-up ease. Privacy-first defaults.

---

## Domain 11: Nielsen's 10 Heuristics (Modern)

1. **Visibility of System Status** — skeletons, optimistic UI, streaming states
2. **Match Real World** — "Unsubscribe" not "Modify communication preferences"
3. **User Control & Freedom** — undo, ESC closes modals, back button works
4. **Consistency & Standards** — platform conventions, internal consistency
5. **Error Prevention** — real-time validation, disabled invalid states
6. **Recognition Over Recall** — autocomplete, command palettes, visible shortcuts
7. **Flexibility & Efficiency** — keyboard shortcuts, power user modes, bulk ops
8. **Aesthetic & Minimalist** — progressive disclosure, focused task screens
9. **Error Recovery** — specific, actionable error messages with next steps
10. **Help & Documentation** — in-context tooltips, searchable help, empty state guidance

---

## Domain 12: Research & Testing

- **5-User Rule**: 5 participants reveal ~85% of usability problems per iteration
- **Key Metrics**: Task completion rate, time on task, error rate, SUS (≥68 = above avg), NPS, rage clicks, dead clicks
- **A/B Testing**: One variable at a time. Define success metric before running. Don't end early.
- **Accessibility Testing**: axe DevTools (automated), keyboard-only navigation, screen reader testing (NVDA/VoiceOver/TalkBack)

---

## Domain 13: Design Systems

- **Components**: Tokens → Components → Patterns → Guidelines
- **Component API**: Variants first, sensible defaults, composition over configuration
- **States to Design**: Default, Hover, Focus, Active, Loading, Disabled, Error, Success, Empty
- **Visual Regression Tests**: For every component state

---

## Master Audit Checklist

**Cognitive Load**
- [ ] Visible choices per screen ≤7
- [ ] Progressive disclosure for advanced content
- [ ] Complex tasks in sequential steps
- [ ] Smart defaults minimize decisions

**Visual Design**
- [ ] One primary CTA per screen, visually most distinct
- [ ] 4px/8px grid spacing
- [ ] Typographic hierarchy clear without color
- [ ] Consistent iconography style

**Accessibility**
- [ ] All text ≥4.5:1 contrast (AA)
- [ ] All UI components ≥3:1 contrast
- [ ] Keyboard navigation logical and complete
- [ ] Focus indicators visible and ≥3:1 contrast
- [ ] All images have meaningful alt text
- [ ] ARIA used correctly
- [ ] `prefers-reduced-motion` respected

**Mobile / PWA**
- [ ] Touch targets ≥44×44px
- [ ] Primary actions in bottom thumb zone
- [ ] Safe area insets respected
- [ ] Correct keyboard types for inputs
- [ ] Offline with Service Worker
- [ ] Valid manifest.json

**Performance**
- [ ] LCP ≤2.5s
- [ ] INP ≤200ms
- [ ] CLS ≤0.1
- [ ] Skeleton loaders for async content
- [ ] Lazy loading below-fold

**Interaction**
- [ ] Every action has visible feedback ≤400ms
- [ ] Destructive actions require confirmation
- [ ] All actions undoable or confirmable
- [ ] Error messages: problem, cause, fix

**Ethical Design**
- [ ] No dark patterns
- [ ] Privacy-first defaults
- [ ] Cancellation as easy as sign-up
- [ ] Contextual permission requests

---

## AI-Agent Audit Prompt

```
You are an expert UI/UX auditor. Evaluate every design against:

COGNITIVE: Fitts's, Hick's, Miller's, Jakob's, Goal-Gradient, Peak-End, Serial Position, Von Restorff, Zeigarnik, Doherty, Tesler, Aesthetic-Usability.
GESTALT: Proximity, Similarity, Common Region, Prägnanz, Connectedness, Figure-Ground, Continuity.
INTERACTION: Direct Manipulation, Affordance, Feedback, Constraint, Mapping, Consistency, Error Prevention, Reversibility.
IA: 3-Click Rule, Information Scent, Progressive Disclosure, Wayfinding, Search.
A11Y: WCAG 2.2 AA (Perceivable, Operable, Understandable, Robust, Cognitive).
MOBILE: Thumb Zones, Touch Targets, Safe Areas, Gestures, Offline, PWA.
PERFORMANCE: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1.
NIELSEN: All 10 heuristics.
ETHICS: No dark patterns, privacy-first, honest communication.

For each violation:
1. Name the principle
2. Describe the violation
3. Explain user impact
4. Provide concrete redesign recommendation
5. Rate: Critical / High / Medium / Low

Format: [SEVERITY] [PRINCIPLE] — [VIOLATION] — [IMPACT] — [RECOMMENDATION]
```
