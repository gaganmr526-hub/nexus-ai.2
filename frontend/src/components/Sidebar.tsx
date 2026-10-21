import { NavLink } from 'react-router-dom'
import {
  LayoutDashboardIcon,
  NetworkIcon,
  SearchIcon,
  ZapIcon,
  AlertTriangleIcon,
  ShieldIcon,
  RefreshCwIcon,
  ShoppingCartIcon,
  FileTextIcon,
  PackageIcon,
  UploadIcon,
  BarChart2Icon,
  BellIcon,
  SettingsIcon,
} from 'lucide-react'
import clsx from 'clsx'
import { useNotifications } from '@/hooks/useNotifications'
import { useQuery } from '@tanstack/react-query'
import { getFindings } from '@/api/dependencies'
import { useCompany } from '@/hooks/useCompany'

interface NavItem {
  to: string
  label: string
  icon: React.ElementType
  badge?: number
}

interface Props {
  collapsed: boolean
}

export default function Sidebar({ collapsed }: Props) {
  const { notifications } = useNotifications()
  const unreadCount = notifications.filter((n) => !n.is_read).length
  const { selectedCompany } = useCompany()

  const { data: findings = [] } = useQuery({
    queryKey: ['findings-open', selectedCompany?.id],
    queryFn: () => getFindings(selectedCompany!.id, { status: 'open' }),
    enabled: !!selectedCompany,
  })

  const navItems: NavItem[] = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboardIcon },
    { to: '/network', label: 'Network Explorer', icon: NetworkIcon },
    {
      to: '/dependencies',
      label: 'Hidden Dependencies',
      icon: SearchIcon,
      badge: findings.length || undefined,
    },
    { to: '/simulator', label: 'Disruption Simulator', icon: ZapIcon },
    { to: '/risks', label: 'Risk Register', icon: AlertTriangleIcon },
    { to: '/impact', label: 'Impact & Protection', icon: ShieldIcon },
    { to: '/alternatives', label: 'Alt. Suppliers', icon: RefreshCwIcon },
    { to: '/procurement', label: 'Procurement', icon: ShoppingCartIcon },
    { to: '/recovery', label: 'Recovery Planner', icon: FileTextIcon },
    { to: '/orders', label: 'Purchase Orders', icon: PackageIcon },
    { to: '/import', label: 'Data Import', icon: UploadIcon },
    { to: '/reports', label: 'Reports', icon: BarChart2Icon },
    {
      to: '/notifications',
      label: 'Notifications',
      icon: BellIcon,
      badge: unreadCount || undefined,
    },
    { to: '/admin', label: 'Administration', icon: SettingsIcon },
  ]

  return (
    <aside
      className={clsx(
        'h-full bg-navy-950 border-r border-navy-800 flex flex-col transition-all duration-300 flex-shrink-0',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      <div className="p-4 border-b border-navy-800 flex items-center gap-3">
        <div className="w-8 h-8 bg-navy-500 rounded-lg flex items-center justify-center flex-shrink-0">
          <NetworkIcon className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <div>
            <p className="font-bold text-sm text-slate-100 leading-none">NEXUSTRACE</p>
            <p className="text-xs text-navy-400">AI Platform</p>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors relative group',
                isActive
                  ? 'bg-navy-800 text-slate-100 font-medium'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-navy-900'
              )
            }
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {!collapsed && <span className="flex-1 truncate">{item.label}</span>}
            {!collapsed && item.badge !== undefined && item.badge > 0 && (
              <span className="bg-navy-500 text-white text-xs font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center">
                {item.badge > 99 ? '99+' : item.badge}
              </span>
            )}
            {collapsed && item.badge !== undefined && item.badge > 0 && (
              <span className="absolute top-1 right-1 w-2 h-2 bg-navy-400 rounded-full" />
            )}
            {collapsed && (
              <div className="absolute left-full ml-2 px-2 py-1 bg-navy-800 border border-navy-700 rounded text-xs text-slate-200 whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50">
                {item.label}
              </div>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
