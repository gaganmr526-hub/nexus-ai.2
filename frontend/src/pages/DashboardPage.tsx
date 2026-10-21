import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import {
  BuildingIcon,
  NetworkIcon,
  AlertTriangleIcon,
  DollarSignIcon,
  ShieldIcon,
  ZapIcon,
  PackageIcon,
  TrendingUpIcon,
} from 'lucide-react'
import { useCompany } from '@/hooks/useCompany'
import { getDashboardStats } from '@/api/companies'
import { getFindings } from '@/api/dependencies'
import { getSuppliers } from '@/api/suppliers'
import DemoBanner from '@/components/DemoBanner'
import KPICard from '@/components/KPICard'
import LoadingSpinner from '@/components/LoadingSpinner'
import { format } from 'date-fns'

const RISK_COLORS = ['#22c55e', '#f59e0b', '#ef4444', '#7c3aed']

const fmt = (n: number) =>
  n >= 1_000_000
    ? `$${(n / 1_000_000).toFixed(1)}M`
    : n >= 1_000
      ? `$${(n / 1_000).toFixed(0)}K`
      : `$${n}`

export default function DashboardPage() {
  const navigate = useNavigate()
  const { selectedCompany } = useCompany()

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
    refetch,
  } = useQuery({
    queryKey: ['dashboard-stats', selectedCompany?.id],
    queryFn: () => getDashboardStats(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const { data: findings = [] } = useQuery({
    queryKey: ['findings', selectedCompany?.id],
    queryFn: () => getFindings(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers', selectedCompany?.id],
    queryFn: () => getSuppliers(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to view the dashboard.</p>
      </div>
    )
  }

  if (statsLoading) return <div className="flex justify-center py-24"><LoadingSpinner size="lg" /></div>
  const riskDist = [
    { name: 'Low', value: suppliers.filter((s) => s.criticality === 'low').length },
    { name: 'Medium', value: suppliers.filter((s) => s.criticality === 'medium').length },
    { name: 'High', value: suppliers.filter((s) => s.criticality === 'high').length },
    { name: 'Critical', value: suppliers.filter((s) => s.criticality === 'critical').length },
  ]

  const tierDist = [1, 2, 3, 4].map((tier) => ({
    tier: `Tier ${tier}`,
    count: suppliers.filter((s) => s.tier_level === tier).length,
  }))

  const topFindings = findings
    .filter((f) => f.severity === 'critical' || f.severity === 'high')
    .slice(0, 5)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">{selectedCompany.name}</h1>
          <p className="text-slate-500 text-sm mt-0.5">Supply Chain Intelligence Dashboard</p>
        </div>
        {stats && (
          <p className="text-slate-600 text-xs">
            Last updated: {format(new Date(stats.last_updated), 'MMM d, HH:mm')}
          </p>
        )}
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      {statsError && (
        <div
          role="alert"
          className="rounded-lg border border-amber-800 bg-amber-950/40 px-4 py-3 text-sm text-amber-300"
        >
          Summary metrics are unavailable, but supplier and risk data can still be viewed.
          <button className="ml-2 underline" onClick={() => refetch()}>
            Retry
          </button>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          title="Total Suppliers"
          value={stats?.total_suppliers ?? suppliers.length}
          icon={BuildingIcon}
          subtitle={`${stats?.total_upstream_entities ?? 0} upstream entities`}
          onClick={() => navigate('/network')}
        />
        <KPICard
          title="Shared Upstream Sources"
          value={
            stats?.shared_upstream_sources ??
            findings.filter((f) => f.finding_type === 'hidden_dependency').length
          }
          icon={NetworkIcon}
          severity="warning"
          subtitle="Hidden dependencies"
          onClick={() => navigate('/dependencies')}
        />
        <KPICard
          title="Critical Risk Sources"
          value={
            stats?.critical_risk_sources ??
            findings.filter((f) => f.severity === 'critical').length
          }
          icon={AlertTriangleIcon}
          severity="critical"
          onClick={() => navigate('/risks')}
        />
        <KPICard
          title="Revenue Exposure"
          value={stats ? fmt(stats.estimated_revenue_exposure) : '—'}
          icon={DollarSignIcon}
          severity={
            stats && stats.estimated_revenue_exposure > 1_000_000 ? 'critical' : 'warning'
          }
          subtitle={stats?.currency ?? 'USD'}
          onClick={() => navigate('/impact')}
        />
        <KPICard
          title="Products at Risk"
          value={stats?.products_at_risk ?? 0}
          icon={PackageIcon}
          onClick={() => navigate('/simulator')}
        />
        <KPICard
          title="Recovery Cost Est."
          value={stats ? fmt(stats.estimated_recovery_cost) : '—'}
          icon={ShieldIcon}
          onClick={() => navigate('/recovery')}
        />
        <KPICard
          title="Risk Reduction Potential"
          value={stats ? `${stats.risk_reduction_potential}%` : '—'}
          icon={TrendingUpIcon}
          onClick={() => navigate('/alternatives')}
        />
        <KPICard
          title="Scenario Affected"
          value={stats?.active_scenario_affected_suppliers ?? 0}
          icon={ZapIcon}
          subtitle="Active scenario suppliers"
          onClick={() => navigate('/simulator')}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Suppliers by Tier</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={tierDist} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <XAxis
                dataKey="tier"
                tick={{ fill: '#64748b', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: '#64748b', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141540',
                  border: '1px solid #1e2166',
                  borderRadius: 8,
                  color: '#94a3b8',
                }}
              />
              <Bar dataKey="count" fill="#4f5de8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={riskDist}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={65}
                innerRadius={35}
              >
                {riskDist.map((_, i) => (
                  <Cell key={i} fill={RISK_COLORS[i]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#141540',
                  border: '1px solid #1e2166',
                  borderRadius: 8,
                }}
              />
              <Legend
                iconType="circle"
                iconSize={8}
                wrapperStyle={{ fontSize: 12, color: '#94a3b8' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {topFindings.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-300">Critical & High Findings</h3>
            <button
              className="text-navy-400 text-sm hover:text-navy-300 transition-colors"
              onClick={() => navigate('/dependencies')}
            >
              View all →
            </button>
          </div>
          <div className="space-y-3">
            {topFindings.map((f) => (
              <div
                key={f.id}
                className="flex items-start gap-3 p-3 bg-navy-800/50 rounded-lg cursor-pointer hover:bg-navy-800 transition-colors"
                onClick={() => navigate('/dependencies')}
              >
                <AlertTriangleIcon
                  className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                    f.severity === 'critical' ? 'text-purple-400' : 'text-red-400'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-slate-200 text-sm font-medium truncate">{f.title}</p>
                  <p className="text-slate-500 text-xs mt-0.5 line-clamp-1">{f.description}</p>
                </div>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${
                    f.severity === 'critical'
                      ? 'bg-purple-900/40 text-purple-400'
                      : 'bg-red-900/40 text-red-400'
                  }`}
                >
                  {f.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
