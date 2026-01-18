'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface Note {
  id: number
  task_id: number
  user_id: number
  content: string
  created_at: string
  updated_at: string
}

interface NoteListProps {
  taskId: number
}

export default function NoteList({ taskId }: NoteListProps) {
  const [newNoteContent, setNewNoteContent] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')
  const queryClient = useQueryClient()

  // Fetch notes
  const { data: notes = [], isLoading } = useQuery({
    queryKey: ['notes', taskId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/notes`, {
        credentials: 'include'
      })
      if (!response.ok) throw new Error('Failed to fetch notes')
      return response.json()
    }
  })

  // Create note mutation
  const createMutation = useMutation({
    mutationFn: async (content: string) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/notes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ content })
      })
      if (!response.ok) throw new Error('Failed to create note')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes', taskId] })
      setNewNoteContent('')
    }
  })

  // Update note mutation
  const updateMutation = useMutation({
    mutationFn: async ({ id, content }: { id: number, content: string }) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/notes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ content })
      })
      if (!response.ok) throw new Error('Failed to update note')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes', taskId] })
      setEditingId(null)
      setEditContent('')
    }
  })

  // Delete note mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/notes/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      if (!response.ok) throw new Error('Failed to delete note')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes', taskId] })
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (newNoteContent.trim()) {
      createMutation.mutate(newNoteContent)
    }
  }

  const handleEdit = (note: Note) => {
    setEditingId(note.id)
    setEditContent(note.content)
  }

  const handleSaveEdit = (id: number) => {
    if (editContent.trim()) {
      updateMutation.mutate({ id, content: editContent })
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditContent('')
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block w-8 h-8 border-4 border-white border-opacity-20 border-t-white rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Add new note */}
      <form onSubmit={handleSubmit} className="mb-6">
        <textarea
          value={newNoteContent}
          onChange={(e) => setNewNoteContent(e.target.value)}
          placeholder="Write a note..."
          rows={3}
          className="w-full px-4 py-3 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
        <div className="flex justify-end mt-2">
          <motion.button
            type="submit"
            disabled={!newNoteContent.trim() || createMutation.isPending}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg disabled:opacity-50"
          >
            {createMutation.isPending ? 'Saving...' : 'Add Note'}
          </motion.button>
        </div>
      </form>

      {/* Note list */}
      <div className="space-y-3">
        <AnimatePresence>
          {notes.map((note: Note) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="p-4 bg-white bg-opacity-5 hover:bg-opacity-10 rounded-lg transition-all group"
            >
              {editingId === note.id ? (
                // Edit mode
                <div>
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 bg-white bg-opacity-10 border border-white border-opacity-20 rounded-lg text-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={() => handleSaveEdit(note.id)}
                      className="px-4 py-1 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors"
                    >
                      Save
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="px-4 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                // View mode
                <div>
                  <p className="text-white text-sm leading-relaxed mb-2 whitespace-pre-wrap">
                    {note.content}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">
                      {formatDate(note.created_at)}
                      {note.updated_at !== note.created_at && ' (edited)'}
                    </span>
                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => handleEdit(note)}
                        className="text-blue-400 hover:text-blue-300 text-xs"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteMutation.mutate(note.id)}
                        className="text-red-400 hover:text-red-300 text-xs"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {notes.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <p>No notes yet. Add one to keep track of important details!</p>
          </div>
        )}
      </div>
    </div>
  )
}
