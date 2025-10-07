# Ratatouille Frontend Documentation

Complete guide to the Next.js frontend application.

## Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn UI
- **Icons**: Lucide React
- **State Management**: React hooks + localStorage
- **HTTP Client**: Native fetch API

---

## Application Structure

### Pages (App Router)

**`app/chat/page.tsx`** - Main chat interface
- Primary user interaction point
- Conversational recipe discovery
- Agent progress visualization
- Bookmark/exclude recipe functionality

**`app/cook/page.tsx`** - Interactive cooking mode
- Step-by-step guided cooking
- Timers for each step
- XP rewards and gamification
- Ingredient checklist

**`app/cookbook/page.tsx`** - Saved recipes
- View all bookmarked recipes
- Recipe cards with metadata
- "Let's Cook" action buttons

**`app/page.tsx`** - Landing page
- Redirects to `/chat`

**`app/layout.tsx`** - Root layout
- Global styles
- Font configuration (Geist)
- Metadata

---

## Key Features

### 1. Chat Interface

**File**: `app/chat/page.tsx`

**Features**:
- Natural language recipe requests
- Real-time loading states with chef-themed phrases
- Agent progress visualization (5 steps)
- Recipe cards with bookmarking
- Follow-up Q&A
- Conversation persistence (localStorage)

**State Management**:
```typescript
const [messages, setMessages] = useState<Message[]>([])
const [recipes, setRecipes] = useState<RecipeCardType[]>([])
const [isLoading, setIsLoading] = useState(false)
const [agentSteps, setAgentSteps] = useState<AgentStep[]>(AGENT_STEPS)
```

**Local Storage**:
- `chatMessages`: Conversation history
- `chatRecipes`: Recipe results
- `savedRecipes`: Bookmarked recipes
- Persists across page refreshes
- Cleared when logo clicked (triggers storage event)

**Loading Phrases**:
```typescript
[
  "Searching for the perfect recipes...",
  "Putting on my tiny chef hat...",
  "Saying 'Yes Chef!' as loud as I can...",
  "Doing my best Carmy impression...",
  "Putting out a kitchen fire..."
]
```

Rotates every 2 seconds during 30s wait.

**Agent Progress** (Fake but effective UX):
```typescript
const AGENT_STEPS = [
  { label: "Planning search", status: "pending" },
  { label: "Hunting recipes", status: "pending" },
  { label: "Validating techniques", status: "pending" },
  { label: "Personalizing for you", status: "pending" },
  { label: "Adding nutrition", status: "pending" }
]
```

Updates every 6 seconds (30s / 5 = 6s per step).

---

### 2. Cooking Mode

**File**: `app/cook/page.tsx`

**Features**:
- Step-by-step instructions with timers
- Ingredient checklist
- Progress tracking (XP system)
- Visual step cards with highlights
- Completion screen with XP reward

**URL Parameters**:
- `url`: Recipe URL to cook from
- `title`: Recipe title
- `learning`: What technique user is learning

**Example**:
```
/cook?url=https://example.com/recipe&title=Pan+Sauce+Steak&learning=pan+sauces
```

**Flow**:
1. Extract recipe from URL (`/api/extract`)
2. Generate cooking guide (`/api/cook-guide`)
3. Display step-by-step with timers
4. Track completion and award XP

**Components Used**:
- `IngredientList` - Checkable ingredient list
- `StepCard` - Individual cooking step with timer
- `Timer` - Countdown timer component
- `CompletionCard` - Success screen with XP

---

### 3. Cookbook

**File**: `app/cookbook/page.tsx`

**Features**:
- Grid layout of saved recipes
- Recipe cards with metadata
- "Let's Cook" action buttons
- Empty state for no saved recipes

**Local Storage**:
```typescript
const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes') || '[]')
```

**Recipe Card Data**:
```typescript
{
  recipe: {
    title: string
    url: string
    difficulty: string
    time_estimate: string
  },
  reasoning: string,
  technique_highlights: string[]
}
```

