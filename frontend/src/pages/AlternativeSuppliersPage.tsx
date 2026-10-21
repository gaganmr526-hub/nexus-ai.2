import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useCompany } from '@/hooks/useCompany'
import { getAlternativeSuppliers } from '@/api/alternatives'
import type { AlternativeSupplier } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import Modal from '@/components/Modal'
import { DownloadIcon, StarIcon } from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts'

function ScoreBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100)
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div className="bg-navy-800 rounded-full h-1.5">
        <div className="bg-navy-500 h-1.5 rounded-full" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function AlternativeSuppliersPage() {
  const { selectedCompany } = useCompany()
  const [selected, setSelected] = useState<AlternativeSupplier | null>(null)
  const [compared, setCompared] = useState<string[]>([])

  const { data: alternatives = [], isLoading } = useQuery({
    queryKey: ['alternatives', selectedCompany?.id],
    queryFn: () => getAlternativeSuppliers(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const sorted = [...alternatives].sort((a, b) => b.overall_score - a.overall_score)

  const toggleCompare = (id: string) => {
    setCompared((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : prev.length < 3 ? [...prev, id] : prev
    )
  }

  const comparedAlts = sorted.filter((a) => compared.includes(a.id))

  const radarData = (alt: AlternativeSupplier) => [
    { subject: 'Compatibility', value: alt.compatibility_score * 100 },
    { subject: 'Capacity', value: alt.capacity_score * 100 },
    { subject: 'Reliability', value: alt.reliability_score * 100 },
    { subject: 'Geo Safety', value: (1 - alt.geographic_exposure_score) * 100 },
    { subject: 'Concentration', value: (1 - alt.concentration_score) * 100 },
  ]

  const exportCsv = () => {
    const rows = [
      ['Supplier ID', 'Overall Score', 'Compatibility', 'Capacity', 'Lead Time', 'Reliability'],
      ...sorted.map((a) => [
        a.supplier_id,
        a.overall_score.toFixed(2),
        a.compatibility_score.toFixed(2),
        a.capacity_score.toFixed(2),
        String(a.lead_time_days),
        a.reliability_score.toFixed(2),
      ]),
    ]
    const csv = rows.map((r) => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'alternative-suppliers.csv'
    a.click()
  }

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to view alternatives.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Alternative Suppliers</h1>
          <p className="text-slate-500 text-sm">Ranked alternatives by overall suitability score</p>
        </div>
        <button className="btn-secondary flex items-center gap-2" onClick={exportCsv}>
          <DownloadIcon className="w-4 h-4" /> Export CSV
        </button>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      {compared.length >= 2 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Comparison ({compared.length})</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {comparedAlts.map((alt) => (
              <div key={alt.id} className="space-y-2">
                <p className="text-slate-200 text-sm font-medium">
                  {alt.supplier_name ?? alt.supplier_id.slice(0, 8) + '…'}
                </p>
                <p className="text-navy-400 font-bold text-xl">{(alt.overall_score * 100).toFixed(0)}</p>
                <ResponsiveContainer width="100%" height={120}>
                  <RadarChart data={radarData(alt)}>
                    <PolarGrid stroke="#1e2166" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 9 }} />
                    <Radar dataKey="value" fill="#4f5de8" fillOpacity={0.4} stroke="#4f5de8" />
                    <Tooltip contentStyle={{ backgroundColor: '#141540', border: '1px solid #1e2166', borderRadius: 8 }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            ))}
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12"><LoadingSpinner /></div>
      ) : sorted.length === 0 ? (
        <EmptyState title="No alternatives found" description="No alternative suppliers have been identified for this company." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sorted.map((alt, i) => (
            <div
              key={alt.id}
              className="card cursor-pointer hover:border-navy-700 transition-colors space-y-3"
              onClick={() => setSelected(alt)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs bg-navy-700 text-navy-300 px-2 py-0.5 rounded-full">#{i + 1}</span>
                    {alt.quality_cert && (
                      <span className="text-xs bg-green-900/30 text-green-400 border border-green-700/30 px-2 py-0.5 rounded-full">
                        {alt.quality_cert}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-200 font-medium">
                    {alt.supplier_name ?? `Supplier ${alt.supplier_id.slice(0, 8)}`}
                  </p>
                  <p className="text-slate-500 text-xs">Lead time: {alt.lead_time_days} days</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-navy-400">
                    {(alt.overall_score * 100).toFixed(0)}
                  </p>
                  <p className="text-xs text-slate-500">score</p>
                </div>
              </div>

              <div className="space-y-1.5">
                <ScoreBar label="Compatibility" value={alt.compatibility_score} />
                <ScoreBar label="Capacity" value={alt.capacity_score} />
                <ScoreBar label="Reliability" value={alt.reliability_score} />
              </div>

              <div className="flex gap-2">
                <input
                  type="checkbox"
                  checked={compared.includes(alt.id)}
                  onChange={(e) => { e.stopPropagation(); toggleCompare(alt.id) }}
                  className="accent-navy-400"
                  title="Compare"
                />
                <span className="text-xs text-slate-500">Compare</span>
                <div className="flex-1" />
                <button
                  className="text-xs text-navy-400 hover:text-navy-300"
                  onClick={(e) => { e.stopPropagation(); /* save shortlist */ }}
                >
                  <StarIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        isOpen={!!selected}
        onClose={() => setSelected(null)}
        title={`Alternative Supplier Details`}
        size="md"
      >
        {selected && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="label">Overall Score</p>
                <p className="text-2xl font-bold text-navy-400">{(selected.overall_score * 100).toFixed(0)}</p>
              </div>
              <div>
                <p className="label">Lead Time</p>
                <p className="text-slate-200">{selected.lead_time_days} days</p>
              </div>
              <div>
                <p className="label">Switching Cost</p>
                <p className="text-slate-200">
                  {selected.switching_cost_estimate
                    ? `$${(selected.switching_cost_estimate / 1000).toFixed(0)}K`
                    : 'N/A'}
                </p>
              </div>
              <div>
                <p className="label">Quality Cert</p>
                <p className="text-slate-200">{selected.quality_cert ?? 'None'}</p>
              </div>
            </div>

            <div className="space-y-2">
              <ScoreBar label="Compatibility" value={selected.compatibility_score} />
              <ScoreBar label="Capacity" value={selected.capacity_score} />
              <ScoreBar label="Reliability" value={selected.reliability_score} />
              <ScoreBar label="Geo Safety" value={1 - selected.geographic_exposure_score} />
            </div>

            {selected.notes && (
              <div className="p-3 bg-navy-800/50 rounded-lg">
                <p className="text-xs text-slate-500 mb-1">Notes</p>
                <p className="text-slate-300 text-sm">{selected.notes}</p>
              </div>
            )}

            <div className="flex gap-3">
              <button className="btn-primary flex-1">Request Quotation (Demo)</button>
              <button className="btn-secondary">Save to Shortlist</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
