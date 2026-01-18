'use client'

import { Task } from '@/lib/types'
import TaskItem from './TaskItem'
import { useI18n } from '@/contexts/I18nContext'

interface TaskListProps {
  tasks: Task[]
  isLoading: boolean
  onUpdate: () => void
  onEdit: (task: Task) => void
}

export default function TaskList({ tasks, isLoading, onUpdate, onEdit }: TaskListProps) {
  const { t } = useI18n()

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    )
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-white opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-lg font-medium text-white">{t('taskList.noTasks')}</h3>
        <p className="mt-1 text-sm text-white opacity-75">{t('taskList.noTasksDesc')}</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} onUpdate={onUpdate} onEdit={onEdit} />
      ))}
    </div>
  )
}
