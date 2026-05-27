# Good Tests Reference

## Principles

1. **Test behavior, not implementation**
2. **Use public APIs only**
3. **One assertion per concept** (not necessarily one `expect()` call)
4. **Tests should read like documentation**
5. **Tests should survive refactoring**

## Examples by Layer

### Unit Tests (Business Logic)
```typescript
// ✅ GOOD: Tests the rule, not the function structure
describe("PasswordValidator", () => {
  it("accepts passwords with 8+ chars, 1 uppercase, 1 number", () => {
    expect(validatePassword("Hello1")).toBe(false); // too short
    expect(validatePassword("hellohello")).toBe(false); // no uppercase
    expect(validatePassword("HELLOHELLO")).toBe(false); // no lowercase
    expect(validatePassword("HelloWorld")).toBe(false); // no number
    expect(validatePassword("HelloWorld1")).toBe(true);
  });
});
```

### Integration Tests (API Layer)
```typescript
// ✅ GOOD: Tests the full request/response cycle
describe("POST /api/users", () => {
  it("creates a user and returns 201 with user ID", async () => {
    const response = await request(app)
      .post("/api/users")
      .send({ email: "test@example.com", password: "HelloWorld1" });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty("id");
    expect(response.body.email).toBe("test@example.com");
    // Password should NEVER be returned
    expect(response.body).not.toHaveProperty("password");
  });
});
```

### Component Tests (UI Layer)
```tsx
// ✅ GOOD: Tests user-visible behavior
import { render, screen, fireEvent } from "@testing-library/react";

describe("LoginForm", () => {
  it("disables submit button when email is invalid", () => {
    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "not-an-email" }
    });

    expect(screen.getByRole("button", { name: "Sign In" })).toBeDisabled();
  });
});
```

## Test Naming Convention

```
[unit under test] should [expected behavior] when [condition]
```

Examples:
- `Cart should calculate total with tax when items exist`
- `AuthService should reject expired tokens when validating`
- `UserRepository should return null when email not found`
