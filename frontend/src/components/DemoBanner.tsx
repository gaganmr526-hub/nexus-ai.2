import { AlertTriangleIcon } from 'lucide-react'

export default function DemoBanner() {
  return (
    <div className="flex items-center gap-2 bg-amber-900/30 border border-amber-600/40 text-amber-400 text-sm px-4 py-2.5 rounded-lg mb-4">
      <AlertTriangleIcon className="w-4 h-4 flex-shrink-0" />
      <span>
        <strong>SYNTHETIC DEMO DATA</strong> — All supplier names, relationships, and financial
        figures are fictional and for demonstration purposes only.
      </span>
    </div>
  )
}
