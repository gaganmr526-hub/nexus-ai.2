import { useState, type ReactNode } from 'react'
import { PanelLeftCloseIcon, PanelLeftOpenIcon } from 'lucide-react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function Layout({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-navy-950">
      <Sidebar collapsed={collapsed} />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
      <button
        className="fixed bottom-4 left-4 p-2 bg-navy-800 hover:bg-navy-700 border border-navy-700 rounded-lg transition-colors z-40"
        onClick={() => setCollapsed((c) => !c)}
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? (
          <PanelLeftOpenIcon className="w-4 h-4 text-slate-400" />
        ) : (
          <PanelLeftCloseIcon className="w-4 h-4 text-slate-400" />
        )}
      </button>
    </div>
  )
}
