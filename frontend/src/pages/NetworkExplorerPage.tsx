import { useState, useCallback, useMemo } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { useQuery } from '@tanstack/react-query'
import { SearchIcon, LayoutGridIcon, TableIcon } from 'lucide-react'
import { useCompany } from '@/hooks/useCompany'
import { getGraph } from '@/api/graph'
import SupplyNode from '@/components/graph/SupplyNode'
import SupplyEdge from '@/components/graph/SupplyEdge'
import NodeDetailPanel from '@/components/graph/NodeDetailPanel'
import DemoBanner from '@/components/DemoBanner'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorState from '@/components/ErrorState'
import DataTable from '@/components/DataTable'
import type { GraphNode, ColumnDef } from '@/types'
import RiskBadge from '@/components/RiskBadge'
import StatusBadge from '@/components/StatusBadge'

const nodeTypes = { supply: SupplyNode }
const edgeTypes = { supply: SupplyEdge }

export default function NetworkExplorerPage() {
  const { selectedCompany } = useCompany()
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [search, setSearch] = useState('')
  const [viewMode, setViewMode] = useState<'graph' | 'table'>('graph')
  const [riskFilter, setRiskFilter] = useState<string>('')

  const {
    data: graphData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['graph', selectedCompany?.id],
    queryFn: () => getGraph(selectedCompany!.id),
    enabled: !!selectedCompany,
  })

  const filteredNodes = useMemo(() => {
    if (!graphData) return []
    return graphData.nodes.filter((n) => {
      const matchSearch = !search || n.data.label.toLowerCase().includes(search.toLowerCase())
      const matchRisk = !riskFilter || n.data.criticality === riskFilter
      return matchSearch && matchRisk
    })
  }, [graphData, search, riskFilter])

  const rfNodes: Node[] = useMemo(
    () =>
      filteredNodes.map((n) => ({
        ...n,
        type: 'supply',
      })),
    [filteredNodes]
  )

  const rfEdges: Edge[] = useMemo(
    () =>
      (graphData?.edges ?? [])
        .filter(
          (e) =>
            filteredNodes.some((n) => n.id === e.source) &&
            filteredNodes.some((n) => n.id === e.target)
        )
        .map((e) => ({ ...e, type: 'supply' })),
    [graphData, filteredNodes]
  )

  const [_nodes, , onNodesChange] = useNodesState(rfNodes)
  const [_edges, , onEdgesChange] = useEdgesState(rfEdges)

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const gn = graphData?.nodes.find((n) => n.id === node.id)
      setSelectedNode(gn ?? null)
    },
    [graphData]
  )

  const tableColumns: ColumnDef<Record<string, unknown>>[] = [
    { key: 'label', header: 'Name', sortable: true, render: (v) => <span className="font-medium text-slate-200">{String(v)}</span> },
    { key: 'supplier_type', header: 'Type', sortable: true, render: (v) => <span className="capitalize">{String(v).replace(/_/g, ' ')}</span> },
    { key: 'risk_score', header: 'Risk Score', sortable: true, render: (v) => <span className="font-mono">{String(v)}</span> },
    { key: 'criticality', header: 'Criticality', render: (v) => <RiskBadge severity={String(v)} /> },
    { key: 'verification_status', header: 'Verification', render: (v) => <StatusBadge status={String(v)} /> },
    { key: 'geographic_region', header: 'Region' },
    { key: 'downstream_count', header: 'Downstream', sortable: true },
  ]

  const tableData = filteredNodes.map((n) => ({
    id: n.id,
    ...n.data,
  })) as unknown as Record<string, unknown>[]

  if (!selectedCompany) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Select a company to explore the network.</p>
      </div>
    )
  }

  if (isLoading) return <div className="flex justify-center py-24"><LoadingSpinner size="lg" /></div>
  if (error) return <ErrorState message="Failed to load graph data" onRetry={refetch} />

  return (
    <div className="space-y-4 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Network Explorer</h1>
          <p className="text-slate-500 text-sm">
            {graphData?.metadata.total_nodes ?? 0} nodes · {graphData?.metadata.total_edges ?? 0} edges
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className={`btn-secondary flex items-center gap-2 ${viewMode === 'graph' ? 'text-slate-100' : ''}`}
            onClick={() => setViewMode('graph')}
          >
            <LayoutGridIcon className="w-4 h-4" />
            Graph
          </button>
          <button
            className={`btn-secondary flex items-center gap-2 ${viewMode === 'table' ? 'text-slate-100' : ''}`}
            onClick={() => setViewMode('table')}
          >
            <TableIcon className="w-4 h-4" />
            Table
          </button>
        </div>
      </div>

      {selectedCompany.is_demo && <DemoBanner />}

      <div className="flex gap-3">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            className="input pl-9"
            placeholder="Search nodes by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input w-40"
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
        >
          <option value="">All Risk</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {viewMode === 'graph' ? (
        <div className="relative flex-1 rounded-xl border border-navy-800 overflow-hidden" style={{ minHeight: '600px' }}>
          <ReactFlow
            nodes={rfNodes}
            edges={rfEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            fitView
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#1e2166" gap={24} size={1} />
            <Controls className="!bg-navy-900 !border-navy-700" />
            <MiniMap
              style={{ backgroundColor: '#0a0b28' }}
              nodeColor={(n) => {
                const risk = (n.data as { risk_score?: number }).risk_score ?? 0
                return risk >= 80 ? '#ef4444' : risk >= 60 ? '#f59e0b' : '#22c55e'
              }}
            />
          </ReactFlow>
          {selectedNode && (
            <NodeDetailPanel node={selectedNode} onClose={() => setSelectedNode(null)} />
          )}

          <div className="absolute bottom-4 left-4 bg-navy-900/90 border border-navy-700 rounded-lg p-3 text-xs space-y-1">
            <p className="text-slate-400 font-medium mb-2">Legend</p>
            {[
              { color: 'bg-blue-600', label: 'Buyer' },
              { color: 'bg-green-600', label: 'Direct' },
              { color: 'bg-orange-600', label: 'Manufacturer' },
              { color: 'bg-yellow-600', label: 'Material' },
              { color: 'bg-red-500', label: 'High Risk (ring)' },
            ].map(({ color, label }) => (
              <div key={label} className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded ${color}`} />
                <span className="text-slate-400">{label}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card">
          <DataTable
            data={tableData}
            columns={tableColumns}
            keyField="id"
            onRowClick={(row) => {
              const gn = graphData?.nodes.find((n) => n.id === row.id)
              if (gn) setSelectedNode(gn)
            }}
          />
        </div>
      )}
    </div>
  )
}
