'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface Subtask {
  id: number
  task_id: number
  user_id: number
  title: string
  completed: boolean
  display_order: number
  created_at: string
  updated_at: string
}

interface SubtaskListProps {
  taskId: number
}

export default function SubtaskList({ taskId }: SubtaskListProps) {
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('')
  const queryClient = useQueryClient()

  // Fetch subtasks
  const { data: subtasks = [], isLoading } = useQuery({
    queryKey: ['subtasks', taskId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/subtasks`, {
        credentials: 'include'
      })
      if (!response.ok) throw new Error('Failed to fetch subtasks')
      return response.json()
    }
  })

  // Create subtask mutation
  const createMutation = useMutation({
    mutationFn: async (title: string) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/subtasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ title })
      })
      if (!response.ok) throw new Error('Failed to create subtask')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] })
      setNewSubtaskTitle('')
    }
  })

  // Toggle subtask mutation
  const toggleMutation = useMutation({
    mutationFn: async ({ id, completed }: { id: number, completed: boolean }) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/subtasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ completed })
      })
      if (!response.ok) throw new Error('Failed to update subtask')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] })
    }
  })

  // Delete subtask mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/subtasks/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      if (!response.ok) throw new Error('Failed to delete subtask')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] })
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (newSubtaskTitle.trim()) {
      createMutation.mutate(newSubtaskTitle)
    }
  }

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block w-8 h-8 border-4 border-white border-opacity-20 border-t-white rounded-full animate-spin" />
      </div>
    )
  }

  const completedCount = subtasks.filter((s: Subtask) => s.completed).length
  const progress = subtasks.length > 0 ? (completedCount / subtasks.length) * 100 : 0

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      {subtasks.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-300">
              Progress: {completedCount} / {subtasks.length}
            </span>
            <span className="text-sm font-semibold text-white">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-white bg-opacity-10 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-purple-600"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      )}

      {/* Add new subtask */}
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newSubtaskTitle}
            onChange={(e) => setNewSubtaskTitle(e.target.value)}
            placeholder="Add a subtask..."
            className="flex-1 px-4 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <motion.button
            type="submit"
            disabled={!newSubtaskTitle.trim() || createMutation.isPending}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg disabled:opacity-50"
          >
            {createMutation.isPending ? '...' : 'Add'}
          </motion.button>
        </div>
      </form>

      {/* Subtask list */}
      <div className="space-y-2">
        <AnimatePresence>
          {subtasks.map((subtask: Subtask) => (
            <motion.div
              key={subtask.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex items-center gap-3 p-3 bg-white bg-opacity-5 hover:bg-opacity-10 rounded-lg transition-all group"
            >
              {/* Checkbox */}
              <button
                onClick={() => toggleMutation.mutate({ id: subtask.id, completed: !subtask.completed })}
                className="flex-shrink-0"
              >
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all ${
                  subtask.completed
                    ? 'bg-blue-500 border-blue-500'
                    : 'border-white border-opacity-30 hover:border-opacity-50'
                }`}>
                  {subtask.completed && (
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </button>

              {/* Title */}
              <span className={`flex-1 text-sm ${
                subtask.completed ? 'line-through text-gray-400' : 'text-white'
              }`}>
                {subtask.title}
              </span>

              {/* Delete button */}
              <button
                onClick={() => deleteMutation.mutate(subtask.id)}
                className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-300"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </motion.div>
          ))}
        </AnimatePresence>

        {subtasks.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <p>No subtasks yet. Add one to get started!</p>
          </div>
        )}
      </div>
    </div>
  )
}
