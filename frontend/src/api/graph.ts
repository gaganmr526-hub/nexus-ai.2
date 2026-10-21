import { apiClient } from './client'
import type { GraphData, GraphEdge, GraphNode, SupplierType, VerificationStatus } from '@/types'

interface ApiGraphNode {
  id: string
  label?: string
  supplier_type?: SupplierType
  tier_level?: number
  risk_score?: number
  criticality?: string
  geographic_region?: string
  verification_status?: VerificationStatus
  company_id?: string
  data?: GraphNode['data']
  position?: GraphNode['position']
}

interface ApiGraphEdge {
  id: string
  source: string
  target: string
  relationship_type?: string
  confidence_score?: number
  verification_status?: VerificationStatus
  evidence_source?: string
  data?: GraphEdge['data']
}

interface ApiGraphResponse {
  nodes: ApiGraphNode[]
  edges: ApiGraphEdge[]
  metadata?: GraphData['metadata']
}

export const getGraph = async (companyId: string, params?: Record<string, string | number>) => {
  const res = await apiClient.get<ApiGraphResponse>('/graph', {
    params: { company_id: companyId, ...params },
  })
  const graph = res.data
  const downstreamCounts = new Map<string, number>()
  graph.edges.forEach((edge) => {
    downstreamCounts.set(edge.target, (downstreamCounts.get(edge.target) ?? 0) + 1)
  })

  return {
    nodes: graph.nodes.map((node, index) => ({
      id: node.id,
      data: node.data ?? {
        label: node.label ?? node.id,
        supplier_type: node.supplier_type ?? 'direct',
        risk_score: node.risk_score ?? 0,
        criticality: node.criticality ?? 'medium',
        geographic_region: node.geographic_region,
        verification_status: node.verification_status ?? 'unverified',
        downstream_count: downstreamCounts.get(node.id) ?? 0,
        is_demo: false,
      },
      position: node.position ?? {
        x: (index % 5) * 220,
        y: Math.floor(index / 5) * 120,
      },
    })),
    edges: graph.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      data: edge.data ?? {
        relationship_type: edge.relationship_type ?? 'supplies',
        confidence_score: edge.confidence_score,
        verification_status: edge.verification_status ?? 'unverified',
        evidence_source: edge.evidence_source,
      },
    })),
    metadata: graph.metadata ?? {
      total_nodes: graph.nodes.length,
      total_edges: graph.edges.length,
      company_id: companyId,
      generated_at: new Date().toISOString(),
    },
  } satisfies GraphData
}
