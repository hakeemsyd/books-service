import React, { useEffect } from 'react'
import { healthCheck } from '../services/api'
import { LoadingSpinner } from '../components/LoadingSpinner'

export const HomePage: React.FC = () => {
  const [isHealthy, setIsHealthy] = React.useState<boolean | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        setLoading(true)
        const health = await healthCheck()
        setIsHealthy(health.status === 'ok')
        setError(null)
      } catch (err) {
        setIsHealthy(false)
        setError(err instanceof Error ? err.message : 'Failed to connect to API')
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
  }, [])

  if (loading) {
    return <LoadingSpinner message="Checking API connection..." />
  }

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome to the Books Categorization Service</p>

      <section style={{ marginTop: '20px', padding: '16px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
        <h3>API Status</h3>
        {isHealthy ? (
          <p style={{ color: 'green' }}>✅ Backend API is running</p>
        ) : (
          <p style={{ color: 'red' }}>❌ Cannot connect to backend API</p>
        )}
        {error && <p style={{ color: '#d32f2f', fontSize: '12px' }}>{error}</p>}
      </section>

      <section style={{ marginTop: '20px' }}>
        <h3>Features</h3>
        <ul>
          <li>Automatic transaction categorization</li>
          <li>Slack integration for on-demand runs</li>
          <li>Historical data analysis</li>
          <li>Category suggestions</li>
        </ul>
      </section>
    </div>
  )
}

export default HomePage
