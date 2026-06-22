import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import RFQAnalyzer from './pages/RFQAnalyzer'
import DeviationRegister from './pages/DeviationRegister'
import ContentLibrary from './pages/ContentLibrary'
import AddendumTracker from './pages/AddendumTracker'
import BidNoBid from './pages/BidNoBid'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"   element={<Dashboard />} />
          <Route path="projects"    element={<Projects />} />
          <Route path="rfq"         element={<RFQAnalyzer />} />
          <Route path="deviations"  element={<DeviationRegister />} />
          <Route path="library"     element={<ContentLibrary />} />
          <Route path="addendum"    element={<AddendumTracker />} />
          <Route path="bid-no-bid"  element={<BidNoBid />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
