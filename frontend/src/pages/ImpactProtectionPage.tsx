import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useCompany } from '@/hooks/useCompany'
import { getMitigationOptions } from '@/api/alternatives'
import { getScenarios } from '@/api/scenarios'
import type { MitigationOption } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import { DollarSignIcon, ClockIcon, TrendingDownIcon, ShieldIcon } from 'lucide-react'

const fmtMoney = (n: number) =>
  n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(1)}M` : `$${(n / 1_000).toFixed(0)}K`

function ScoreBar({ value, max = 100, color = 'bg-navy-500' }: { value: number; max?: number; color?: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-navy-800 rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full`} style={{ width: `${(value / max) * 100}%` }} />
      </div>
      <span className="text-xs text-slate-400 w-8 text-right">{value.toFixed(0)}%</span>
    </div>
  )
}

export default function ImpactProtectionPage() {
  const { selectedCompany } = useCompany()
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null)
  const [compared, setCompared] = useState<string[]>([])

  const { data: scenarios = [] } = useQuery({
    queryKey: ['scenarios', selectedCompany?.id],
    queryFn: () => getScenarios(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const { data: options = [], isLoading } = useQuery({
    queryKey: ['mitigations', selectedScenarioId],
    queryFn: () => getMitigationOptions(selectedScenarioId!),
    enabled: !!selectedScenarioId,
  })

  const sorted = [...options].sort((a, b) => b.ranking_score - a.ranking_score)

  const toggleCompare = (id: string) => {
    setCompared((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 3 ? [...prev, id] : prev
    )
  }

  const comparedOptions = sorted.filter((o) => compared.includes(o.id))

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to view impact protection options.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Impact & Protection</h1>
        <p className="text-slate-500 text-sm">Mitigation options ranked by effectiveness and cost</p>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="flex gap-3">
        <select
          className="input w-64"
          value={selectedScenarioId ?? ''}
          onChange={(e) => setSelectedScenarioId(e.target.value || null)}
        >
          <option value="">Select a scenario...</option>
          {scenarios.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      {!selectedScenarioId ? (
        <EmptyState title="Select a scenario" description="Choose a disruption scenario to see mitigation options." />
      ) : isLoading ? (
        <div className="flex justify-center py-12"><LoadingSpinner /></div>
      ) : sorted.length === 0 ? (
        <EmptyState title="No options" description="Run the scenario first to generate mitigation options." />
      ) : (
        <>
          {compared.length >= 2 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">
                Comparison ({compared.length} options)
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-navy-800">
                      <th className="text-left py-2 text-slate-400 font-medium">Metric</th>
                      {comparedOptions.map((o) => (
                        <th key={o.id} className="text-left py-2 text-slate-300 font-medium px-3">
                          {o.option_type}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="space-y-1">
                    {[
                      { label: 'Estimated Cost', key: 'estimated_cost', fmt: fmtMoney },
                      { label: 'Time to Implement', key: 'time_to_implement_days', fmt: (v: number) => `${v} days` },
                      { label: 'Shortage Reduction', key: 'expected_shortage_reduction_pct', fmt: (v: number) => `${v}%` },
                      { label: 'Revenue Protection', key: 'expected_revenue_protection', fmt: fmtMoney },
                      { label: 'Ranking Score', key: 'ranking_score', fmt: (v: number) => v.toFixed(2) },
                    ].map(({ label, key, fmt }) => (
                      <tr key={key} className="border-b border-navy-800/40">
                        <td className="py-2 text-slate-400">{label}</td>
                        {comparedOptions.map((o) => (
                          <td key={o.id} className="py-2 px-3 text-slate-200 font-mono">
                            {fmt(o[key as keyof MitigationOption] as number)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sorted.map((option, i) => (
              <div key={option.id} className="card space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-navy-700 text-navy-300 px-2 py-0.5 rounded-full">
                        #{i + 1}
                      </span>
                      <span className="text-xs bg-navy-800 text-slate-400 px-2 py-0.5 rounded-full">
                        {option.option_type}
                      </span>
                    </div>
                    <p className="text-slate-200 font-medium text-sm">{option.description}</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={compared.includes(option.id)}
                    onChange={() => toggleCompare(option.id)}
                    className="mt-1 accent-navy-400 w-4 h-4"
                    title="Compare"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="flex items-center gap-1.5">
                    <DollarSignIcon className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-slate-400">Cost:</span>
                    <span className="text-slate-200 font-mono">{fmtMoney(option.estimated_cost)}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <ClockIcon className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-slate-400">Time:</span>
                    <span className="text-slate-200">{option.time_to_implement_days}d</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <TrendingDownIcon className="w-3.5 h-3.5 text-green-500" />
                    <span className="text-slate-400">Shortage ↓:</span>
                    <span className="text-green-400">{option.expected_shortage_reduction_pct}%</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <ShieldIcon className="w-3.5 h-3.5 text-navy-400" />
                    <span className="text-slate-400">Protects:</span>
                    <span className="text-navy-300 font-mono">{fmtMoney(option.expected_revenue_protection)}</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Ranking Score</span>
                    <span>{option.ranking_score.toFixed(2)}</span>
                  </div>
                  <ScoreBar value={option.ranking_score * 100} color="bg-navy-500" />
                </div>

                {option.operational_constraints && (
                  <p className="text-xs text-amber-400/80 bg-amber-900/20 px-2 py-1 rounded">
                    ⚠ {option.operational_constraints}
                  </p>
                )}

                <button className="btn-secondary w-full text-xs py-1.5">
                  Apply to Recovery Plan
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
