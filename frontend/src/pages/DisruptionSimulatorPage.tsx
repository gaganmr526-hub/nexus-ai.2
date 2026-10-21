import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { ZapIcon, PlayIcon, DollarSignIcon, PackageIcon, BuildingIcon, ClockIcon } from 'lucide-react'
import { useCompany } from '@/hooks/useCompany'
import { getScenarios, createScenario, runScenario, getScenarioResult } from '@/api/scenarios'
import { getSuppliers } from '@/api/suppliers'
import type { Scenario } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import LoadingSpinner from '@/components/LoadingSpinner'
import KPICard from '@/components/KPICard'
import StatusBadge from '@/components/StatusBadge'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

const schema = z.object({
  name: z.string().min(1, 'Name required'),
  disruption_type: z.string().min(1, 'Type required'),
  target_supplier_id: z.string().optional(),
  duration_days: z.coerce.number().min(1).max(365),
  capacity_reduction_pct: z.coerce.number().min(0).max(100),
  description: z.string().optional(),
})
type FormData = z.infer<typeof schema>

const fmtMoney = (n: number) =>
  n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(1)}M` : `$${(n / 1_000).toFixed(0)}K`

export default function DisruptionSimulatorPage() {
  const { companies, selectedCompany, selectCompany } = useCompany()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null)
  const [running, setRunning] = useState(false)
  const [pendingJudgeScenario, setPendingJudgeScenario] = useState<string | null>(null)

  const { data: scenarios = [] } = useQuery({
    queryKey: ['scenarios', selectedCompany?.id],
    queryFn: () => getScenarios(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers', selectedCompany?.id],
    queryFn: () => getSuppliers(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const selectedScenario = scenarios.find((s) => s.id === selectedScenarioId)

  const judgeCases = [
    {
      companyName: 'ApexDrive Mobility',
      supplierCount: 29,
      scenarioName: 'Helios Semiconductor Shutdown',
      title: 'Automotive chip shortage',
      description: 'See how an automotive supply network is exposed to a semiconductor shutdown.',
    },
    {
      companyName: 'VoltEdge Energy',
      supplierCount: 8,
      scenarioName: 'Cobalt Dynamics Bankruptcy',
      title: 'Battery-material disruption',
      description: 'Explore how losing a key cobalt supplier can affect battery production.',
    },
    {
      companyName: 'OrionTech Devices',
      supplierCount: 8,
      scenarioName: 'SkyNode Geopolitical Ban',
      title: 'Electronics trade restriction',
      description: 'Trace how a trade restriction can disrupt an electronics supplier network.',
    },
  ]

  useEffect(() => {
    if (selectedCompany?.name !== pendingJudgeScenario) return
    const judgeCase = judgeCases.find((item) => item.companyName === pendingJudgeScenario)
    const scenario = scenarios.find((item) => item.name === judgeCase?.scenarioName)
    if (scenario) {
      setSelectedScenarioId(scenario.id)
      setPendingJudgeScenario(null)
    }
  }, [pendingJudgeScenario, selectedCompany?.name, scenarios])

  const openJudgeCase = (companyName: string) => {
    const company = companies.find((item) => item.name === companyName)
    if (!company) {
      toast.error(`Demo dataset not found: ${companyName}`)
      return
    }
    setPendingJudgeScenario(companyName)
    setSelectedScenarioId(null)
    selectCompany(company.id)
  }

  const { data: result } = useQuery({
    queryKey: ['scenario-result', selectedScenarioId],
    queryFn: () => getScenarioResult(selectedScenarioId!),
    enabled: !!selectedScenarioId && selectedScenario?.status === 'completed',
  })

  const createMutation = useMutation({
    mutationFn: (data: Partial<Scenario>) => createScenario(data),
    onSuccess: (s) => {
      toast.success('Scenario created')
      qc.setQueryData<Scenario[]>(['scenarios', s.company_id], (current = []) => [
        s,
        ...current.filter((scenario) => scenario.id !== s.id),
      ])
      setSelectedScenarioId(s.id)
    },
    onError: () => toast.error('Could not create scenario. Please try again.'),
  })

  const runMutation = useMutation({
    mutationFn: (id: string) => runScenario(id),
    onSuccess: () => {
      toast.success('Simulation running...')
      setRunning(false)
      qc.invalidateQueries({ queryKey: ['scenarios', selectedCompany?.id] })
      qc.invalidateQueries({ queryKey: ['scenario-result', selectedScenarioId] })
    },
    onError: () => {
      toast.error('Simulation failed')
      setRunning(false)
    },
  })

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { duration_days: 30, capacity_reduction_pct: 50 },
  })

  const duration = watch('duration_days')
  const capacity = watch('capacity_reduction_pct')

  const onSubmit = async (data: FormData) => {
    if (!selectedCompany) return
    createMutation.mutate({ ...data, company_id: selectedCompany.id })
  }

  const handleRun = async () => {
    if (!selectedScenarioId) return
    setRunning(true)
    runMutation.mutate(selectedScenarioId)
  }

  const impactData = result
    ? [
        { name: 'Direct', value: result.direct_affected_count, fill: '#ef4444' },
        { name: 'Indirect', value: result.indirect_affected_count, fill: '#f59e0b' },
        { name: 'Products', value: result.affected_products_count, fill: '#8b5cf6' },
      ]
    : []

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to use the simulator.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Disruption Simulator</h1>
        <p className="text-slate-500 text-sm">Model supply chain disruptions and assess impact</p>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <section className="card space-y-3">
        <div>
          <h2 className="text-base font-semibold text-slate-100">Demo Datasets</h2>
          <p className="text-sm text-slate-500">
            Explore three prepared supplier networks, each paired with a matching disruption scenario.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {judgeCases.map((judgeCase) => (
            <button
              key={judgeCase.companyName}
              type="button"
              className={`text-left p-4 rounded-lg border transition-colors ${
                selectedCompany.name === judgeCase.companyName
                  ? 'border-navy-500 bg-navy-800/50'
                  : 'border-navy-800 hover:border-navy-700'
              }`}
              onClick={() => openJudgeCase(judgeCase.companyName)}
            >
              <span className="text-xs uppercase tracking-wide text-navy-400">
                {judgeCase.companyName}
              </span>
              <h3 className="text-slate-100 font-semibold mt-1">{judgeCase.title}</h3>
              <p className="text-slate-400 text-xs mt-2">{judgeCase.description}</p>
              <span className="inline-block text-xs text-slate-500 mt-3">
                {judgeCase.supplierCount} suppliers · Scenario: {judgeCase.scenarioName}
              </span>
            </button>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Config */}
        <div className="space-y-4">
          {/* Predefined Scenarios */}
          {scenarios.filter((s) => s.is_predefined).length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Predefined Scenarios</h3>
              <div className="space-y-2">
                {scenarios.filter((s) => s.is_predefined).map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      selectedScenarioId === s.id
                        ? 'border-navy-500 bg-navy-800/50'
                        : 'border-navy-800 hover:border-navy-700'
                    }`}
                    onClick={() => setSelectedScenarioId(s.id)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-slate-200 text-sm font-medium">{s.name}</span>
                      <StatusBadge status={s.status} />
                    </div>
                    <p className="text-slate-500 text-xs mt-1">{s.description}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {scenarios.filter((s) => !s.is_predefined).length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-3">Saved Scenarios</h3>
              <div className="space-y-2">
                {scenarios.filter((s) => !s.is_predefined).map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      selectedScenarioId === s.id
                        ? 'border-navy-500 bg-navy-800/50'
                        : 'border-navy-800 hover:border-navy-700'
                    }`}
                    onClick={() => setSelectedScenarioId(s.id)}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-slate-200 text-sm font-medium">{s.name}</span>
                      <StatusBadge status={s.status} />
                    </div>
                    {s.description && (
                      <p className="text-slate-500 text-xs mt-1">{s.description}</p>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Custom Config */}
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-300 mb-3">Custom Scenario</h3>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="label">Scenario Name</label>
                <input {...register('name')} className="input" placeholder="e.g. Taiwan Earthquake" />
                {errors.name && <p className="text-red-400 text-xs mt-1">{errors.name.message}</p>}
              </div>
              <div>
                <label className="label">Disruption Type</label>
                <select {...register('disruption_type')} className="input">
                  <option value="">Select type...</option>
                  <option value="supplier_failure">Supplier Failure</option>
                  <option value="natural_disaster">Natural Disaster</option>
                  <option value="geopolitical">Geopolitical Event</option>
                  <option value="logistics_disruption">Logistics Disruption</option>
                  <option value="cyber_attack">Cyber Attack</option>
                  <option value="pandemic">Pandemic / Health Crisis</option>
                  <option value="port_closure">Port Closure</option>
                </select>
                {errors.disruption_type && <p className="text-red-400 text-xs mt-1">{errors.disruption_type.message}</p>}
              </div>
              <div>
                <label className="label">Target Supplier (optional)</label>
                <select {...register('target_supplier_id')} className="input">
                  <option value="">All suppliers</option>
                  {suppliers.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Duration: {duration} days</label>
                <input
                  {...register('duration_days')}
                  type="range"
                  min={1}
                  max={365}
                  className="w-full accent-navy-500"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>1 day</span><span>365 days</span>
                </div>
              </div>
              <div>
                <label className="label">Capacity Reduction: {capacity}%</label>
                <input
                  {...register('capacity_reduction_pct')}
                  type="range"
                  min={0}
                  max={100}
                  className="w-full accent-red-500"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>0%</span><span>100%</span>
                </div>
              </div>
              <button
                type="submit"
                className="btn-secondary w-full"
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? 'Creating...' : 'Create Scenario'}
              </button>
            </form>
          </div>

          {selectedScenario && (
            <div className="card">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-slate-200 font-semibold">{selectedScenario.name}</p>
                  <StatusBadge status={selectedScenario.status} />
                </div>
                <button
                  className="btn-primary flex items-center gap-2"
                  onClick={handleRun}
                  disabled={running || runMutation.isPending}
                >
                  {running || runMutation.isPending ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <PlayIcon className="w-4 h-4" />
                  )}
                  Run Simulation
                </button>
              </div>
              <div className="text-xs text-slate-500 space-y-1">
                <p>Type: {selectedScenario.disruption_type}</p>
                <p>Duration: {selectedScenario.duration_days} days</p>
                <p>Capacity reduction: {selectedScenario.capacity_reduction_pct}%</p>
              </div>
            </div>
          )}
        </div>

        {/* Right: Results */}
        <div className="space-y-4">
          {!result ? (
            <div className="card flex items-center justify-center h-48">
              <div className="text-center">
                <ZapIcon className="w-10 h-10 text-navy-700 mx-auto mb-3" />
                <p className="text-slate-500 text-sm">Select a scenario and run simulation to see results</p>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3">
                <KPICard
                  title="Direct Affected"
                  value={result.direct_affected_count}
                  icon={BuildingIcon}
                  severity="critical"
                />
                <KPICard
                  title="Indirect Affected"
                  value={result.indirect_affected_count}
                  icon={BuildingIcon}
                  severity="warning"
                />
                <KPICard
                  title="Revenue Exposure"
                  value={fmtMoney(result.estimated_revenue_exposure)}
                  icon={DollarSignIcon}
                  severity="critical"
                />
                <KPICard
                  title="Recovery Days"
                  value={result.recovery_duration_days}
                  icon={ClockIcon}
                />
                <KPICard
                  title="Products at Risk"
                  value={result.affected_products_count}
                  icon={PackageIcon}
                  severity="warning"
                />
                <KPICard
                  title="Shortfall Units"
                  value={result.estimated_shortfall_units.toLocaleString()}
                  icon={PackageIcon}
                  severity="warning"
                />
              </div>

              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-4">Impact Breakdown</h3>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={impactData}>
                    <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#141540', border: '1px solid #1e2166', borderRadius: 8 }} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {impactData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="card">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Financial Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Revenue Exposure</span>
                    <span className="text-red-400 font-mono">{fmtMoney(result.estimated_revenue_exposure)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Estimated Recovery Cost</span>
                    <span className="text-amber-400 font-mono">{fmtMoney(result.estimated_cost)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Shortfall Units</span>
                    <span className="text-slate-200 font-mono">{result.estimated_shortfall_units.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Residual Risk Score</span>
                    <span className="text-slate-200 font-mono">{result.residual_risk_score}/100</span>
                  </div>
                </div>
                <button
                  className="btn-primary w-full mt-4"
                  onClick={() => {
                    if (!selectedScenario) return
                    const params = new URLSearchParams({
                      scenario_id: selectedScenario.id,
                      scenario_name: selectedScenario.name,
                    })
                    navigate(`/recovery?${params.toString()}`)
                  }}
                >
                  Create Recovery Plan
                </button>
              </div>

              <p className="text-slate-600 text-xs text-right">
                Calculated: {format(new Date(result.calculated_at), 'MMM d, HH:mm')}
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
