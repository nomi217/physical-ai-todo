'use client'

import { Priority } from '@/lib/types'
import { useI18n } from '@/contexts/I18nContext'

interface FilterBarProps {
  search: string
  onSearchChange: (value: string) => void
  priority: string
  onPriorityChange: (value: string) => void
  completed: string
  onCompletedChange: (value: string) => void
  sortField: string
  onSortFieldChange: (value: string) => void
  sortOrder: string
  onSortOrderChange: (value: string) => void
  tags: string
  onTagsChange: (value: string) => void
  onClearFilters: () => void
}

export default function FilterBar({
  search,
  onSearchChange,
  priority,
  onPriorityChange,
  completed,
  onCompletedChange,
  sortField,
  onSortFieldChange,
  sortOrder,
  onSortOrderChange,
  tags,
  onTagsChange,
  onClearFilters,
}: FilterBarProps) {
  const { t } = useI18n()
  const hasActiveFilters = search || priority || completed !== 'all' || tags

  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 mb-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white">{t('filters.title')}</h3>
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="text-sm text-white bg-white bg-opacity-20 px-3 py-1 rounded-lg hover:bg-opacity-30 transition-colors"
          >
            {t('filters.clearAll')}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            {t('filters.search')}
          </label>
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-white border-opacity-20 bg-white bg-opacity-10 text-white placeholder-white placeholder-opacity-50 focus:ring-2 focus:ring-white focus:ring-opacity-50 outline-none"
          />
        </div>

        {/* Priority Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            {t('filters.priority')}
          </label>
          <select
            value={priority}
            onChange={(e) => onPriorityChange(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-white border-opacity-20 bg-white bg-opacity-10 text-white focus:ring-2 focus:ring-white focus:ring-opacity-50 outline-none"
          >
            <option value="" className="text-gray-900">{t('filters.allPriorities')}</option>
            <option value="high" className="text-gray-900">{t('filters.highPriority')}</option>
            <option value="medium" className="text-gray-900">{t('filters.mediumPriority')}</option>
            <option value="low" className="text-gray-900">{t('filters.lowPriority')}</option>
          </select>
        </div>

        {/* Completion Status */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            {t('filters.status')}
          </label>
          <select
            value={completed}
            onChange={(e) => onCompletedChange(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-white border-opacity-20 bg-white bg-opacity-10 text-white focus:ring-2 focus:ring-white focus:ring-opacity-50 outline-none"
          >
            <option value="all" className="text-gray-900">{t('filters.allTasks')}</option>
            <option value="false" className="text-gray-900">{t('filters.activeOnly')}</option>
            <option value="true" className="text-gray-900">{t('filters.completedOnly')}</option>
          </select>
        </div>

        {/* Tags Filter */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            {t('filters.tags')}
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => onTagsChange(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-white border-opacity-20 bg-white bg-opacity-10 text-white placeholder-white placeholder-opacity-50 focus:ring-2 focus:ring-white focus:ring-opacity-50 outline-none"
          />
        </div>

        {/* Sort Field */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            {t('filters.sortBy')}
          </label>
          <select
            value={sortField}
            onChange={(e) => onSortFieldChange(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-white border-opacity-20 bg-white bg-opacity-10 text-white focus:ring-2 focus:ring-white focus:ring-opacity-50 outline-none"
          >
            <option value="created_at" className="text-gray-900">{t('filters.dateCreated')}</option>
            <option value="updated_at" className="text-gray-900">{t('filters.dateUpdated')}</option>
            <option value="priority" className="text-gray-900">{t('filters.priority')}</option>
            <option value="title" className="text-gray-900">{t('filters.titleAZ')}</option>
          </select>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-white mb-1">
            {t('filters.order')}
          </label>
          <select
            value={sortOrder}
            onChange={(e) => onSortOrderChange(e.target.value)}
            className="w-full px-4 py-2 rounded-lg border border-white border-opacity-20 bg-white bg-opacity-10 text-white focus:ring-2 focus:ring-white focus:ring-opacity-50 outline-none"
          >
            <option value="desc" className="text-gray-900">{t('filters.descending')}</option>
            <option value="asc" className="text-gray-900">{t('filters.ascending')}</option>
          </select>
        </div>
      </div>
    </div>
  )
}
