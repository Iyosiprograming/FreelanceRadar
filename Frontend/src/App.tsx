import {ProtectedRoute} from './ProtectedRoute'
import {Routes, Route} from 'react-router-dom'
import {HomePage} from './Pages/HomePage'
import {DashboardPage} from './Pages/DashboardPage'
import {NotFoundPage} from './Pages/NotFoundPage'
function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  )
}

export default App
