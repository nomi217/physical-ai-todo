'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getTasks } from '@/lib/api'
import TaskForm from '@/components/TaskForm'
import TaskList from '@/components/TaskList'
import FilterBar from '@/components/FilterBar'
import ThemeToggle from '@/components/ThemeToggle'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import NotificationDropdown from '@/components/NotificationDropdown'
import { Task } from '@/lib/types'
import { useI18n } from '@/contexts/I18nContext'

export default function Home() {
  const { t } = useI18n()
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [showForm, setShowForm] = useState(false)

  // Filter/Search/Sort state
  const [search, setSearch] = useState('')
  const [priority, setPriority] = useState('')
  const [completed, setCompleted] = useState('all')
  const [tags, setTags] = useState('')
  const [sortField, setSortField] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')

  // Fetch tasks using React Query with filters
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['tasks', search, priority, completed, tags, sortField, sortOrder],
    queryFn: () => getTasks({
      search: search || undefined,
      priority: (priority || undefined) as any,
      completed: completed === 'all' ? undefined : completed === 'true',
      tags: tags || undefined,
      sort: sortField as any,
      order: sortOrder as any,
    }),
    refetchOnMount: 'always',        // Always refetch when component mounts
    refetchOnWindowFocus: true,      // Refetch when browser tab/window gains focus
    staleTime: 0,                    // Consider data immediately stale
  })

  const tasks = data?.tasks || []

  const handleClearFilters = () => {
    setSearch('')
    setPriority('')
    setCompleted('all')
    setTags('')
    setSortField('created_at')
    setSortOrder('desc')
  }

  const handleSuccess = () => {
    refetch()
    setShowForm(false)
    setEditingTask(null)
  }

  const handleEdit = (task: Task) => {
    setEditingTask(task)
    setShowForm(true)
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingTask(null)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-500 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-200">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          {/* Top Navigation Bar */}
          <div className="flex items-center justify-end gap-3 mb-6">
            {/* AI Chat Button */}
            <a
              href="/chat"
              className="bg-white bg-opacity-20 hover:bg-opacity-30 backdrop-blur-md rounded-lg p-2.5 transition-all shadow-lg hover:shadow-xl"
              title="AI Chat Assistant"
            >
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
            </a>

            {/* Notification Dropdown - NO wrapper to avoid stacking context */}
            <NotificationDropdown />

            {/* Logout Button */}
            <button
              onClick={() => {
                document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
                window.location.href = '/landing';
              }}
              className="bg-white bg-opacity-20 hover:bg-opacity-30 backdrop-blur-md rounded-lg p-2.5 transition-all shadow-lg hover:shadow-xl"
              title="Logout"
            >
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>

            <LanguageSwitcher />
            <ThemeToggle />
          </div>

          {/* Title Section */}
          <div className="text-center">
            <h1 className="text-5xl font-bold text-white mb-2">
              {t('app.title')}
            </h1>
            <p className="text-white text-opacity-90">
              {t('app.subtitle')}
            </p>
          </div>
        </div>

        {/* Stats Card */}
        <div className="bg-white bg-opacity-20 backdrop-blur-lg rounded-xl p-6 mb-6 shadow-xl">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold text-white">{data?.total || 0}</div>
              <div className="text-white text-opacity-75 text-sm">{t('dashboard.stats.total')}</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">
                {tasks.filter((task) => !task.completed).length}
              </div>
              <div className="text-white text-opacity-75 text-sm">{t('dashboard.stats.active')}</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">
                {tasks.filter((task) => task.completed).length}
              </div>
              <div className="text-white text-opacity-75 text-sm">{t('dashboard.stats.completed')}</div>
            </div>
          </div>
        </div>

        {/* FilterBar */}
        <FilterBar
          search={search}
          onSearchChange={setSearch}
          priority={priority}
          onPriorityChange={setPriority}
          completed={completed}
          onCompletedChange={setCompleted}
          tags={tags}
          onTagsChange={setTags}
          sortField={sortField}
          onSortFieldChange={setSortField}
          sortOrder={sortOrder}
          onSortOrderChange={setSortOrder}
          onClearFilters={handleClearFilters}
        />

        {/* Task Form */}
        {showForm ? (
          <TaskForm
            onSuccess={handleSuccess}
            onCancel={handleCancel}
            editingTask={editingTask}
          />
        ) : (
          <button
            onClick={() => setShowForm(true)}
            className="w-full bg-white rounded-xl shadow-xl p-6 mb-6 hover:shadow-2xl transition-shadow"
          >
            <div className="flex items-center justify-center gap-2">
              <svg
                className="w-6 h-6 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              <span className="text-xl font-semibold text-gray-700">
                {t('dashboard.createTask')}
              </span>
            </div>
          </button>
        )}

        {/* Task List */}
        <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 shadow-xl">
          <h2 className="text-2xl font-bold text-white mb-4">{t('dashboard.yourTasks')}</h2>
          <TaskList
            tasks={tasks}
            isLoading={isLoading}
            onUpdate={refetch}
            onEdit={handleEdit}
          />
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-white text-opacity-75 text-sm">
          <p>
            Backend: <code className="bg-white bg-opacity-20 px-2 py-1 rounded">
              {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}
            </code>
          </p>
        </div>
      </div>
    </main>
  )
}
