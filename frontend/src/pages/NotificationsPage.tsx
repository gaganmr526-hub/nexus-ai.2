import { useNotifications } from '@/hooks/useNotifications'
import { format } from 'date-fns'
import LoadingSpinner from '@/components/LoadingSpinner'
import EmptyState from '@/components/EmptyState'
import clsx from 'clsx'
import { CheckCheckIcon, AlertCircleIcon, InfoIcon, CheckCircleIcon } from 'lucide-react'
import { useState } from 'react'
import type { Notification } from '@/types'
import Modal from '@/components/Modal'
import { isValid } from 'date-fns'

const notificationDate = (value: string) => {
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
  const date = new Date(hasTimezone ? value : `${value}Z`)
  return isValid(date) ? date : null
}

const formatNotificationDate = (value: string, pattern: string) => {
  const date = notificationDate(value)
  return date ? format(date, pattern) : 'Date unavailable'
}

const typeIcon = (type: string) => {
  if (type.includes('alert') || type.includes('warning')) return AlertCircleIcon
  if (type.includes('success')) return CheckCircleIcon
  return InfoIcon
}

const typeColor = (type: string) => {
  if (type.includes('alert') || type.includes('warning')) return 'text-amber-400'
  if (type.includes('success')) return 'text-green-400'
  return 'text-blue-400'
}

export default function NotificationsPage() {
  const { notifications, isLoading, markRead, markAllRead } = useNotifications()
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null)

  const filtered = notifications.filter((n) => filter === 'all' || !n.is_read)
  const unreadCount = notifications.filter((n) => !n.is_read).length

  const openNotification = (notification: Notification) => {
    setSelectedNotification(notification)
    if (!notification.is_read) markRead.mutate(notification.id)
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Notifications</h1>
          <p className="text-slate-500 text-sm">{unreadCount} unread</p>
        </div>
        {unreadCount > 0 && (
          <button
            className="btn-secondary flex items-center gap-2 text-sm"
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
          >
            <CheckCheckIcon className="w-4 h-4" /> Mark All Read
          </button>
        )}
      </div>

      <div className="flex gap-1 border-b border-navy-800">
        {(['all', 'unread'] as const).map((f) => (
          <button
            key={f}
            className={`px-4 py-2 text-sm font-medium transition-colors capitalize border-b-2 -mb-px ${
              filter === f
                ? 'border-navy-400 text-slate-100'
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
            onClick={() => setFilter(f)}
          >
            {f} {f === 'unread' && unreadCount > 0 && `(${unreadCount})`}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><LoadingSpinner /></div>
      ) : filtered.length === 0 ? (
        <EmptyState
          title="No notifications"
          description={filter === 'unread' ? 'All caught up!' : 'No notifications yet.'}
        />
      ) : (
        <div className="space-y-2">
          {filtered.map((notif: Notification) => {
            const Icon = typeIcon(notif.notification_type)
            const color = typeColor(notif.notification_type)
            return (
              <button
                type="button"
                key={notif.id}
                className={clsx(
                  'w-full text-left flex items-start gap-4 p-4 rounded-xl border transition-colors cursor-pointer',
                  notif.is_read
                    ? 'border-navy-800 bg-navy-900'
                    : 'border-navy-700 bg-navy-800/50 hover:bg-navy-800'
                )}
                onClick={() => openNotification(notif)}
              >
                <div className={clsx('mt-0.5 flex-shrink-0', color)}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <p
                      className={clsx(
                        'text-sm font-medium',
                        notif.is_read ? 'text-slate-400' : 'text-slate-100'
                      )}
                    >
                      {notif.title}
                    </p>
                    <p className="text-xs text-slate-600 flex-shrink-0">
                      {formatNotificationDate(notif.created_at, 'MMM d, yyyy, HH:mm')}
                    </p>
                  </div>
                  <p className="text-slate-500 text-sm mt-0.5">{notif.message}</p>
                  {notif.related_entity_type && (
                    <p className="text-xs text-navy-400 mt-1">
                      {notif.related_entity_type}: {notif.related_entity_id}
                    </p>
                  )}
                </div>
                {!notif.is_read && (
                  <div className="w-2 h-2 bg-navy-400 rounded-full mt-2 flex-shrink-0" />
                )}
              </button>
            )
          })}
        </div>
      )}

      <Modal
        isOpen={!!selectedNotification}
        onClose={() => setSelectedNotification(null)}
        title={selectedNotification?.title ?? 'Notification'}
        size="md"
      >
        {selectedNotification && (
          <div className="space-y-4">
            <p className="text-slate-300">{selectedNotification.message || 'No additional details.'}</p>
            <div className="text-sm text-slate-400 space-y-2">
              <p>
                <span className="text-slate-500">Type:</span>{' '}
                {selectedNotification.notification_type || 'Notification'}
              </p>
              <p>
                <span className="text-slate-500">Date and time:</span>{' '}
                {formatNotificationDate(selectedNotification.created_at, 'MMMM d, yyyy, HH:mm')}
              </p>
              {selectedNotification.related_entity_type && (
                <p className="break-all">
                  <span className="text-slate-500">Related to:</span>{' '}
                  {selectedNotification.related_entity_type}
                  {selectedNotification.related_entity_id
                    ? ` (${selectedNotification.related_entity_id})`
                    : ''}
                </p>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