---

## Components

### Navigation
**File**: `components/Navigation.tsx`

Tab bar with icons:
- Chat (MessageCircle icon)
- Cookbook (BookMarked icon)
- Logo (Rat icon) - Clears chat on click

**Active State**:
- Orange fill for active tab
- Gray outline for inactive

### RecipeCard
**File**: `components/RecipeCard.tsx`

**Props**:
```typescript
{
  recipe: RecipeData
  reasoning: string
  techniqueHighlights: string[]
  nutrition?: NutritionData
  onBookmark?: () => void
  onExclude?: () => void
  isBookmarked?: boolean
}
```

**Features**:
- Recipe title, source, difficulty, time
- "Why this recipe" reasoning
- Technique highlights (badges)
- Nutrition info (optional)
- Action buttons:
  - Bookmark (saves to cookbook)
  - Exclude (removes from future results)
  - Let's Cook (opens cooking mode)
  - View Recipe (external link)

### StepCard
**File**: `components/StepCard.tsx`

**Props**:
```typescript
{
  stepNumber: number
  title: string
  instruction: string
  durationMinutes?: number
  keyTechnique?: string
  tips?: string[]
  timerSuggested?: boolean
  onComplete: () => void
}
```

**Features**:
- Step number badge
- Title and instructions
- Key technique highlight
- Tips expansion
- Timer button (if suggested)
- Completion checkbox

### Timer
**File**: `components/Timer.tsx`

**Props**:
```typescript
{
  durationMinutes: number
  onComplete?: () => void
}
```

**Features**:
- Countdown timer
- Start/Pause/Reset controls
- Visual progress ring (CSS animation)
- Audio alert on completion (optional)
- Time formatting (MM:SS)

### IngredientList
**File**: `components/IngredientList.tsx`

**Props**:
```typescript
{
  ingredients: Array<{
    item: string
    amount: string
    preparation?: string
  }>
}
```

**Features**:
- Checkable list items
- Strikethrough when checked
- Amount and preparation display
- localStorage persistence

### CompletionCard
**File**: `components/CompletionCard.tsx`

**Props**:
```typescript
{
  title: string
  xpEarned: number
  onContinue: () => void
}
```

**Features**:
- Success animation
- XP reward display
- Continue button
- Celebration messaging

### ErrorBoundary
**File**: `components/ErrorBoundary.tsx`

React error boundary for graceful error handling.

---

## API Integration

### API Client
**File**: `lib/api.ts`

**Functions**:

```typescript
// Send chat message
sendChatMessage(message, isFollowUp, excludedUrls): Promise<ChatResponse>

// Get recommendations (legacy)
getRecommendations(request): Promise<RecommendationResponse>

// Extract recipe
extractRecipe(url): Promise<{ content: string }>

// Generate cooking guide
getCookingGuide(content, skillLevel, learningFocus): Promise<CookGuide>
```

**Error Handling**:
```typescript
class APIError extends Error {
  constructor(public status: number, message: string)
}
```

All functions throw `APIError` on failure.

**Configuration**:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

---

## Type Definitions

**File**: `lib/types.ts`

### Core Types

```typescript
export interface RecipeCard {
  recipe: {
    title: string
    url: string
    source: string
    author: string
    published_date: string
    difficulty: "beginner" | "intermediate" | "advanced"
    time_estimate: string
  }
  reasoning: string
  technique_highlights: string[]
  nutrition?: {
    calories: number
    protein_g: number
    carbs_g: number
    fat_g: number
    fiber_g: number
    sodium_mg: number
    servings: number
    disclaimer: string
  }
  score: number
}

export interface Message {
  role: "user" | "assistant"
  content: string
  recipes?: RecipeCard[]
}

export interface AgentStep {
  label: string
  status: "pending" | "in_progress" | "completed"
}

export interface CookingStep {
  step_number: number
  title: string
  instruction: string
  duration_minutes?: number
  key_technique?: string
  tips?: string[]
  timer_suggested?: boolean
}

export interface CookGuide {
  title: string
  estimated_time: string
  difficulty: string
  xp_reward: number
  steps: CookingStep[]
  ingredients: Array<{
    item: string
    amount: string
    preparation?: string
  }>
}
```

