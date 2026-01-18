'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import SubtaskList from './SubtaskList'
import NoteList from './NoteList'
import AttachmentList from './AttachmentList'

interface Task {
  id: number
  title: string
  description: string
  priority: string
  completed: boolean
  tags: string[]
  created_at: string
  updated_at: string
}

interface TaskDetailModalProps {
  task: Task
  isOpen: boolean
  onClose: () => void
}

export default function TaskDetailModal({ task, isOpen, onClose }: TaskDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'subtasks' | 'notes' | 'attachments'>('subtasks')
  const queryClient = useQueryClient()

  if (!isOpen) return null

  const tabs = [
    { id: 'subtasks', label: 'Subtasks', icon: '☑️' },
    { id: 'notes', label: 'Notes', icon: '📝' },
    { id: 'attachments', label: 'Attachments', icon: '📎' }
  ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-4xl max-h-[90vh] overflow-hidden backdrop-blur-xl bg-white bg-opacity-10 border border-white border-opacity-20 rounded-3xl shadow-2xl"
      >
        {/* Header */}
        <div className="p-6 border-b border-white border-opacity-20">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2">{task.title}</h2>
              {task.description && (
                <p className="text-gray-300 text-sm leading-relaxed">{task.description}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="ml-4 text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Meta info */}
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <span className={`px-3 py-1 rounded-full ${
              task.priority === 'high' ? 'bg-red-500 bg-opacity-20 text-red-300 border border-red-500' :
              task.priority === 'medium' ? 'bg-yellow-500 bg-opacity-20 text-yellow-300 border border-yellow-500' :
              'bg-green-500 bg-opacity-20 text-green-300 border border-green-500'
            }`}>
              {task.priority.toUpperCase()}
            </span>
            {task.tags.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-500 bg-opacity-20 text-blue-300 border border-blue-500 rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white border-opacity-20">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors relative ${
                activeTab === tab.id
                  ? 'text-white'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
              {activeTab === tab.id && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-600"
                />
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 280px)' }}>
          <AnimatePresence mode="wait">
            {activeTab === 'subtasks' && (
              <motion.div
                key="subtasks"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <SubtaskList taskId={task.id} />
              </motion.div>
            )}
            {activeTab === 'notes' && (
              <motion.div
                key="notes"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <NoteList taskId={task.id} />
              </motion.div>
            )}
            {activeTab === 'attachments' && (
              <motion.div
                key="attachments"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                <AttachmentList taskId={task.id} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}
