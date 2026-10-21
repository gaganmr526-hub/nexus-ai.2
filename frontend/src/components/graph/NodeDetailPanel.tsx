import { XIcon, ZapIcon, SearchIcon } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import type { GraphNode } from '@/types'
import RiskBadge from '@/components/RiskBadge'
import StatusBadge from '@/components/StatusBadge'
import clsx from 'clsx'

interface Props {
  node: GraphNode | null
  onClose: () => void
}

export default function NodeDetailPanel({ node, onClose }: Props) {
  const navigate = useNavigate()
  if (!node) return null
  const { data } = node

  return (
    <div className="absolute right-4 top-4 bottom-4 w-72 bg-navy-900 border border-navy-700 rounded-xl shadow-2xl flex flex-col z-10 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-navy-800">
        <h3 className="font-semibold text-slate-100 text-sm truncate">{data.label}</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-navy-800 rounded transition-colors flex-shrink-0"
        >
          <XIcon className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-slate-500 text-xs mb-1">Type</p>
            <p className="text-slate-200 text-sm capitalize">
              {data.supplier_type.replace(/_/g, ' ')}
            </p>
          </div>
          <div>
            <p className="text-slate-500 text-xs mb-1">Risk Score</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-navy-800 rounded-full h-1.5">
                <div
                  className={clsx(
                    'h-1.5 rounded-full',
                    data.risk_score >= 80
                      ? 'bg-red-500'
                      : data.risk_score >= 60
                        ? 'bg-amber-500'
                        : 'bg-green-500'
                  )}
                  style={{ width: `${data.risk_score}%` }}
                />
              </div>
              <span className="text-sm text-slate-200 font-mono">{data.risk_score}</span>
            </div>
          </div>
          <div>
            <p className="text-slate-500 text-xs mb-1">Criticality</p>
            <RiskBadge severity={data.criticality} />
          </div>
          <div>
            <p className="text-slate-500 text-xs mb-1">Verification</p>
            <StatusBadge status={data.verification_status} />
          </div>
        </div>

        {data.geographic_region && (
          <div>
            <p className="text-slate-500 text-xs mb-1">Region</p>
            <p className="text-slate-200 text-sm">{data.geographic_region}</p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 p-3 bg-navy-800/50 rounded-lg">
          <div className="text-center">
            <p className="text-2xl font-bold text-slate-100">{data.downstream_count}</p>
            <p className="text-slate-500 text-xs">Downstream</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-slate-100">{data.is_demo ? '⬡' : '○'}</p>
            <p className="text-slate-500 text-xs">{data.is_demo ? 'Demo' : 'Live'}</p>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-navy-800 space-y-2">
        <button
          className="btn-secondary w-full text-sm flex items-center justify-center gap-2"
          onClick={() => navigate('/dependencies')}
        >
          <SearchIcon className="w-4 h-4" />
          Find Dependencies
        </button>
        <button
          className="btn-primary w-full text-sm flex items-center justify-center gap-2"
          onClick={() => navigate('/simulator')}
        >
          <ZapIcon className="w-4 h-4" />
          Open in Simulator
        </button>
      </div>
    </div>
  )
}
