import { memo } from 'react'
import { Handle, Position, type NodeProps } from 'reactflow'
import clsx from 'clsx'
import type { SupplierType, VerificationStatus } from '@/types'

interface NodeData {
  label: string
  supplier_type: SupplierType
  risk_score: number
  criticality: string
  geographic_region?: string
  verification_status: VerificationStatus
  downstream_count: number
  is_demo: boolean
}

const typeColors: Record<string, string> = {
  buyer: 'bg-blue-900 border-blue-600',
  direct: 'bg-green-900 border-green-600',
  subtier: 'bg-teal-900 border-teal-600',
  manufacturer: 'bg-orange-900 border-orange-600',
  material: 'bg-yellow-900 border-yellow-600',
  facility: 'bg-indigo-900 border-indigo-600',
  logistics: 'bg-cyan-900 border-cyan-600',
  port: 'bg-sky-900 border-sky-600',
  region: 'bg-slate-800 border-slate-600',
  product: 'bg-purple-900 border-purple-600',
  production_facility: 'bg-rose-900 border-rose-600',
}

const riskRing = (score: number) => {
  if (score >= 80) return 'ring-2 ring-red-500'
  if (score >= 60) return 'ring-2 ring-amber-500'
  if (score >= 40) return 'ring-1 ring-yellow-600'
  return ''
}

const statusDot: Record<string, string> = {
  verified: 'bg-green-400',
  supplier_declared: 'bg-blue-400',
  evidence_inference: 'bg-amber-400',
  unverified: 'bg-slate-500',
  unknown: 'bg-slate-600',
  rejected: 'bg-red-500',
}

const SupplyNode = memo(({ data, selected }: NodeProps<NodeData>) => {
  const colorClass = typeColors[data.supplier_type] ?? 'bg-navy-800 border-navy-600'
  return (
    <div
      className={clsx(
        'px-3 py-2 rounded-xl border text-xs font-medium min-w-[120px] max-w-[160px] shadow-lg',
        colorClass,
        riskRing(data.risk_score),
        selected && 'ring-2 ring-white',
        'transition-all'
      )}
    >
      <Handle type="target" position={Position.Left} className="!bg-navy-400 !w-2 !h-2" />
      <div className="flex items-start justify-between gap-1 mb-1">
        <p className="text-slate-100 font-semibold leading-tight line-clamp-2 flex-1">
          {data.label}
        </p>
        <div
          className={clsx(
            'w-2 h-2 rounded-full flex-shrink-0 mt-0.5',
            statusDot[data.verification_status] ?? 'bg-slate-500'
          )}
          title={data.verification_status}
        />
      </div>
      <p className="text-slate-400 capitalize text-[10px]">
        {data.supplier_type.replace(/_/g, ' ')}
      </p>
      <div className="flex items-center gap-1 mt-1">
        <div className="flex-1 bg-navy-950/50 rounded-full h-1">
          <div
            className={clsx(
              'h-1 rounded-full',
              data.risk_score >= 80
                ? 'bg-red-500'
                : data.risk_score >= 60
                  ? 'bg-amber-500'
                  : 'bg-green-500'
            )}
            style={{ width: `${data.risk_score}%` }}
          />
        </div>
        <span className="text-[10px] text-slate-500">{data.risk_score}</span>
      </div>
      <Handle type="source" position={Position.Right} className="!bg-navy-400 !w-2 !h-2" />
    </div>
  )
})

SupplyNode.displayName = 'SupplyNode'
export default SupplyNode
