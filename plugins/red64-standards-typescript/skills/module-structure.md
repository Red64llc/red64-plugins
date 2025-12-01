# Module Structure

Well-organized module structure improves maintainability and enables clean imports across the codebase.

## DO

Use barrel exports with index files for clean public APIs:

```typescript
// src/models/index.ts
export { User } from './user';
export { Order } from './order';
export { Product } from './product';
export type { UserProfile, OrderStatus } from './types';

// Consumer can import cleanly
import { User, Order, Product } from '@/models';
```

Organize modules by feature or domain:

```typescript
src/
  features/
    auth/
      index.ts
      auth.service.ts
      auth.types.ts
      hooks/
        useAuth.ts
    orders/
      index.ts
      orders.service.ts
      orders.types.ts
      components/
        OrderList.tsx
```

Separate types into dedicated files when they grow large:

```typescript
// types.ts - shared types for the module
export interface ApiResponse<T> {
    data: T;
    meta: ResponseMeta;
}

export type RequestConfig = {
    timeout?: number;
    retries?: number;
};
```

Use explicit named exports for better tree-shaking:

```typescript
// Prefer named exports
export function calculateTotal(items: Item[]): number { ... }
export function formatCurrency(amount: number): string { ... }
```

## DON'T

Avoid circular dependencies between modules:

```typescript
// Avoid: circular import
// user.ts
import { Order } from './order';
export class User { orders: Order[] }

// order.ts
import { User } from './user';
export class Order { user: User }

// Prefer: extract shared types
// types.ts
export interface IUser { id: string }
export interface IOrder { userId: string }
```

Avoid deeply nested directory structures:

```typescript
// Avoid: excessive nesting
src/modules/features/user/components/forms/inputs/TextInput.tsx

// Prefer: flatter structure
src/features/user/components/TextInput.tsx
```

Avoid mixing concerns within a single module:

```typescript
// Avoid: mixed concerns in one file
// user.ts
export class User { ... }
export function fetchUsers() { ... }
export function renderUserCard() { ... }
export const USER_ROLES = { ... };

// Prefer: separate by responsibility
// user.model.ts - data model
// user.service.ts - API calls
// UserCard.tsx - UI component
// user.constants.ts - constants
```

Avoid default exports for better refactoring support:

```typescript
// Avoid: default exports
export default function processOrder() { ... }

// Prefer: named exports
export function processOrder() { ... }
```
