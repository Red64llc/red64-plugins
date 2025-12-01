# Type Safety

Type safety is a core strength of TypeScript. Leverage the type system to catch errors at compile time.

## DO

Use explicit types for function parameters and return values:

```typescript
function calculateDiscount(price: number, percentage: number): number {
    return price * (percentage / 100);
}

async function fetchUser(id: string): Promise<User | null> {
    const response = await api.get(`/users/${id}`);
    return response.data;
}
```

Use discriminated unions for type-safe state handling:

```typescript
type RequestState<T> =
    | { status: 'idle' }
    | { status: 'loading' }
    | { status: 'success'; data: T }
    | { status: 'error'; error: Error };

function handleState(state: RequestState<User>) {
    switch (state.status) {
        case 'success':
            return state.data.name;
        case 'error':
            return state.error.message;
    }
}
```

Enable strict null checks and handle nullable values explicitly:

```typescript
function getUsername(user: User | null): string {
    if (!user) {
        return 'Guest';
    }
    return user.name;
}

const name = user?.profile?.displayName ?? 'Unknown';
```

## DON'T

Avoid using the `any` type as it bypasses type checking:

```typescript
// Avoid: loses all type safety
const data: any = fetchData();
function process(input: any): any { ... }

// Prefer: use unknown for truly unknown types
const data: unknown = fetchData();
if (isUser(data)) {
    console.log(data.name);
}
```

Avoid type assertions without proper validation:

```typescript
// Avoid: unsafe assertion
const user = response.data as User;

// Prefer: validate before asserting
function isUser(data: unknown): data is User {
    return typeof data === 'object' && data !== null && 'id' in data;
}

if (isUser(response.data)) {
    const user = response.data;
}
```

Avoid ignoring null and undefined values:

```typescript
// Avoid: ignoring potential null
const length = user.name.length;

// Prefer: handle null explicitly
const length = user?.name?.length ?? 0;
```
