import { useEffect, type ReactNode } from 'react'
import { XIcon } from 'lucide-react'

interface Props {
  isOpen: boolean
  onClose: () => void
  title: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

export default function Modal({ isOpen, onClose, title, children, size = 'md' }: Props) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  if (!isOpen) return null

  const widths = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-2xl', xl: 'max-w-4xl' }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div
        className={`relative w-full ${widths[size]} bg-navy-900 border border-navy-700 rounded-xl shadow-2xl max-h-[90vh] overflow-hidden flex flex-col`}
      >
        <div className="flex items-center justify-between p-6 border-b border-navy-800">
          <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-navy-800 rounded-lg transition-colors"
          >
            <XIcon className="w-5 h-5 text-slate-400" />
          </button>
        </div>
        <div className="overflow-y-auto flex-1 p-6">{children}</div>
      </div>
    </div>
  )
}
