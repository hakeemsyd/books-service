/**
 * Common type definitions for the application
 */

export interface HealthCheckResponse {
  status: string
}

export interface ApiError {
  message: string
  status?: number
  data?: unknown
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface Transaction {
  id: string
  name: string
  amount: number
  date: string
  accountId: string
  category?: string
  reviewed?: boolean
}

export interface Category {
  id: string
  name: string
  business?: string
}

export interface CategorizationResult {
  auto: Transaction[]
  suggested: Transaction[]
  needsReview: Transaction[]
}
