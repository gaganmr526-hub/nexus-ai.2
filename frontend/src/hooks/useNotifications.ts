import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getNotifications, markNotificationRead, markAllRead } from '@/api/notifications'
import toast from 'react-hot-toast'

export function useNotifications() {
  const queryClient = useQueryClient()

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: getNotifications,
    refetchInterval: 60_000,
  })

  const unreadCount = notifications.filter((n) => !n.is_read).length

  const markRead = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
    onError: () => toast.error('Could not mark notification as read. Please try again.'),
  })

  const markAllReadMutation = useMutation({
    mutationFn: markAllRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
    onError: () => toast.error('Could not mark notifications as read. Please try again.'),
  })

  return { notifications, unreadCount, isLoading, markRead, markAllRead: markAllReadMutation }
}
