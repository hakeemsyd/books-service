# TypeScript Setup Guide

This frontend has been fully converted to TypeScript for better type safety and developer experience.

## What Changed

✅ **File Extensions**
- `.jsx` → `.tsx` (React components)
- `.js` → `.ts` (Regular JavaScript)
- Added `vite-env.d.ts` for Vite environment types

✅ **Configuration Files**
- `tsconfig.json` - Main TypeScript configuration
- `tsconfig.node.json` - Config for build tools
- `.eslintrc.json` - ESLint with TypeScript support
- `.prettierrc.json` - Code formatting rules

✅ **Dev Dependencies**
- `typescript` - TypeScript compiler
- `@types/react`, `@types/react-dom` - React type definitions
- `@typescript-eslint/*` - TypeScript linting
- `eslint`, `prettier` - Code quality tools

## Project Structure

```
frontend/src/
├── main.tsx                    # React entry point
├── App.tsx                     # Root component (typed)
├── vite-env.d.ts              # Environment variable types
├── components/
│   ├── LoadingSpinner.tsx      # Example typed component
│   └── LoadingSpinner.css
├── pages/
│   └── HomePage.tsx           # Example typed page
├── services/
│   └── api.ts                 # Typed API client
├── hooks/
│   └── useApi.ts              # Example typed hook
├── types/
│   └── index.ts               # Shared type definitions
└── styles/
    └── index.css
```

## Running & Commands

```bash
# Install dependencies (includes TypeScript)
npm install

# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint          # Check for issues
npm run lint:fix      # Auto-fix issues

# Code formatting
npm run format        # Format all files
npm run format:check  # Check if formatted

# Build
npm run build         # Type-checks then builds
npm run preview       # Preview production build
```

## Writing Typed Components

### Functional Component with Props

```typescript
interface ButtonProps {
  label: string
  onClick: () => void
  disabled?: boolean
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, disabled }) => (
  <button onClick={onClick} disabled={disabled}>
    {label}
  </button>
)
```

### Component with State

```typescript
import React, { useState } from 'react'

export const Counter: React.FC = () => {
  const [count, setCount] = useState<number>(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  )
}
```

### Using Custom Hooks

```typescript
import { useApi } from '../hooks/useApi'
import type { Transaction } from '../types'

export const TransactionList: React.FC = () => {
  const { data, loading, error, fetch } = useApi<Transaction[]>('/transactions', [])

  React.useEffect(() => {
    fetch()
  }, [fetch])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  if (!data) return <div>No data</div>

  return (
    <ul>
      {data.map((tx) => (
        <li key={tx.id}>{tx.name}</li>
      ))}
    </ul>
  )
}
```

## Adding New Files

### New Component

Create `src/components/MyComponent.tsx`:

```typescript
import React from 'react'
import './MyComponent.css'

interface MyComponentProps {
  title: string
}

export const MyComponent: React.FC<MyComponentProps> = ({ title }) => (
  <div className="my-component">
    <h2>{title}</h2>
  </div>
)

export default MyComponent
```

### New Custom Hook

Create `src/hooks/useMyHook.ts`:

```typescript
import { useState, useCallback } from 'react'

interface UseMyHookState {
  value: string
}

export const useMyHook = () => {
  const [state, setState] = useState<UseMyHookState>({ value: '' })

  const setValue = useCallback((value: string) => {
    setState({ value })
  }, [])

  return { ...state, setValue }
}
```

### New Type Definition

Add to `src/types/index.ts`:

```typescript
export interface MyType {
  id: string
  name: string
}
```

## Type Definitions

### Common Patterns

**API Responses:**
```typescript
interface ApiResponse<T> {
  data: T
  status: number
}
```

**React Event Handlers:**
```typescript
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {}
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {}
```

**Component Children:**
```typescript
interface WithChildrenProps {
  children: React.ReactNode
}

export const Wrapper: React.FC<WithChildrenProps> = ({ children }) => (
  <div>{children}</div>
)
```

## Strict Mode

TypeScript is configured in strict mode. This means:
- `noImplicitAny: true` - No implicit `any` types
- `strictNullChecks: true` - Null/undefined safety
- `strictFunctionTypes: true` - Function type safety
- And more...

If you get type errors, use the proper types instead of `as any`.

## ESLint & Prettier

The project includes ESLint and Prettier for code quality:

```bash
# Check for issues
npm run lint

# Auto-fix issues
npm run lint:fix

# Format code
npm run format
```

Configuration:
- `.eslintrc.json` - ESLint rules
- `.prettierrc.json` - Formatting rules

## Gradual Adoption

You can migrate files gradually:
1. Keep old `.js` / `.jsx` files working
2. Migrate one file/component at a time to `.ts` / `.tsx`
3. TypeScript compiler will catch issues
4. No need to convert everything at once

## Troubleshooting

### "Cannot find module"
- Check file extension is `.ts` or `.tsx`
- Run `npm run type-check` to find issues

### "Type not found"
- Add type definition to `src/types/index.ts`
- Or install types: `npm install --save-dev @types/package-name`

### "Unused variable"
- Delete the unused code
- Or prefix with `_` to ignore: `const _unused = ...`

### Build fails
Run type checking first:
```bash
npm run type-check
```

Fix any errors before building.

## Learning Resources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [Vite TypeScript Docs](https://vitejs.dev/guide/features.html#typescript)
