# Naming Conventions

Consistent naming conventions improve code readability and maintainability across TypeScript codebases.

## DO

Use PascalCase for types, interfaces, classes, and enums:

```typescript
interface UserProfile {
    id: string;
    displayName: string;
}

type PaymentStatus = 'pending' | 'completed' | 'failed';

class OrderProcessor {
    process(order: Order): ProcessedOrder { ... }
}

enum HttpStatus {
    Ok = 200,
    NotFound = 404,
}
```

Use camelCase for variables, functions, and method names:

```typescript
const userAccountBalance = calculateTotal(items);
const isAuthenticated = checkAuth();

function getUserPreferences(userId: string): UserPreferences {
    return preferences.get(userId);
}
```

Use SCREAMING_SNAKE_CASE for true constants:

```typescript
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT_MS = 5000;
const API_BASE_URL = 'https://api.example.com';
```

## DON'T

Avoid Hungarian notation that encodes type information in names:

```typescript
// Avoid: redundant type prefixes
const strUserName: string = 'Alice';
const arrItems: Item[] = [];
const objConfig: Config = {};

// Prefer: clean names, TypeScript provides types
const userName: string = 'Alice';
const items: Item[] = [];
const config: Config = {};
```

Avoid single-letter variable names outside narrow contexts:

```typescript
// Avoid: unclear intent
const d = new Date();
const u = getUser();

// Prefer: descriptive names
const currentDate = new Date();
const authenticatedUser = getUser();
```

Avoid inconsistent casing within the same scope:

```typescript
// Avoid: mixed conventions
const user_name = 'Alice';
const UserAge = 25;
const userEmail = 'alice@example.com';

// Prefer: consistent camelCase
const userName = 'Alice';
const userAge = 25;
const userEmail = 'alice@example.com';
```
