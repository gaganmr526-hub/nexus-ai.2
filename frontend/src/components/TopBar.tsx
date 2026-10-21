import { BellIcon, ChevronDownIcon, LogOutIcon, UserIcon } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/store/auth'
import { useCompany } from '@/hooks/useCompany'
import { useNotifications } from '@/hooks/useNotifications'

export default function TopBar() {
  const { user, logout } = useAuth()
  const { companies, selectedCompany, selectCompany } = useCompany()
  const { unreadCount } = useNotifications()
  const navigate = useNavigate()
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  return (
    <header className="h-16 bg-navy-950 border-b border-navy-800 flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-4">
        {companies.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-slate-500 text-sm">Company:</span>
            <select
              className="bg-navy-800 border border-navy-700 text-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-navy-400"
              value={selectedCompany?.id ?? ''}
              onChange={(e) => selectCompany(e.target.value)}
            >
              {companies.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} {c.is_demo ? '(Demo)' : ''}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          className="relative p-2 hover:bg-navy-800 rounded-lg transition-colors"
          onClick={() => navigate('/notifications')}
        >
          <BellIcon className="w-5 h-5 text-slate-400" />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-navy-400 rounded-full" />
          )}
        </button>

        <div className="relative">
          <button
            className="flex items-center gap-2 hover:bg-navy-800 rounded-lg px-3 py-2 transition-colors"
            onClick={() => setUserMenuOpen((o) => !o)}
          >
            <div className="w-7 h-7 bg-navy-700 rounded-full flex items-center justify-center">
              <UserIcon className="w-4 h-4 text-slate-300" />
            </div>
            <span className="text-sm text-slate-300 max-w-[120px] truncate">
              {user?.full_name}
            </span>
            <ChevronDownIcon className="w-4 h-4 text-slate-500" />
          </button>

          {userMenuOpen && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setUserMenuOpen(false)}
              />
              <div className="absolute right-0 top-full mt-1 w-48 bg-navy-900 border border-navy-700 rounded-xl shadow-xl z-50">
                <div className="p-3 border-b border-navy-800">
                  <p className="text-sm font-medium text-slate-200 truncate">{user?.full_name}</p>
                  <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                </div>
                <button
                  className="flex items-center gap-2 w-full px-4 py-3 text-sm text-slate-400 hover:text-red-400 hover:bg-navy-800 transition-colors rounded-b-xl"
                  onClick={() => {
                    logout()
                    navigate('/login')
                  }}
                >
                  <LogOutIcon className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
