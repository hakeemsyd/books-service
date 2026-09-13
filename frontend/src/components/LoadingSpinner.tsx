import React from 'react'
import './LoadingSpinner.css'

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large'
  message?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  message = 'Loading...',
}) => (
  <div className={`spinner spinner-${size}`}>
    <div className="spinner-ring"></div>
    <p>{message}</p>
  </div>
)

export default LoadingSpinner
