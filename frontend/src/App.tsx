import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import './App.css'

const App: React.FC = () => {
  return (
    <Router>
      <div className="app">
        <header>
          <h1>📚 Books Categorization Service</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
