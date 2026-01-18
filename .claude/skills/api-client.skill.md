# API Client Generator Skill

## Purpose
Generate TypeScript API client functions with proper error handling, type safety, and React Query integration.

## Process

### API Function Template
```typescript
import { API_BASE_URL } from '@/lib/config'

export class APIError extends Error {
  constructor(message: string, public status?: number, public data?: any) {
    super(message)
  }
}

async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include', // Include cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new APIError(error.detail || `HTTP ${response.status}`, response.status, error)
  }

  if (response.status === 204) return null as T
  return await response.json()
}

// CRUD operations
export const get{Resource}s = () =>
  fetchAPI<{Resource}[]>('/api/v1/{resources}')

export const get{Resource} = (id: number) =>
  fetchAPI<{Resource}>(`/api/v1/{resources}/${id}`)

export const create{Resource} = (data: {Resource}Create) =>
  fetchAPI<{Resource}>('/api/v1/{resources}', {
    method: 'POST',
    body: JSON.stringify(data),
  })

export const update{Resource} = (id: number, data: {Resource}Update) =>
  fetchAPI<{Resource}>(`/api/v1/{resources}/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })

export const delete{Resource} = (id: number) =>
  fetchAPI<void>(`/api/v1/{resources}/${id}`, {
    method: 'DELETE',
  })
```

## React Query Hooks
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export function use{Resource}s() {
  return useQuery({
    queryKey: ['{resources}'],
    queryFn: get{Resource}s,
  })
}

export function useCreate{Resource}() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: create{Resource},
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['{resources}'] })
    },
  })
}
```

## Output
Complete API client with type safety and React Query integration.
