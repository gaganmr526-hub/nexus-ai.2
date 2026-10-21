import { InboxIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface Props {
  title?: string
  description?: string
  action?: ReactNode
}

export default function EmptyState({ title = 'No data', description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <InboxIcon className="w-12 h-12 text-navy-600 mb-4" />
      <h3 className="text-lg font-semibold text-slate-300 mb-2">{title}</h3>
      {description && <p className="text-slate-500 text-sm mb-4 max-w-sm">{description}</p>}
      {action}
    </div>
  )
}
