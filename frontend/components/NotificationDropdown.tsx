'use client'

import { useState, useEffect, useRef } from 'react'
import { Notification } from '@/lib/types'
import { getNotifications, getUnreadCount, markAllNotificationsAsRead } from '@/lib/api'
import NotificationItem from './NotificationItem'
import NotificationToast from './NotificationToast'

export default function NotificationDropdown() {
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [toastNotification, setToastNotification] = useState<Notification | null>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const previousCountRef = useRef<number>(0)

  // Fetch notifications and unread count
  const fetchData = async () => {
    try {
      const [notifs, countData] = await Promise.all([
        getNotifications({ limit: 20 }),
        getUnreadCount()
      ])

      // Show toast for NEW unread notifications
      if (countData.unread_count > previousCountRef.current && notifs.length > 0) {
        const newestNotification = notifs[0]
        if (!newestNotification.is_read) {
          setToastNotification(newestNotification)
        }
      }

      previousCountRef.current = countData.unread_count
      setNotifications(notifs)
      setUnreadCount(countData.unread_count)
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    }
  }

  // Poll every 60 seconds
  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [])

  // Listen for notification refresh events (triggered after task actions)
  useEffect(() => {
    const handleRefresh = () => {
      fetchData()
    }

    window.addEventListener('refreshNotifications', handleRefresh)
    return () => window.removeEventListener('refreshNotifications', handleRefresh)
  }, [])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleMarkAllAsRead = async () => {
    setIsLoading(true)
    try {
      await markAllNotificationsAsRead()
      await fetchData()
    } catch (error) {
      console.error('Failed to mark all as read:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Icon Button with glass-morphism effect */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2.5 text-white bg-white bg-opacity-20 hover:bg-opacity-30 backdrop-blur-md rounded-lg transition-all shadow-lg hover:shadow-xl focus:outline-none"
        aria-label="Notifications"
      >
        {/* Bell Icon with shake animation when there are unread notifications */}
        <svg
          className={`w-7 h-7 ${unreadCount > 0 ? 'animate-pulse' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>

        {/* Unread Badge - Facebook style (bright red, prominent) */}
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center min-w-[22px] h-[22px] px-1.5 text-xs font-bold text-white bg-red-600 rounded-full border-2 border-white shadow-lg animate-pulse">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel - SOLID WHITE, NO BLUR, positioned relative to viewport */}
      {isOpen && (
        <div
          className="fixed top-20 right-4 w-96 max-w-[calc(100vw-2rem)] rounded-xl border border-gray-300 max-h-[calc(100vh-6rem)] flex flex-col"
          style={{
            backgroundColor: '#ffffff',  // Solid white, no transparency
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',  // Strong shadow
            zIndex: 9999,  // High z-index, no parent can override
            position: 'fixed',  // Explicitly fixed to viewport
            willChange: 'auto',  // Prevent transform optimization
          }}
        >
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-white rounded-t-xl flex-shrink-0">
              <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  disabled={isLoading}
                  className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50 font-medium"
                >
                  Mark all as read
                </button>
              )}
            </div>

            {/* Notification List - Scrollable */}
            <div className="overflow-y-auto flex-1">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="text-sm">No notifications yet</p>
              </div>
            ) : (
              <div>
                {notifications.map((notification) => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onUpdate={fetchData}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t border-gray-200 text-center flex-shrink-0 rounded-b-xl bg-white">
              <button
                onClick={() => setIsOpen(false)}
                className="text-sm text-gray-600 hover:text-gray-900 font-medium"
              >
                Close
              </button>
            </div>
          )}
        </div>
      )}

      {/* Toast Popup for New Notifications */}
      {toastNotification && (
        <NotificationToast
          notification={toastNotification}
          onClose={() => setToastNotification(null)}
        />
      )}
    </div>
  )
}
