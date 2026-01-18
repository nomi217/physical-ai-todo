'use client'
import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

interface Attachment {
  id: number
  task_id: number
  user_id: number
  filename: string
  file_url: string
  file_size: number
  mime_type: string
  ocr_text: string | null
  created_at: string
}

interface AttachmentListProps {
  taskId: number
}

export default function AttachmentList({ taskId }: AttachmentListProps) {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  // Fetch attachments
  const { data: attachments = [], isLoading } = useQuery({
    queryKey: ['attachments', taskId],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/attachments`, {
        credentials: 'include'
      })
      if (!response.ok) throw new Error('Failed to fetch attachments')
      return response.json()
    }
  })

  // Upload attachment mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/attachments`, {
        method: 'POST',
        credentials: 'include',
        body: formData
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to upload file')
      }
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attachments', taskId] })
    }
  })

  // Delete attachment mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/attachments/${id}`, {
        method: 'DELETE',
        credentials: 'include'
      })
      if (!response.ok) throw new Error('Failed to delete attachment')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['attachments', taskId] })
    }
  })

  const handleFileSelect = (files: FileList | null) => {
    if (files && files.length > 0) {
      uploadMutation.mutate(files[0])
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  }

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return '🖼️'
    if (mimeType.includes('pdf')) return '📄'
    if (mimeType.includes('word') || mimeType.includes('document')) return '📝'
    if (mimeType.includes('sheet') || mimeType.includes('excel')) return '📊'
    return '📎'
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
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
      {/* Upload area */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-blue-500 bg-blue-500 bg-opacity-10'
            : 'border-white border-opacity-20 hover:border-opacity-40 bg-white bg-opacity-5'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
          accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.csv,.xlsx"
        />

        {uploadMutation.isPending ? (
          <div>
            <div className="inline-block w-12 h-12 border-4 border-white border-opacity-20 border-t-white rounded-full animate-spin mb-4" />
            <p className="text-white font-medium">Uploading...</p>
          </div>
        ) : (
          <div>
            <div className="text-6xl mb-4">📎</div>
            <p className="text-white font-medium mb-2">
              {isDragging ? 'Drop file here' : 'Click or drag files to upload'}
            </p>
            <p className="text-gray-400 text-sm">
              Supports: Images, PDFs, Documents (Max 10MB)
            </p>
          </div>
        )}

        {uploadMutation.isError && (
          <p className="text-red-400 text-sm mt-4">
            {uploadMutation.error?.message || 'Upload failed'}
          </p>
        )}
      </div>

      {/* Attachment list */}
      <div className="space-y-2">
        <AnimatePresence>
          {attachments.map((attachment: Attachment) => (
            <motion.div
              key={attachment.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="flex items-center gap-3 p-4 bg-white bg-opacity-5 hover:bg-opacity-10 rounded-lg transition-all group"
            >
              {/* Icon */}
              <div className="text-3xl flex-shrink-0">
                {getFileIcon(attachment.mime_type)}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium truncate">
                  {attachment.filename}
                </p>
                <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                  <span>{formatFileSize(attachment.file_size)}</span>
                  <span>•</span>
                  <span>{formatDate(attachment.created_at)}</span>
                </div>
                {attachment.ocr_text && (
                  <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                    OCR: {attachment.ocr_text}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 flex-shrink-0">
                <a
                  href={`http://localhost:8000${attachment.file_url}`}
                  download={attachment.filename}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-blue-400 hover:text-blue-300"
                  onClick={(e) => e.stopPropagation()}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </a>
                <button
                  onClick={() => deleteMutation.mutate(attachment.id)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-300"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {attachments.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <p>No attachments yet. Upload files to get started!</p>
          </div>
        )}
      </div>
    </div>
  )
}
