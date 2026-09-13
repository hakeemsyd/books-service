import { useState, useCallback } from 'react'
import apiClient from '../services/api'
import type { ApiError } from '../types'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
}

export const useApi = <T,>(url: string, initialData: T | null = null) => {
  const [state, setState] = useState<UseApiState<T>>({
    data: initialData,
    loading: false,
    error: null,
  })

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const response = await apiClient.get<T>(url)
      setState({ data: response.data, loading: false, error: null })
      return response.data
    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'An error occurred',
        status: error instanceof Error && 'status' in error ? (error as any).status : undefined,
      }
      setState((prev) => ({ ...prev, loading: false, error: apiError }))
      throw apiError
    }
  }, [url])

  return {
    ...state,
    fetch: fetchData,
  }
}

export default useApi
