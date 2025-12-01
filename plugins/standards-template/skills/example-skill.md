# Example Skill: Naming Conventions

This is a template demonstrating the SKILL.md format for standards plugins. Each skill should focus on a single coding standard topic and provide clear guidance with examples.

## DO

Use descriptive, consistent naming that reveals intent and follows language conventions.

### Variable and Function Names

Use camelCase for variables and functions with descriptive names:

```typescript
const userAccountBalance = calculateTotal(items);

function getUserPreferences(userId: string): UserPreferences {
    return preferences.get(userId);
}
```

### Type and Interface Names

Use PascalCase for types, interfaces, and classes:

```typescript
interface UserProfile {
    id: string;
    displayName: string;
    createdAt: Date;
}

type PaymentStatus = 'pending' | 'completed' | 'failed';

class OrderProcessor {
    process(order: Order): ProcessedOrder { ... }
}
```

### Constants

Use SCREAMING_SNAKE_CASE for true constants:

```typescript
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT_MS = 5000;
```

## DON'T

Avoid naming patterns that reduce code clarity or violate language conventions.

### Single-Letter Variables

Avoid single-letter names outside of narrow contexts (loop counters, coordinates):

```typescript
// Avoid: unclear intent
const d = new Date();
const u = getUser();

// Prefer: descriptive names
const currentDate = new Date();
const authenticatedUser = getUser();
```

### Hungarian Notation

Avoid prefixing variable names with type information:

```typescript
// Avoid: redundant type encoding
const strUserName: string = 'Alice';
const arrItems: Item[] = [];
const objConfig: Config = {};

// Prefer: TypeScript provides type information
const userName: string = 'Alice';
const items: Item[] = [];
const config: Config = {};
```

### Inconsistent Casing

Avoid mixing naming conventions within the same scope:

```typescript
// Avoid: inconsistent style
const user_name = 'Alice';
const UserAge = 25;
const userEmail = 'alice@example.com';

// Prefer: consistent camelCase
const userName = 'Alice';
const userAge = 25;
const userEmail = 'alice@example.com';
```
