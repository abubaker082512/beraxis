import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MarketingLayout from './layouts/MarketingLayout';
import DashboardLayout from './layouts/DashboardLayout';

// Marketing Pages
import Home from './pages/marketing/Home';
import Features from './pages/marketing/Features';
import Pricing from './pages/marketing/Pricing';
import About from './pages/marketing/About';
import Contact from './pages/marketing/Contact';
import Login from './pages/marketing/Login';
import Register from './pages/marketing/Register';
import BookDemo from './pages/marketing/BookDemo';

// Dashboard Pages
import DashboardOverview from './pages/dashboard/Overview';
import Campaigns from './pages/dashboard/Campaigns';
import AgentBuilder from './pages/dashboard/AgentBuilder';
import CallLogs from './pages/dashboard/CallLogs';
import Contacts from './pages/dashboard/Contacts';
import Billing from './pages/dashboard/Billing';
import AdminPanel from './pages/dashboard/Admin';
import Settings from './pages/dashboard/Settings';

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Marketing Routes */}
        <Route element={<MarketingLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/features" element={<Features />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/book-demo" element={<BookDemo />} />
        </Route>

        {/* Dashboard Routes */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<DashboardOverview />} />
          <Route path="campaigns" element={<Campaigns />} />
          <Route path="agent-builder" element={<AgentBuilder />} />
          <Route path="call-logs" element={<CallLogs />} />
          <Route path="contacts" element={<Contacts />} />
          <Route path="billing" element={<Billing />} />
          <Route path="admin" element={<AdminPanel />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}
