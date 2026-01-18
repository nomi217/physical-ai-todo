'use client'

import { Notification } from '@/lib/types'
import { markNotificationAsRead } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface NotificationItemProps {
  notification: Notification
  onUpdate: () => void
}

export default function NotificationItem({ notification, onUpdate }: NotificationItemProps) {
  const router = useRouter()

  const handleClick = async () => {
    try {
      // Mark as read
      if (!notification.is_read) {
        await markNotificationAsRead(notification.id)
      }

      // Navigate to task (refresh to show the task)
      router.push('/dashboard')
      onUpdate()
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div
      onClick={handleClick}
      className={`p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors ${
        !notification.is_read ? 'bg-blue-50' : ''
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Icon based on notification type */}
        <div className={`flex-shrink-0 mt-0.5 p-2 rounded-full ${
          notification.type === 'task_created' ? 'bg-green-100 text-green-600' :
          notification.type === 'task_completed' ? 'bg-blue-100 text-blue-600' :
          notification.type === 'task_updated' ? 'bg-yellow-100 text-yellow-600' :
          notification.type === 'task_deleted' ? 'bg-red-100 text-red-600' :
          notification.type === 'task_reopened' ? 'bg-purple-100 text-purple-600' :
          notification.type === 'reminder' ? 'bg-indigo-100 text-indigo-600' :
          'bg-orange-100 text-orange-600'
        }`}>
          {notification.type === 'task_created' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          )}
          {notification.type === 'task_completed' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          )}
          {notification.type === 'task_updated' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          )}
          {notification.type === 'task_deleted' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          )}
          {notification.type === 'task_reopened' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          )}
          {notification.type === 'reminder' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          )}
          {notification.type === 'overdue' && (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          )}
        </div>

        {/* Content */}
        <div className="flex-grow min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className={`text-sm font-medium ${
              !notification.is_read ? 'text-gray-900' : 'text-gray-700'
            }`}>
              {notification.title}
            </p>
            {!notification.is_read && (
              <span className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-1"></span>
            )}
          </div>
          <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
          <p className="text-xs text-gray-400 mt-1">{formatTime(notification.created_at)}</p>
        </div>
      </div>
    </div>
  )
}
