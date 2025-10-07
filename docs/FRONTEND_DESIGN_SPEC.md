# Ratatouille Frontend Design Specification

**Design Philosophy:** Chef's Sketchbook - Hand-drawn, Playful, Professional
**Adapted From:** the-bugle mobile app design system
**Platform:** Mobile-first (matching the-bugle's mobile-only approach)

---

## Design System Overview

### Brand Personality
- **Friendly Cooking Companion** - Approachable, encouraging, hand-drawn aesthetic
- **Playful but Professional** - Fun illustrations, serious about teaching techniques
- **Sketchbook Feel** - Like flipping through a chef's personal recipe notebook

### Color Palette

**Primary Colors:**
- **Black:** `#000000` - Primary text, borders, chef's ink
- **White:** `#FFFFFF` - Background, card surfaces
- **Navy Blue:** `#1E3A5F` - Chef's apron blue (accent color)

**No gradients** - Clean, flat colors only

### Typography

**Font Family:** Plus Jakarta Sans
- Consistent with the-bugle
- Clean, modern, readable
- Works well at small mobile sizes

**Font Hierarchy:**
```css
/* Page Titles */
font-size: 28px
font-weight: 700
letter-spacing: -0.02em

/* Section Headers */
font-size: 20px
font-weight: 600

/* Body Text */
font-size: 16px
font-weight: 400
line-height: 1.5

/* Small Text / Metadata */
font-size: 14px
font-weight: 500
color: #666666
```

---

## Asset Library (Borrowed from the-bugle)

### Border Assets
Located: `/public/border-assets/`

Use these hand-drawn line elements to frame content:
- `Line-top.svg` - Top borders for cards
- `Line-bottom.svg` - Bottom borders
- `Line-left.svg` - Left decorative lines
- `Line-right.svg` - Right decorative lines
- `Line-*-curve.svg` - Curved corner variants

**Usage:** Apply to recipe cards, section dividers, accent lines around CTAs

### Circle Borders (for Buttons)
Located: `/public/Accent Icons/`

- `circle-border-combined.svg` - Full circle border for primary CTAs
- `circle-border-top-edge.svg` - Partial circle accents
- `circle-border-bottom-edge.svg`
- `circle-border-left-edge.svg`
- `circle-border-right-edge.svg`

**Usage:** Wrap "Find Recipes" button, difficulty badges, technique tags

### Additional Decorative Elements
- `Background Scribble.svg` - Subtle background texture
- `Blob Collage.svg` - Organic shapes for empty states
- Custom icons with hand-drawn aesthetic

---

## Page Structure

### Mobile Layout (Single Column)

```
┌─────────────────────────────────────┐
│ 🐀 Ratatouille                      │  ← Logo + Wordmark
│ Your AI Culinary Coach              │  ← Tagline (14px, gray)
│                                     │
│ [decorative line border]            │
│                                     │
│ What do you want to learn?          │  ← Input Section
│ [hand-drawn border around input]    │
│ ┌─────────────────────────────────┐│
│ │ e.g., "pan sauces"              ││
│ └─────────────────────────────────┘│
│                                     │
│ Your skill level:                   │
│ ○ Beginner  ○ Intermediate ○ Adv...│  ← Radio buttons with
│                                     │    circle-border accents
│                                     │
│ Dietary restrictions: (optional)    │
│ □ Vegetarian  □ Vegan               │
│ □ Gluten-free □ Kosher              │
│                                     │
│ [decorative scribble line]          │
│                                     │
│     ┌───────────────────┐          │  ← Primary CTA
│     │  Find Recipes →   │          │    with circle-border.svg
│     └───────────────────┘          │    Black bg, white text
│                                     │
└─────────────────────────────────────┘
```

**Height:** Fits in viewport without scrolling (mobile-optimized)
**Spacing:** Generous whitespace (pt-8, pb-12, px-6)
**Borders:** Hand-drawn SVG lines from the-bugle

---

## Recipe Card Carousel

### Carousel Design (Post-Submit)

**Modern Swipeable Carousel:**
- Smooth horizontal scrolling
- Snap-to-center behavior
- Progress dots below cards
- Gesture-friendly swipe zones

**Card Dimensions:**
- Width: 85vw (allows peek of next card)
- Height: Auto (min 500px)
- Gap: 16px between cards
- Border-radius: 12px with hand-drawn line accents

### Individual Recipe Card Layout

```
┌─────────────────────────────────────┐
│ [top decorative line]               │
│                                     │
│ 🍳 Pan-Seared Chicken               │  ← Title (20px, bold)
│    with Lemon Butter                │
│                                     │
│ Difficulty: ★★☆☆☆ Intermediate     │  ← Difficulty badge
│ Time: 45 min  |  Serious Eats      │  ← Metadata
│                                     │
│ ─────────────────────────────────   │  ← Divider line
│                                     │
│ 🎯 Why This Recipe:                 │
│ Perfect for mastering pan sauce     │
│ fundamentals. Teaches deglazing,    │  ← Reasoning (16px)
│ emulsification, and heat control... │
│                                     │
│ 🔥 Techniques You'll Learn:         │
│ ┌─ Pan deglazing with wine         │
│ ├─ Butter emulsion (mounting)      │  ← Technique list
│ └─ Temperature control for searing  │    with custom bullets
│                                     │
│ 🥗 Nutrition (per serving):         │
│ 450 cal | 25g protein | 18g fat    │  ← Nutrition summary
│                                     │
│ ─────────────────────────────────   │
│                                     │
│     [ View Full Recipe → ]          │  ← Secondary CTA
│                                     │
│ [bottom decorative line]            │
└─────────────────────────────────────┘
```

**Card Styling:**
- Background: `#FFFFFF`
- Border: 2px solid `#000000` with hand-drawn line SVG overlay
- Box Shadow: `0 4px 12px rgba(0,0,0,0.08)` (subtle depth)
- Padding: `24px`

---

## Component Design Details

### Input Field (Learning Goal)

**Style:**
```css
border: 2px solid #000000
border-radius: 8px
padding: 16px
font-size: 16px
font-family: Plus Jakarta Sans
background: #FFFFFF

/* Hand-drawn accent line above input */
position: relative
&::before {
  content: url('/border-assets/Line-top.svg')
  position: absolute
  top: -12px
}
```

**Placeholder:** Gray (#999999), italicized
**Focus State:** Navy blue (#1E3A5F) border, no shadow

### Radio Buttons (Skill Level)

**Custom Styled:**
- Replace default radio with hand-drawn circle border
- Selected: Filled black circle inside border
- Unselected: Empty circle
- Label: 16px, aligned right of circle

**Layout:** Horizontal row on mobile (space-between)

### Checkboxes (Dietary)

**Style:**
- Hand-drawn square border (from circle-border adapted)
- Check: Bold checkmark icon
- Layout: 2-column grid on mobile

### Primary CTA Button ("Find Recipes")

**Design:**
```css
background: #000000
color: #FFFFFF
padding: 16px 32px
font-size: 18px
font-weight: 600
border-radius: 24px
position: relative

/* Wrap with circle-border-combined.svg */
&::after {
  background-image: url('/Accent Icons/circle-border-combined.svg')
  transform: scale(1.1)
}

/* Hover/Press */
&:active {
  transform: scale(0.98)
  background: #1E3A5F (navy blue)
}
```

**Loading State:**
- Replace arrow with spinning loader
- Text: "Finding recipes..."
- Disable: `opacity: 0.6, pointer-events: none`

### Secondary CTA ("View Full Recipe")

**Design:**
```css
border: 2px solid #000000
background: transparent
color: #000000
padding: 12px 24px
font-size: 16px
border-radius: 20px

/* Hand-drawn line accent */
position: relative
&::before {
  content: url('/border-assets/Line-right-curve.svg')
}
```

---

## Loading States

### While Agents Work (30-45 seconds)

**Full-Screen Overlay:**
```
┌─────────────────────────────────────┐
│                                     │
│         [animated chef hat          │
│          or cooking pot icon]       │  ← Custom loading animation
│                                     │
│      Finding your recipes...        │
│                                     │
│  [Progress indicator]               │
│  ●●●○○ Step 3 of 5                  │  ← Shows current agent
│                                     │
│  🔍 Validating techniques...        │  ← Live agent updates
│                                     │
└─────────────────────────────────────┘
```

**Agent Progress Labels:**
1. "Planning search..." (Research Planner)
2. "Hunting recipes..." (Recipe Hunter)
3. "Validating techniques..." (Technique Validator)
4. "Personalizing for you..." (Personalization)
5. "Adding nutrition..." (Nutrition Analyzer)

**Visual:** Pulsing hand-drawn circles, no spinners

---

## Empty States & Errors

### No Recipes Found

```
┌─────────────────────────────────────┐
│    [Blob Collage.svg background]   │
│                                     │
│  😕 No recipes found for            │
│  "{user's learning goal}"           │
│                                     │
│  Try:                               │
│  • Broadening your search           │
│  • Removing dietary filters         │
│  • Trying a different skill level   │
│                                     │
│     [ Try Again ]                   │
│                                     │
└─────────────────────────────────────┘
```

### Error State

**Toast Notification:**
- Top-right corner
- Red accent (#DC2626)
- Auto-dismiss after 5s
- Hand-drawn border

---

## Typography Scale (the-bugle Adapted)

```css
/* From Plus Jakarta Sans */
--font-plus-jakarta-sans: 'Plus Jakarta Sans', system-ui, sans-serif;

/* Headings */
h1: 28px / 700 / -0.02em
h2: 24px / 600 / -0.01em
h3: 20px / 600 / 0em
h4: 18px / 600 / 0em

/* Body */
body: 16px / 400 / 1.5
small: 14px / 500 / 1.4
```

---

## Spacing System (Tailwind)

Consistent with the-bugle:
- `px-6` - Page horizontal padding
- `py-8` - Section vertical padding
- `gap-4` - Between form elements
- `gap-6` - Between sections
- `mb-2` - Label to input
- `mt-8` - Between major sections

---

## Animation Principles

**Subtle, Not Flashy:**
- Page transitions: 200ms ease-out
- Button press: scale(0.98)
- Card entrance: fade-in + slide-up (300ms)
- Carousel swipe: spring physics

**No:**
- Excessive bouncing
- Rotating elements
- Flashing colors
- Auto-playing carousels

---

## Accessibility

### Touch Targets
- Minimum: 44×44px (iOS standard)
- Buttons: 48px height minimum
- Spacing between interactive elements: 8px

### Contrast
- Black on white: 21:1 (AAA)
- Navy on white: 7.4:1 (AA)
- Gray text: #666666 minimum

### Screen Reader
- Semantic HTML (`<button>`, `<input>`, `<label>`)
- ARIA labels for icons
- Focus visible states

---

## Mobile-Specific Optimizations

### Gestures
```css
/* From the-bugle globals.css */
touch-action: pan-y pinch-zoom  /* Vertical scroll only */
overscroll-behavior-x: none     /* Prevent horizontal bounce */
-webkit-tap-highlight-color: transparent  /* No blue flash */
```

### Safe Areas
```css
/* iOS notch/home indicator */
padding-top: env(safe-area-inset-top)
padding-bottom: env(safe-area-inset-bottom)
```

### Performance
- Lazy load images (Next.js Image component)
- Skeleton screens while loading
- Optimistic UI updates

---

## Component Library Mapping

### Reuse from the-bugle

| Component | Source | Adaptation |
|-----------|--------|------------|
| Button | `components/ui/button.tsx` | Add circle-border wrapper |
| Card | `components/ui/card.tsx` | Add hand-drawn line borders |
| Input | `components/ui/input.tsx` | Style with black borders |
| Badge | `components/ui/badge.tsx` | Use for difficulty/tags |
| Carousel | Custom (new) | Modern swipe with progress dots |

### New Components for Ratatouille

1. **RecipeCard** - Main recipe display with techniques/nutrition
2. **RecipeCarousel** - Swipeable card container
3. **TechniqueList** - Bulleted list with custom chef icons
4. **NutritionSummary** - Compact nutrition grid
5. **DifficultyBadge** - Star rating + skill level
6. **LoadingAgentProgress** - Multi-step progress indicator

---

## Implementation Plan

### Phase 1: Core Layout (Day 1)
1. Set up Next.js 14 app structure
2. Configure Plus Jakarta Sans font
3. Copy border-assets and accent-icons from the-bugle
4. Build input form page
5. Style with hand-drawn borders

### Phase 2: Recipe Cards (Day 2)
1. Design RecipeCard component
2. Build swipeable carousel
3. Add progress dots
4. Implement nutrition display
5. Add technique highlights

### Phase 3: States & Polish (Day 3)
1. Loading states with agent progress
2. Empty/error states
3. Animations and transitions
4. Mobile gesture optimization
5. Accessibility audit

---

## File Structure

```
ratatouille-frontend/
├── app/
│   ├── layout.tsx          # Root layout with font
│   ├── globals.css         # the-bugle styles adapted
│   ├── page.tsx            # Input form
│   └── results/
│       └── page.tsx        # Recipe carousel
├── components/
│   ├── ui/                 # Copied from the-bugle
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── badge.tsx
│   ├── RecipeCard.tsx      # New
│   ├── RecipeCarousel.tsx  # New
│   ├── TechniqueList.tsx   # New
│   └── AgentProgress.tsx   # New
└── public/
    ├── border-assets/      # From the-bugle
    ├── accent-icons/       # From the-bugle
    └── ratatouille-logo.svg # New logo
```

---

## Design Inspiration Summary

**What We're Borrowing:**
- ✅ Hand-drawn line borders
- ✅ Circle border accents for buttons
- ✅ Plus Jakarta Sans typography
- ✅ Black/white/navy color scheme
- ✅ Mobile-first touch optimizations
- ✅ Playful but professional aesthetic

**What's Original:**
- 🆕 Recipe card layout (techniques + nutrition focus)
- 🆕 Swipeable carousel interaction
- 🆕 Agent progress loading states
- 🆕 Culinary-specific iconography
- 🆕 Technique-focused UX flow

---

**Ready to build:** This design system gives us a professional, unique look that leverages your existing assets while feeling fresh for a cooking app.

**Next Step:** Create React components following this spec.