---

## Styling

### Tailwind Configuration
**File**: `tailwind.config.ts`

Custom colors:
```typescript
colors: {
  border: "hsl(var(--border))",
  background: "hsl(var(--background))",
  foreground: "hsl(var(--foreground))",
  primary: {...},
  secondary: {...},
  // ... Shadcn UI color system
}
```

### Global Styles
**File**: `app/globals.css`

- CSS custom properties for theming
- Tailwind base/components/utilities
- Shadcn UI styles
- Custom animations

---

## User Experience

### Loading States

**Chat Page**:
- Spinner icon
- Rotating loading phrases (2s intervals)
- Agent progress steps (6s intervals)
- Disabled input during loading

**Cook Page**:
- Skeleton loading for recipe extraction
- "Generating your cooking guide..." message
- Smooth transitions

### Error Handling

**API Errors**:
- Display error message in UI
- "Try Again" button
- "Go Back" button
- Specific messages for 403 (blocked sites)

**Network Errors**:
- Timeout after 60s
- Retry mechanism
- Clear error messaging

### Empty States

**No Recipes**:
- Helpful message
- Suggested queries
- Chef rat illustration

**Empty Cookbook**:
- "No saved recipes yet"
- Prompt to search for recipes

### Accessibility

- Semantic HTML elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus visible states
- Screen reader friendly

---

## Performance

### Optimization Techniques

1. **Code Splitting**: Automatic with Next.js App Router
2. **Image Optimization**: Next.js Image component (not currently used)
3. **LocalStorage**: Reduces server requests for saved data
4. **Lazy Loading**: Components load on demand
5. **Memoization**: React.memo for expensive components (future improvement)

### Bundle Size

Current bundle size:
- First Load JS: ~200KB (estimated)
- Largest component: Chat page

Optimization opportunities:
- Tree-shake unused Shadcn components
- Remove unused Tailwind classes
- Optimize icon library imports

---

## Development Workflow

### Local Development

```bash
cd frontend
npm run dev
```

Hot reload enabled for:
- TypeScript files
- CSS/Tailwind
- React components

### Build

```bash
npm run build
```

Generates optimized production build in `.next/`

### Type Checking

```bash
npm run type-check  # (if configured)
```

TypeScript strict mode enabled.

---

## Environment Variables

**Required**:
- `NEXT_PUBLIC_API_URL`: Backend API URL

**Development** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production**:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS Safari, Chrome Android

---

## Future Enhancements

### Planned Features
- [ ] User authentication
- [ ] Recipe rating system
- [ ] Social sharing
- [ ] Offline mode (PWA)
- [ ] Dark mode toggle
- [ ] Recipe notes/modifications
- [ ] Shopping list export
- [ ] Meal planning calendar

### Technical Improvements
- [ ] React Query for server state
- [ ] Zustand for global state
- [ ] Component testing (Vitest)
- [ ] E2E testing (Playwright)
- [ ] Storybook for component docs
- [ ] Performance monitoring (Vercel Analytics)

---

## Troubleshooting

### Common Issues

**Blank screen on load**:
- Check browser console for errors
- Verify API_URL is correct
- Clear localStorage
- Try incognito mode

**Recipes not saving**:
- Check localStorage quota (10MB limit)
- Verify localStorage is enabled
- Check browser privacy settings

**Slow performance**:
- Clear browser cache
- Check network tab for slow requests
- Verify backend is responsive

**Build errors**:
- Delete `.next` folder
- Delete `node_modules` and reinstall
- Check TypeScript errors

---

## Contributing

When adding new features:
1. Follow existing component patterns
2. Use TypeScript for type safety
3. Add proper error handling
4. Update types in `lib/types.ts`
5. Test on mobile viewport
6. Ensure accessibility standards
