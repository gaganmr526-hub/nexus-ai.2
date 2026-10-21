import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useCompany } from '@/hooks/useCompany'
import { getFindings } from '@/api/dependencies'
import type { RiskFinding, ColumnDef } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import DataTable from '@/components/DataTable'
import RiskBadge from '@/components/RiskBadge'
import StatusBadge from '@/components/StatusBadge'
import Modal from '@/components/Modal'
import { format } from 'date-fns'
import { DownloadIcon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function RiskRegisterPage() {
  const { selectedCompany } = useCompany()
  const navigate = useNavigate()
  const [selectedFinding, setSelectedFinding] = useState<RiskFinding | null>(null)
  const [severityFilter, setSeverityFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: findings = [], isLoading } = useQuery({
    queryKey: ['findings', selectedCompany?.id],
    queryFn: () => getFindings(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const filtered = findings.filter((f) => {
    return (
      (!severityFilter || f.severity === severityFilter) &&
      (!typeFilter || f.finding_type === typeFilter) &&
      (!statusFilter || f.status === statusFilter)
    )
  })

  const columns: ColumnDef<RiskFinding>[] = [
    {
      key: 'title',
      header: 'Title',
      sortable: true,
      render: (v) => <span className="font-medium text-slate-200">{String(v)}</span>,
    },
    {
      key: 'finding_type',
      header: 'Type',
      render: (v) => (
        <span className="text-xs bg-navy-800 px-2 py-0.5 rounded-full text-slate-400">
          {String(v).replace(/_/g, ' ')}
        </span>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      sortable: true,
      render: (v) => <RiskBadge severity={String(v)} />,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (v) => <StatusBadge status={String(v)} />,
    },
    {
      key: 'confidence_score',
      header: 'Confidence',
      render: (v) => (
        <div className="flex items-center gap-2">
          <div className="w-16 bg-navy-800 rounded-full h-1">
            <div
              className="bg-navy-400 h-1 rounded-full"
              style={{ width: `${(Number(v) ?? 0) * 100}%` }}
            />
          </div>
          <span className="text-xs text-slate-500">{Math.round((Number(v) ?? 0) * 100)}%</span>
        </div>
      ),
    },
    {
      key: 'created_at',
      header: 'Date',
      sortable: true,
      render: (v) => (
        <span className="text-xs text-slate-500">{format(new Date(String(v)), 'MMM d, yyyy')}</span>
      ),
    },
  ]

  const exportCsv = () => {
    const rows = [
      ['Title', 'Type', 'Severity', 'Status', 'Confidence', 'Date'],
      ...filtered.map((f) => [
        f.title,
        f.finding_type,
        f.severity,
        f.status,
        String(Math.round((f.confidence_score ?? 0) * 100)) + '%',
        format(new Date(f.created_at), 'yyyy-MM-dd'),
      ]),
    ]
    const csv = rows.map((r) => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'risk-register.csv'
    a.click()
  }

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to view the risk register.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Risk Register</h1>
          <p className="text-slate-500 text-sm">{filtered.length} findings</p>
        </div>
        <button className="btn-secondary flex items-center gap-2" onClick={exportCsv}>
          <DownloadIcon className="w-4 h-4" /> Export CSV
        </button>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="flex gap-3">
        <select className="input w-40" value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
          <option value="">All Severity</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select className="input w-52" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="hidden_dependency">Hidden Dependency</option>
          <option value="concentration">Concentration</option>
          <option value="single_point_of_failure">Single Point of Failure</option>
          <option value="geographic_exposure">Geographic Exposure</option>
        </select>
        <select className="input w-44" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="verified">Verified</option>
          <option value="rejected">Rejected</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>

      <div className="card">
        <DataTable
          data={filtered as unknown as Record<string, unknown>[]}
          columns={columns as unknown as ColumnDef<Record<string, unknown>>[]}
          isLoading={isLoading}
          onRowClick={(row) => setSelectedFinding(row as unknown as RiskFinding)}
          keyField="id"
        />
      </div>

      <Modal
        isOpen={!!selectedFinding}
        onClose={() => setSelectedFinding(null)}
        title={selectedFinding?.title ?? ''}
        size="lg"
      >
        {selectedFinding && (
          <div className="space-y-4">
            <div className="flex gap-2 flex-wrap">
              <RiskBadge severity={selectedFinding.severity} />
              <StatusBadge status={selectedFinding.status} />
            </div>
            <p className="text-slate-400">{selectedFinding.description}</p>
            {selectedFinding.recommended_action && (
              <div className="p-3 bg-navy-800/50 rounded-lg">
                <p className="text-xs text-slate-500 mb-1">Recommended Action</p>
                <p className="text-slate-300 text-sm">{selectedFinding.recommended_action}</p>
              </div>
            )}
            <div className="flex gap-3">
              <button className="btn-primary" onClick={() => navigate('/dependencies')}>
                View in Dependencies
              </button>
              <button className="btn-secondary" onClick={() => navigate('/simulator')}>
                Simulate Impact
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
