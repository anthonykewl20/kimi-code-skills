# Deep Modules Reference

## Characteristics of Deep Modules

1. **Simple Interface, Complex Implementation**
   - Few public methods (usually 1-5)
   - Rich private implementation
   - Hides complexity from consumers

2. **Information Hiding**
   - Internal data structures are private
   - Algorithms are encapsulated
   - Consumers don't need to know HOW it works

3. **High Functionality-to-Interface Ratio**
   - One method call accomplishes a lot
   - No "setup" required before use
   - Sensible defaults for all optional behavior

## Examples

### Deep: File System
```typescript
// Interface: 1 method
fs.readFile("/path/to/file");

// Implementation: thousands of lines
// - Path resolution
// - Permission checks
// - Buffer management
// - Encoding handling
// - Error translation
```

### Shallow: String Utilities (Bad)
```typescript
// Interface: 20 methods
StringUtils.isEmpty(str);
StringUtils.isNotEmpty(str);
StringUtils.trim(str);
StringUtils.trimLeft(str);
StringUtils.trimRight(str);
StringUtils.toCamelCase(str);
StringUtils.toSnakeCase(str);
// ... 13 more

// Implementation: each is 1-3 lines
```

### Deepened: String Utilities (Good)
```typescript
// Interface: 3 methods
StringUtils.validate(str, rules);     // flexible validation
StringUtils.transform(str, strategy); // flexible transformation
StringUtils.parse(str, format);       // flexible parsing

// Implementation: complex rule engine, strategy pattern
```

## How to Deepen a Shallow Module

1. **Group by responsibility** — split 20 methods into 3-4 focused classes
2. **Parameterize** — replace `isEmpty`/`isNotEmpty` with `validate(str, { allowEmpty: false })`
3. **Compose** — instead of 5 sequential calls, provide one `process()` method
4. **Default everything** — require zero configuration for 80% use cases
