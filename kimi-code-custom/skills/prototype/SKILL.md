---
name: prototype
description: Build a throwaway prototype to flesh out a design — either a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route.
---

# /prototype — Design Exploration

> "Prototyping is the conversation you have with your ideas." — Before committing to implementation, test your assumptions.

## When to Use

- When a design decision has 2+ viable approaches
- When you're unsure about a UI pattern or interaction
- When business logic complexity needs validation before coding
- When the user says "I'm not sure what I want — show me options"

## When NOT to Use

- When the design is already clear and agreed upon
- For trivial UI elements (buttons, inputs)
- When time is critical and the approach is obvious

## Prototype Types

### Type A: Terminal Prototype (Business Logic)

For validating algorithms, state machines, or data flows.

**What it is:**
- A standalone Node.js/Python script
- No UI, no database, no external dependencies
- Hardcoded data
- Console output showing state transitions

**Example:**
```typescript
// prototype-cart-rules.ts
// Tests: "What happens when we apply multiple discounts?"

const cart = new Cart();
cart.addItem({ id: "A", price: 100, qty: 2 });
cart.addItem({ id: "B", price: 50, qty: 1 });

console.log("Subtotal:", cart.subtotal); // 250

cart.applyCoupon("SAVE20"); // 20% off
console.log("After SAVE20:", cart.total); // 200

cart.applyCoupon("FREESHIP"); // Waives shipping
console.log("After FREESHIP:", cart.total); // 200 + 0 shipping

// Edge case: stackable?
cart.applyCoupon("EXTRA10"); // 10% off total
console.log("Stacked:", cart.total); // 180?
```

**Rules:**
- Must be runnable with `node prototype-cart-rules.ts` or `python prototype_cart.py`
- No frameworks, no build step
- Output clearly shows state at each step
- Comments explain what behavior is being tested

### Type B: UI Variation Prototype

For validating UI/UX approaches.

**What it is:**
- A single route/page in your app
- Multiple variations toggleable via query param or state
- Minimal styling (focus on layout and interaction)
- No backend integration (mock data)

**Example:**
```tsx
// /prototype/dashboard?variant=A
// /prototype/dashboard?variant=B
// /prototype/dashboard?variant=C

export default function DashboardPrototype() {
  const variant = useSearchParams().get("variant") || "A";

  return (
    <div>
      <div className="prototype-nav">
        <a href="?variant=A">A: Sidebar</a>
        <a href="?variant=B">B: Top Nav</a>
        <a href="?variant=C">C: Bottom Sheet</a>
      </div>

      {variant === "A" && <SidebarLayout />}
      {variant === "B" && <TopNavLayout />}
      {variant === "C" && <BottomSheetLayout />}
    </div>
  );
}
```

**Rules:**
- All variations in one file for easy comparison
- Query param makes it shareable (send link to designer)
- No real data — use realistic mock data
- Focus on layout, not polish (no animations, minimal color)

## Process

### Step 1: Define the Question

What decision are we trying to make?

```
"Should discount coupons stack or be exclusive?"
"Should the dashboard use a sidebar or top navigation?"
"Should we paginate or infinite-scroll the product list?"
```

### Step 2: Build the Prototype

- Terminal prototype: 30-100 lines, runnable script
- UI prototype: 1 route, 2-3 variations, mock data

### Step 3: Run and Document

```
## Prototype Results: [Question]

**Option A:** [Description]
- Pros: [list]
- Cons: [list]
- Output: [paste terminal output or screenshot]

**Option B:** [Description]
- Pros: [list]
- Cons: [list]
- Output: [paste terminal output or screenshot]

**Recommendation:** [A or B, with rationale]

**Next Step:** [What to implement based on this]
```

### Step 4: Discard

Prototypes are throwaway. Do NOT:
- Merge prototype code into main
- Use prototype code as the foundation for real implementation
- Leave prototype routes in production

Save the prototype in a separate branch or `prototypes/` directory that is `.gitignore`d.

## Edge Cases

**"All options look the same"**
→ You're prototyping the wrong thing. The decision isn't about UI — it's about behavior. Switch to a terminal prototype.

**"The prototype works but production will be different"**
→ That's the point! The prototype validates the concept. Now you know the concept works before investing in production-quality code.

## Success Criteria

This skill succeeded if:
- A decision was made based on prototype results
- The prototype clearly showed differences between options
- The prototype was discarded after the decision (not merged)
- The user feels confident about the chosen approach
