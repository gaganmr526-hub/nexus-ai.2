import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/store/auth'
import { CompanyProvider } from '@/hooks/useCompany'
import Layout from '@/components/Layout'
import LoginPage from '@/pages/LoginPage'
import OnboardingPage from '@/pages/OnboardingPage'
import DashboardPage from '@/pages/DashboardPage'
import NetworkExplorerPage from '@/pages/NetworkExplorerPage'
import HiddenDependencyPage from '@/pages/HiddenDependencyPage'
import DisruptionSimulatorPage from '@/pages/DisruptionSimulatorPage'
import RiskRegisterPage from '@/pages/RiskRegisterPage'
import ImpactProtectionPage from '@/pages/ImpactProtectionPage'
import AlternativeSuppliersPage from '@/pages/AlternativeSuppliersPage'
import ProcurementPage from '@/pages/ProcurementPage'
import RecoveryPlannerPage from '@/pages/RecoveryPlannerPage'
import PurchaseOrdersPage from '@/pages/PurchaseOrdersPage'
import DataImportPage from '@/pages/DataImportPage'
import ReportsPage from '@/pages/ReportsPage'
import NotificationsPage from '@/pages/NotificationsPage'
import AdminPage from '@/pages/AdminPage'
import LoadingSpinner from '@/components/LoadingSpinner'

function ProtectedRoutes() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />

  return (
    <CompanyProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/network" element={<NetworkExplorerPage />} />
          <Route path="/dependencies" element={<HiddenDependencyPage />} />
          <Route path="/simulator" element={<DisruptionSimulatorPage />} />
          <Route path="/risks" element={<RiskRegisterPage />} />
          <Route path="/impact" element={<ImpactProtectionPage />} />
          <Route path="/alternatives" element={<AlternativeSuppliersPage />} />
          <Route path="/procurement" element={<ProcurementPage />} />
          <Route path="/recovery" element={<RecoveryPlannerPage />} />
          <Route path="/orders" element={<PurchaseOrdersPage />} />
          <Route path="/import" element={<DataImportPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </Layout>
    </CompanyProvider>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/onboarding" element={
          <CompanyProvider>
            <OnboardingPage />
          </CompanyProvider>
        } />
        <Route path="/*" element={<ProtectedRoutes />} />
      </Routes>
    </AuthProvider>
  )
}
