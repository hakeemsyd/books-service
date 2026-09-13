import axios, { AxiosInstance, AxiosError } from 'axios'

interface HealthCheckResponse {
  status: string
}

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const healthCheck = async (): Promise<HealthCheckResponse> => {
  try {
    const response = await apiClient.get<HealthCheckResponse>('/health')
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError
    console.error('Health check failed:', axiosError)
    throw axiosError
  }
}

export default apiClient
