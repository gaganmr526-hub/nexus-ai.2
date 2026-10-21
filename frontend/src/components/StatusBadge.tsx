import clsx from 'clsx'

interface Props {
  status: string
  className?: string
}

const configs: Record<string, string> = {
  open: 'bg-blue-900/40 text-blue-400 border-blue-700/50',
  investigating: 'bg-amber-900/40 text-amber-400 border-amber-700/50',
  verified: 'bg-green-900/40 text-green-400 border-green-700/50',
  rejected: 'bg-slate-700/40 text-slate-400 border-slate-600/50',
  resolved: 'bg-teal-900/40 text-teal-400 border-teal-700/50',
  draft: 'bg-slate-700/40 text-slate-400 border-slate-600/50',
  pending: 'bg-amber-900/40 text-amber-400 border-amber-700/50',
  pending_approval: 'bg-amber-900/40 text-amber-400 border-amber-700/50',
  approved: 'bg-green-900/40 text-green-400 border-green-700/50',
  active: 'bg-blue-900/40 text-blue-400 border-blue-700/50',
  completed: 'bg-teal-900/40 text-teal-400 border-teal-700/50',
  failed: 'bg-red-900/40 text-red-400 border-red-700/50',
  running: 'bg-navy-600/40 text-navy-300 border-navy-500/50',
  issued: 'bg-indigo-900/40 text-indigo-400 border-indigo-700/50',
  received: 'bg-teal-900/40 text-teal-400 border-teal-700/50',
  cancelled: 'bg-slate-700/40 text-slate-400 border-slate-600/50',
  validating: 'bg-amber-900/40 text-amber-400 border-amber-700/50',
  preview: 'bg-blue-900/40 text-blue-400 border-blue-700/50',
  confirmed: 'bg-green-900/40 text-green-400 border-green-700/50',
  importing: 'bg-navy-600/40 text-navy-300 border-navy-500/50',
}

export default function StatusBadge({ status, className }: Props) {
  const cls = configs[status] ?? 'bg-slate-700/40 text-slate-400 border-slate-600/50'
  const label = status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border',
        cls,
        className
      )}
    >
      {label}
    </span>
  )
}
