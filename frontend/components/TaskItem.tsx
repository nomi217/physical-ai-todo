'use client'

import { Task, Priority } from '@/lib/types'
import { toggleComplete, deleteTask } from '@/lib/api'
import { useState } from 'react'
import { useI18n } from '@/contexts/I18nContext'

interface TaskItemProps {
  task: Task
  onUpdate: () => void
  onEdit: (task: Task) => void
}

const priorityColors: Record<Priority, string> = {
  high: 'bg-red-100 text-red-800 border-red-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  low: 'bg-blue-100 text-blue-800 border-blue-300',
}

export default function TaskItem({ task, onUpdate, onEdit }: TaskItemProps) {
  const { t } = useI18n()
  const [isDeleting, setIsDeleting] = useState(false)
  const [isToggling, setIsToggling] = useState(false)

  const priorityLabels: Record<Priority, string> = {
    high: t('taskItem.high'),
    medium: t('taskItem.medium'),
    low: t('taskItem.low'),
  }

  const handleToggle = async () => {
    if (isToggling) return
    setIsToggling(true)
    try {
      await toggleComplete(task.id)
      onUpdate()
    } catch (error) {
      console.error('Failed to toggle task:', error)
      alert(t('taskItem.updateFailed'))
    } finally {
      setIsToggling(false)
    }
  }

  const handleDelete = async () => {
    if (isDeleting) return
    if (!confirm(t('taskItem.deleteConfirm'))) return

    setIsDeleting(true)
    try {
      await deleteTask(task.id)
      onUpdate()
    } catch (error) {
      console.error('Failed to delete task:', error)
      alert(t('taskItem.deleteFailed'))
    } finally {
      setIsDeleting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div
      className={`bg-white rounded-lg shadow-md p-4 transition-all duration-300 hover:shadow-lg border-l-4 ${
        task.completed ? 'border-green-500 opacity-75' : 'border-blue-500'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <button
          onClick={handleToggle}
          disabled={isToggling}
          className="flex-shrink-0 mt-1"
        >
          <div
            className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-all ${
              task.completed
                ? 'bg-green-500 border-green-500'
                : 'border-gray-300 hover:border-green-400'
            } ${isToggling ? 'opacity-50' : ''}`}
          >
            {task.completed && (
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </button>

        {/* Task Content */}
        <div className="flex-grow min-w-0">
          {/* Title and Priority */}
          <div className="flex items-start gap-2 flex-wrap mb-1">
            <h3
              className={`text-lg font-semibold ${
                task.completed ? 'line-through text-gray-500' : 'text-gray-900'
              }`}
            >
              {task.title}
            </h3>
            <span
              className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${
                priorityColors[task.priority]
              }`}
            >
              {priorityLabels[task.priority]}
            </span>
          </div>

          {/* Description */}
          {task.description && (
            <p className={`text-sm mb-2 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
              {task.description}
            </p>
          )}

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {task.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-700"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Due Date Badge and Reminder Indicator */}
          {task.due_date && (
            <div className="flex flex-wrap items-center gap-2 mb-2">
              {(() => {
                const dueDate = new Date(task.due_date)
                const now = new Date()
                const isOverdue = dueDate < now && !task.completed

                return (
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border ${
                    isOverdue
                      ? 'bg-red-100 text-red-800 border-red-300'
                      : 'bg-orange-100 text-orange-800 border-orange-300'
                  }`}>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      {isOverdue ? (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      )}
                    </svg>
                    {isOverdue ? 'Overdue' : 'Due'}: {formatDate(task.due_date)}
                  </span>
                )
              })()}
              {task.reminder_offset && (
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-300" title="Reminder set">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  {task.reminder_offset === '1h' && '1h before'}
                  {task.reminder_offset === '1d' && '1d before'}
                  {task.reminder_offset === '3d' && '3d before'}
                  {task.reminder_offset === '5d' && '5d before'}
                  {task.reminder_offset === '1w' && '1w before'}
                </span>
              )}
            </div>
          )}

          {/* Dates */}
          <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-2">
            <span title={t('taskItem.created')}>
              {t('taskItem.created')}: {formatDate(task.created_at)}
            </span>
            {task.updated_at !== task.created_at && (
              <span title={t('taskItem.updated')}>
                {t('taskItem.updated')}: {formatDate(task.updated_at)}
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => onEdit(task)}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              {t('taskItem.edit')}
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              {isDeleting ? t('taskItem.deleting') : t('taskItem.delete')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
