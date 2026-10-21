import clsx from 'clsx'
import { TrendingUpIcon, TrendingDownIcon, type LucideIcon } from 'lucide-react'

interface Props {
  title: string
  value: string | number
  subtitle?: string
  trend?: number
  icon?: LucideIcon
  onClick?: () => void
  severity?: 'normal' | 'warning' | 'critical'
}

export default function KPICard({
  title,
  value,
  subtitle,
  trend,
  icon: Icon,
  onClick,
  severity = 'normal',
}: Props) {
  const borderColor = {
    normal: 'border-navy-800',
    warning: 'border-amber-700/50',
    critical: 'border-red-700/50',
  }[severity]

  return (
    <div
      className={clsx(
        'card border',
        borderColor,
        onClick && 'cursor-pointer hover:border-navy-600 hover:bg-navy-800/50 transition-colors'
      )}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <p className="text-slate-400 text-sm font-medium">{title}</p>
        {Icon && <Icon className="w-5 h-5 text-navy-400" />}
      </div>
      <p
        className={clsx(
          'text-2xl font-bold',
          severity === 'critical'
            ? 'text-red-400'
            : severity === 'warning'
              ? 'text-amber-400'
              : 'text-slate-100'
        )}
      >
        {value}
      </p>
      {(subtitle || trend !== undefined) && (
        <div className="flex items-center gap-2 mt-2">
          {subtitle && <p className="text-slate-500 text-xs">{subtitle}</p>}
          {trend !== undefined && (
            <span
              className={clsx(
                'flex items-center gap-0.5 text-xs font-medium',
                trend >= 0 ? 'text-red-400' : 'text-green-400'
              )}
            >
              {trend >= 0 ? (
                <TrendingUpIcon className="w-3 h-3" />
              ) : (
                <TrendingDownIcon className="w-3 h-3" />
              )}
              {Math.abs(trend)}%
            </span>
          )}
        </div>
      )}
    </div>
  )
}
