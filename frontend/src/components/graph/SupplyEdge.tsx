import { memo } from 'react'
import { BaseEdge, EdgeLabelRenderer, getStraightPath, type EdgeProps } from 'reactflow'

interface EdgeData {
  relationship_type: string
  confidence_score?: number
  verification_status: string
  evidence_source?: string
}

const verificationColors: Record<string, string> = {
  verified: '#22c55e',
  supplier_declared: '#3b82f6',
  evidence_inference: '#f59e0b',
  unverified: '#64748b',
  unknown: '#475569',
  rejected: '#ef4444',
}

const SupplyEdge = memo(
  ({ id, sourceX, sourceY, targetX, targetY, data, selected }: EdgeProps<EdgeData>) => {
    const [edgePath, labelX, labelY] = getStraightPath({
      sourceX,
      sourceY,
      targetX,
      targetY,
    })
    const color = verificationColors[data?.verification_status ?? 'unknown'] ?? '#64748b'

    return (
      <>
        <BaseEdge
          id={id}
          path={edgePath}
          style={{
            stroke: color,
            strokeWidth: selected ? 2.5 : 1.5,
            opacity: selected ? 1 : 0.6,
          }}
        />
        {selected && data?.relationship_type && (
          <EdgeLabelRenderer>
            <div
              style={{
                transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              }}
              className="absolute pointer-events-none"
            >
              <span className="bg-navy-900 border border-navy-700 text-slate-300 text-[10px] px-1.5 py-0.5 rounded">
                {data.relationship_type}
              </span>
            </div>
          </EdgeLabelRenderer>
        )}
      </>
    )
  }
)

SupplyEdge.displayName = 'SupplyEdge'
export default SupplyEdge
