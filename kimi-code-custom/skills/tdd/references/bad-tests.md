# Bad Tests Reference

## Anti-Patterns

### 1. Testing Implementation Details
```typescript
// ❌ BAD: Tests internal function calls
it("calls calculateDiscount with correct arguments", () => {
  const spy = jest.spyOn(pricingModule, "calculateDiscount");
  cart.applyCoupon("SAVE20");
  expect(spy).toHaveBeenCalledWith(100, 20);
});
```
→ Breaks when you inline the discount calculation.

### 2. Testing Multiple Behaviors in One Test
```typescript
// ❌ BAD: 5 different behaviors, hard to tell which failed
it("works correctly", () => {
  const user = createUser("test");
  expect(user.name).toBe("test");
  expect(user.id).toBeDefined();
  expect(user.createdAt).toBeInstanceOf(Date);
  expect(user.isActive).toBe(true);
  expect(user.settings).toEqual({});
});
```
→ Split into 5 separate tests with descriptive names.

### 3. Tests That Depend on Other Tests
```typescript
// ❌ BAD: Test 2 fails if run alone
describe("User flow", () => {
  it("creates user", () => {
    user = createUser("test"); // global variable!
  });

  it("updates user", () => {
    user.name = "updated"; // depends on previous test
    expect(user.name).toBe("updated");
  });
});
```
→ Each test must be independent. Use `beforeEach` to reset state.

### 4. Tests With No Assert
```typescript
// ❌ BAD: What is this testing?
it("fetches data", async () => {
  const data = await fetchData();
  console.log(data);
});
```
→ Every test must have at least one assertion that verifies behavior.

### 5. Tests That Mock Everything
```typescript
// ❌ BAD: Mocking the system under test
it("sends email", async () => {
  const mockSend = jest.fn();
  EmailService.prototype.send = mockSend;

  await notifyUser(user);

  expect(mockSend).toHaveBeenCalled();
});
```
→ If you mock the thing you're testing, you're not testing it. Mock dependencies, not the unit under test.
