import clsx from 'clsx'
import type { RiskSeverity } from '@/types'

interface Props {
  severity: RiskSeverity | string
  className?: string
}

const configs: Record<string, { label: string; className: string }> = {
  low: { label: 'Low', className: 'bg-green-900/40 text-green-400 border-green-700/50' },
  medium: { label: 'Medium', className: 'bg-amber-900/40 text-amber-400 border-amber-700/50' },
  high: { label: 'High', className: 'bg-red-900/40 text-red-400 border-red-700/50' },
  critical: { label: 'Critical', className: 'bg-purple-900/40 text-purple-400 border-purple-700/50' },
}

export default function RiskBadge({ severity, className }: Props) {
  const cfg = configs[severity] ?? configs.low
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border',
        cfg.className,
        className
      )}
    >
      {cfg.label}
    </span>
  )
}
