# Error Handling

Robust error handling improves reliability and debugging in TypeScript applications.

## DO

Create custom error types for domain-specific errors:

```typescript
class ValidationError extends Error {
    constructor(
        message: string,
        public readonly field: string,
        public readonly code: string
    ) {
        super(message);
        this.name = 'ValidationError';
    }
}

class ApiError extends Error {
    constructor(
        message: string,
        public readonly statusCode: number,
        public readonly endpoint: string
    ) {
        super(message);
        this.name = 'ApiError';
    }
}
```

Use the Result pattern for operations that can fail:

```typescript
type Result<T, E = Error> =
    | { success: true; data: T }
    | { success: false; error: E };

function parseJson<T>(json: string): Result<T> {
    try {
        return { success: true, data: JSON.parse(json) };
    } catch (e) {
        return { success: false, error: e as Error };
    }
}

const result = parseJson<User>(input);
if (result.success) {
    console.log(result.data.name);
} else {
    console.error(result.error.message);
}
```

Handle async errors with try-catch or Promise chains:

```typescript
async function fetchUserSafely(id: string): Promise<User | null> {
    try {
        const response = await api.get(`/users/${id}`);
        return response.data;
    } catch (error) {
        logger.error('Failed to fetch user', { id, error });
        return null;
    }
}
```

## DON'T

Avoid empty catch blocks that swallow errors silently:

```typescript
// Avoid: error is lost
try {
    await processOrder(order);
} catch (e) {}

// Prefer: log or re-throw
try {
    await processOrder(order);
} catch (error) {
    logger.error('Order processing failed', { error });
    throw error;
}
```

Avoid throwing generic Error without context:

```typescript
// Avoid: no context for debugging
throw new Error('Failed');

// Prefer: include relevant context
throw new ValidationError(
    'Invalid email format',
    'email',
    'INVALID_EMAIL'
);
```

Avoid catching errors without proper type narrowing:

```typescript
// Avoid: assuming error type
catch (error) {
    console.log(error.message);
}

// Prefer: narrow the error type
catch (error) {
    if (error instanceof ApiError) {
        console.log(`API error ${error.statusCode}: ${error.message}`);
    } else if (error instanceof Error) {
        console.log(error.message);
    }
}
```
