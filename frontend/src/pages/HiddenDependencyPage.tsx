import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { SearchIcon, ZapIcon, CheckIcon, XIcon, AlertCircleIcon, ChevronDownIcon, ChevronRightIcon } from 'lucide-react'
import { useCompany } from '@/hooks/useCompany'
import { getFindings, analyzeHiddenDependencies, updateFindingStatus } from '@/api/dependencies'
import type { RiskFinding } from '@/types'
import DemoBanner from '@/components/DemoBanner'
import RiskBadge from '@/components/RiskBadge'
import StatusBadge from '@/components/StatusBadge'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorState from '@/components/ErrorState'
import EmptyState from '@/components/EmptyState'
import Modal from '@/components/Modal'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { format } from 'date-fns'

const TYPE_LABELS: Record<string, string> = {
  hidden_dependency: 'Hidden Dependency',
  concentration: 'Concentration Risk',
  single_point_of_failure: 'Single Point of Failure',
  geographic_exposure: 'Geographic Exposure',
}

export default function HiddenDependencyPage() {
  const { selectedCompany } = useCompany()
  const navigate = useNavigate()
  const qc = useQueryClient()

  const [statusFilter, setStatusFilter] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [selectedFinding, setSelectedFinding] = useState<RiskFinding | null>(null)
  const [expandedPaths, setExpandedPaths] = useState<string | null>(null)

  const {
    data: findings = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['findings', selectedCompany?.id, statusFilter, severityFilter],
    queryFn: () =>
      getFindings(selectedCompany!.id, {
        ...(statusFilter ? { status: statusFilter } : {}),
        ...(severityFilter ? { severity: severityFilter } : {}),
      }),
    enabled: !!selectedCompany,
  })

  const analyzeMutation = useMutation({
    mutationFn: () => analyzeHiddenDependencies(selectedCompany!.id),
    onSuccess: (data) => {
      toast.success(`Analysis complete: ${data.length} findings`)
      qc.invalidateQueries({ queryKey: ['findings', selectedCompany?.id] })
    },
    onError: () => toast.error('Analysis failed'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status, notes }: { id: string; status: RiskFinding['status']; notes?: string }) =>
      updateFindingStatus(id, status, notes),
    onSuccess: () => {
      toast.success('Status updated')
      qc.invalidateQueries({ queryKey: ['findings', selectedCompany?.id] })
      setSelectedFinding(null)
    },
    onError: () => toast.error('Failed to update status'),
  })

  const severityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }
  const sorted = [...findings].sort(
    (a, b) => (severityOrder[a.severity] ?? 9) - (severityOrder[b.severity] ?? 9)
  )

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to view findings.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Hidden Dependencies</h1>
          <p className="text-slate-500 text-sm">AI-detected shared upstream risks</p>
        </div>
        <button
          className="btn-primary flex items-center gap-2"
          onClick={() => analyzeMutation.mutate()}
          disabled={analyzeMutation.isPending}
        >
          <SearchIcon className="w-4 h-4" />
          {analyzeMutation.isPending ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      {/* Helios Demo Callout */}
      {selectedCompany.is_demo && (
        <div className="card border-purple-700/50 bg-purple-900/10">
          <div className="flex items-start gap-3">
            <AlertCircleIcon className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-purple-300 font-semibold">Critical Finding: Helios Semiconductor Works</p>
              <p className="text-slate-400 text-sm mt-1">
                3 of your direct suppliers (TechComp Solutions, ElectroBase Corp, and Quantum Parts Ltd)
                all depend on the same upstream semiconductor manufacturer — <strong className="text-slate-300">Helios Semiconductor Works</strong>. 
                A disruption at Helios would affect 78% of your component supply chain simultaneously.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-3">
        <select
          className="input w-40"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="verified">Verified</option>
          <option value="rejected">Rejected</option>
          <option value="resolved">Resolved</option>
        </select>
        <select
          className="input w-40"
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
        >
          <option value="">All Severity</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <div className="flex-1" />
        <span className="text-slate-500 text-sm self-center">{sorted.length} findings</span>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><LoadingSpinner /></div>
      ) : error ? (
        <ErrorState message="Failed to load findings" onRetry={refetch} />
      ) : sorted.length === 0 ? (
        <EmptyState
          title="No findings"
          description="Run the analysis to detect hidden dependencies."
          action={
            <button className="btn-primary" onClick={() => analyzeMutation.mutate()}>
              Run Analysis
            </button>
          }
        />
      ) : (
        <div className="space-y-3">
          {sorted.map((finding) => (
            <div
              key={finding.id}
              className="card cursor-pointer hover:border-navy-700 transition-colors"
              onClick={() => setSelectedFinding(finding)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <RiskBadge severity={finding.severity} />
                    <StatusBadge status={finding.status} />
                    <span className="text-xs text-slate-500 bg-navy-800 px-2 py-0.5 rounded-full">
                      {TYPE_LABELS[finding.finding_type] ?? finding.finding_type}
                    </span>
                    {finding.confidence_score !== undefined && (
                      <span className="text-xs text-slate-500">
                        {Math.round(finding.confidence_score * 100)}% confidence
                      </span>
                    )}
                  </div>
                  <h3 className="text-slate-100 font-semibold mb-1">{finding.title}</h3>
                  <p className="text-slate-400 text-sm line-clamp-2">{finding.description}</p>

                  {finding.affected_suppliers_json && finding.affected_suppliers_json.length > 0 && (
                    <p className="text-slate-500 text-xs mt-2">
                      Affected: {finding.affected_suppliers_json.map((s) => s.name).join(', ')}
                    </p>
                  )}
                </div>

                <div className="flex flex-col gap-2 flex-shrink-0">
                  <button
                    className="btn-secondary text-xs py-1 px-3 flex items-center gap-1"
                    onClick={(e) => {
                      e.stopPropagation()
                      updateMutation.mutate({ id: finding.id, status: 'investigating' })
                    }}
                  >
                    <AlertCircleIcon className="w-3 h-3" /> Investigate
                  </button>
                  <button
                    className="btn-secondary text-xs py-1 px-3 flex items-center gap-1"
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate('/simulator')
                    }}
                  >
                    <ZapIcon className="w-3 h-3" /> Simulate
                  </button>
                  <button
                    className="text-xs text-green-400 hover:text-green-300 px-3 py-1 flex items-center gap-1"
                    onClick={(e) => {
                      e.stopPropagation()
                      updateMutation.mutate({ id: finding.id, status: 'verified' })
                    }}
                  >
                    <CheckIcon className="w-3 h-3" /> Verify
                  </button>
                  <button
                    className="text-xs text-slate-500 hover:text-slate-400 px-3 py-1 flex items-center gap-1"
                    onClick={(e) => {
                      e.stopPropagation()
                      updateMutation.mutate({ id: finding.id, status: 'rejected' })
                    }}
                  >
                    <XIcon className="w-3 h-3" /> Reject
                  </button>
                </div>
              </div>

              {finding.confidence_score !== undefined && (
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-xs text-slate-500 w-20">Confidence</span>
                  <div className="flex-1 bg-navy-800 rounded-full h-1.5">
                    <div
                      className="bg-navy-400 h-1.5 rounded-full"
                      style={{ width: `${(finding.confidence_score ?? 0) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-400 w-10 text-right">
                    {Math.round((finding.confidence_score ?? 0) * 100)}%
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      <Modal
        isOpen={!!selectedFinding}
        onClose={() => setSelectedFinding(null)}
        title={selectedFinding?.title ?? ''}
        size="lg"
      >
        {selectedFinding && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 flex-wrap">
              <RiskBadge severity={selectedFinding.severity} />
              <StatusBadge status={selectedFinding.status} />
              <span className="text-xs text-slate-500">
                {TYPE_LABELS[selectedFinding.finding_type]}
              </span>
            </div>

            <p className="text-slate-400">{selectedFinding.description}</p>

            {selectedFinding.recommended_action && (
              <div className="p-3 bg-navy-800/50 rounded-lg">
                <p className="text-xs text-slate-500 mb-1">Recommended Action</p>
                <p className="text-slate-300 text-sm">{selectedFinding.recommended_action}</p>
              </div>
            )}

            {selectedFinding.dependency_paths_json && selectedFinding.dependency_paths_json.length > 0 && (
              <div>
                <button
                  className="flex items-center gap-2 text-sm text-slate-300 font-medium mb-2"
                  onClick={() =>
                    setExpandedPaths(expandedPaths === selectedFinding.id ? null : selectedFinding.id)
                  }
                >
                  {expandedPaths === selectedFinding.id ? (
                    <ChevronDownIcon className="w-4 h-4" />
                  ) : (
                    <ChevronRightIcon className="w-4 h-4" />
                  )}
                  Dependency Paths ({selectedFinding.dependency_paths_json.length})
                </button>
                {expandedPaths === selectedFinding.id && (
                  <div className="space-y-2">
                    {selectedFinding.dependency_paths_json.map((path, i) => (
                      <div key={i} className="text-xs text-slate-400 bg-navy-800/50 p-2 rounded font-mono">
                        {Array.isArray(path.path) ? path.path.join(' → ') : JSON.stringify(path)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {selectedFinding.evidence_json && selectedFinding.evidence_json.length > 0 && (
              <div>
                <p className="text-sm text-slate-300 font-medium mb-2">Evidence</p>
                <div className="space-y-2">
                  {selectedFinding.evidence_json.map((ev, i) => (
                    <div key={i} className="text-xs text-slate-400 bg-navy-800/50 p-2 rounded">
                      {ev.description ?? JSON.stringify(ev)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <p className="text-slate-600 text-xs">
              Created: {format(new Date(selectedFinding.created_at), 'MMM d, yyyy HH:mm')}
            </p>

            <div className="flex gap-3 pt-2">
              <button
                className="btn-primary flex items-center gap-2"
                onClick={() => updateMutation.mutate({ id: selectedFinding.id, status: 'verified' })}
                disabled={updateMutation.isPending}
              >
                <CheckIcon className="w-4 h-4" /> Verify
              </button>
              <button
                className="btn-secondary flex items-center gap-2"
                onClick={() =>
                  updateMutation.mutate({ id: selectedFinding.id, status: 'investigating' })
                }
                disabled={updateMutation.isPending}
              >
                Investigate
              </button>
              <button
                className="btn-secondary flex items-center gap-2"
                onClick={() => navigate('/simulator')}
              >
                <ZapIcon className="w-4 h-4" /> Open in Simulator
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
