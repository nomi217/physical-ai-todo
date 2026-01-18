'use client'

import { useState, useEffect } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { Task, TaskCreate, Priority, ReminderOffset } from '@/lib/types'
import { createTask, updateTask } from '@/lib/api'
import { useI18n } from '@/contexts/I18nContext'

interface TaskFormProps {
  onSuccess: () => void
  onCancel: () => void
  editingTask?: Task | null
}

export default function TaskForm({ onSuccess, onCancel, editingTask }: TaskFormProps) {
  const { t } = useI18n()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<Priority>('medium')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [dueDate, setDueDate] = useState<Date | null>(null)
  const [reminderOffset, setReminderOffset] = useState<ReminderOffset>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (editingTask) {
      setTitle(editingTask.title)
      setDescription(editingTask.description || '')
      setPriority(editingTask.priority)
      setTags(editingTask.tags || [])
      setDueDate(editingTask.due_date ? new Date(editingTask.due_date) : null)
      setReminderOffset(editingTask.reminder_offset || null)
    }
  }, [editingTask])

  const handleAddTag = () => {
    const trimmed = tagInput.trim()
    if (trimmed && !tags.includes(trimmed)) {
      setTags([...tags, trimmed])
      setTagInput('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag))
  }

  // Calculate if reminder offset is valid based on due date
  const isOffsetValid = (offset: ReminderOffset): boolean => {
    if (!dueDate || !offset) return true

    const now = new Date()
    const offsetMs: Record<string, number> = {
      '1h': 60 * 60 * 1000,
      '1d': 24 * 60 * 60 * 1000,
      '3d': 3 * 24 * 60 * 60 * 1000,
      '5d': 5 * 24 * 60 * 60 * 1000,
      '1w': 7 * 24 * 60 * 60 * 1000,
    }

    const reminderTime = dueDate.getTime() - (offsetMs[offset] || 0)
    return reminderTime > now.getTime()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      alert(t('taskForm.titleRequired'))
      return
    }

    setIsSubmitting(true)

    try {
      if (editingTask) {
        // Update existing task
        await updateTask(editingTask.id, {
          title: title.trim(),
          description: description.trim(),
          priority,
          tags,
          completed: editingTask.completed,
          due_date: dueDate ? dueDate.toISOString() : undefined,
          reminder_offset: reminderOffset || undefined,
        })
      } else {
        // Create new task
        const taskData: TaskCreate = {
          title: title.trim(),
          description: description.trim(),
          priority,
          tags,
          due_date: dueDate ? dueDate.toISOString() : undefined,
          reminder_offset: reminderOffset || undefined,
        }
        await createTask(taskData)
      }

      // Reset form
      setTitle('')
      setDescription('')
      setPriority('medium')
      setTags([])
      setTagInput('')
      setDueDate(null)
      setReminderOffset(null)

      onSuccess()
    } catch (error) {
      console.error('Failed to save task:', error)
      alert(t('taskForm.saveFailed'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-xl p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-900">
        {editingTask ? t('taskForm.editTask') : t('taskForm.createTask')}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            {t('taskForm.title')} <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            maxLength={200}
            required
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            {t('taskForm.description')}
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
            rows={3}
            maxLength={2000}
          />
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
            {t('taskForm.priority')}
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
            <option value="low">{t('taskForm.lowPriority')}</option>
            <option value="medium">{t('taskForm.mediumPriority')}</option>
            <option value="high">{t('taskForm.highPriority')}</option>
          </select>
        </div>

        {/* Tags */}
        <div>
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
            {t('taskForm.tags')}
          </label>
          <div className="flex gap-2 mb-2">
            <input
              id="tags"
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  handleAddTag()
                }
              }}
              className="flex-grow px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            <button
              type="button"
              onClick={handleAddTag}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              {t('taskForm.addTag')}
            </button>
          </div>

          {/* Tag List */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  #{tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Due Date */}
        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
            Due Date & Time
          </label>
          <DatePicker
            selected={dueDate}
            onChange={(date) => {
              setDueDate(date)
              // Reset reminder offset if due date is cleared or changes
              if (!date || (reminderOffset && !isOffsetValid(reminderOffset))) {
                setReminderOffset(null)
              }
            }}
            showTimeSelect
            timeFormat="HH:mm"
            timeIntervals={15}
            dateFormat="MMMM d, yyyy h:mm aa"
            minDate={new Date()}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            isClearable
          />
        </div>

        {/* Reminder Offset (only visible when due date is set) */}
        {dueDate && (
          <div>
            <label htmlFor="reminderOffset" className="block text-sm font-medium text-gray-700 mb-1">
              Reminder
            </label>
            <select
              id="reminderOffset"
              value={reminderOffset || ''}
              onChange={(e) => setReminderOffset(e.target.value as ReminderOffset || null)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              <option value="">Never</option>
              <option value="1h" disabled={!isOffsetValid('1h')}>
                1 hour before {!isOffsetValid('1h') && '(too soon)'}
              </option>
              <option value="1d" disabled={!isOffsetValid('1d')}>
                1 day before {!isOffsetValid('1d') && '(too soon)'}
              </option>
              <option value="3d" disabled={!isOffsetValid('3d')}>
                3 days before {!isOffsetValid('3d') && '(too soon)'}
              </option>
              <option value="5d" disabled={!isOffsetValid('5d')}>
                5 days before {!isOffsetValid('5d') && '(too soon)'}
              </option>
              <option value="1w" disabled={!isOffsetValid('1w')}>
                1 week before {!isOffsetValid('1w') && '(too soon)'}
              </option>
            </select>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-grow px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? t('taskForm.saving') : editingTask ? t('taskForm.updateTask') : t('taskForm.createTaskButton')}
          </button>
          {editingTask && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              {t('taskForm.cancel')}
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
