# Async Patterns

Proper async patterns ensure predictable, maintainable, and performant TypeScript code.

## DO

Use async/await for cleaner asynchronous code:

```typescript
async function fetchUserWithOrders(userId: string): Promise<UserWithOrders> {
    const user = await userService.getById(userId);
    const orders = await orderService.getByUserId(userId);
    return { ...user, orders };
}
```

Use Promise.all for parallel operations:

```typescript
async function fetchDashboardData(userId: string): Promise<DashboardData> {
    const [user, orders, notifications] = await Promise.all([
        userService.getById(userId),
        orderService.getByUserId(userId),
        notificationService.getUnread(userId),
    ]);
    return { user, orders, notifications };
}
```

Implement proper cancellation with AbortController:

```typescript
async function fetchWithTimeout<T>(
    url: string,
    timeoutMs: number
): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const response = await fetch(url, { signal: controller.signal });
        return response.json();
    } finally {
        clearTimeout(timeoutId);
    }
}
```

Use Promise.allSettled when partial failures are acceptable:

```typescript
async function sendNotifications(userIds: string[]): Promise<NotificationResults> {
    const results = await Promise.allSettled(
        userIds.map(id => notificationService.send(id))
    );

    return {
        succeeded: results.filter(r => r.status === 'fulfilled').length,
        failed: results.filter(r => r.status === 'rejected').length,
    };
}
```

## DON'T

Avoid mixing callbacks and promises:

```typescript
// Avoid: callback inside async function
async function processFile(path: string) {
    fs.readFile(path, (err, data) => {
        if (err) throw err;
        console.log(data);
    });
}

// Prefer: promisified version
async function processFile(path: string) {
    const data = await fs.promises.readFile(path);
    console.log(data);
}
```

Avoid unhandled promise rejections:

```typescript
// Avoid: fire-and-forget without error handling
fetchUser(userId);

// Prefer: handle or await the promise
fetchUser(userId).catch(err => logger.error('Fetch failed', err));

// Or in async context
try {
    await fetchUser(userId);
} catch (err) {
    logger.error('Fetch failed', err);
}
```

Avoid sequential awaits when operations are independent:

```typescript
// Avoid: unnecessary sequential execution
const user = await fetchUser(id);
const orders = await fetchOrders(id);
const settings = await fetchSettings(id);

// Prefer: parallel execution
const [user, orders, settings] = await Promise.all([
    fetchUser(id),
    fetchOrders(id),
    fetchSettings(id),
]);
```

Avoid race conditions with shared mutable state:

```typescript
// Avoid: race condition
let latestResult: Data;
async function fetchData() {
    const data = await api.fetch();
    latestResult = data;
}

// Prefer: use request tracking
let currentRequestId = 0;
async function fetchData() {
    const requestId = ++currentRequestId;
    const data = await api.fetch();
    if (requestId === currentRequestId) {
        setResult(data);
    }
}
```
