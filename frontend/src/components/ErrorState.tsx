import { AlertTriangleIcon } from 'lucide-react'

interface Props {
  title?: string
  message?: string
  onRetry?: () => void
}

export default function ErrorState({ title = 'Something went wrong', message, onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <AlertTriangleIcon className="w-12 h-12 text-red-400 mb-4" />
      <h3 className="text-lg font-semibold text-red-300 mb-2">{title}</h3>
      {message && <p className="text-slate-500 text-sm mb-4 max-w-sm">{message}</p>}
      {onRetry && (
        <button className="btn-secondary text-sm" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}
