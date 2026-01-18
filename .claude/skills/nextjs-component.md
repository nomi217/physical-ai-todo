# Next.js Component Generator

Generate production-ready React components with TypeScript, Tailwind CSS, and shadcn/ui integration.

## Purpose

Accelerate frontend development by auto-generating type-safe, styled React components that follow best practices and integrate seamlessly with your Next.js app.

Features:
- TypeScript interfaces and props
- Tailwind CSS styling
- shadcn/ui component integration
- API integration with React Query
- Accessibility (ARIA labels, keyboard navigation)
- Responsive design
- Loading and error states

## Time Savings

**45 minutes per component** (15 components = 11 hours saved)

## Input Parameters

```bash
/skill nextjs-component --name=<ComponentName> --props=<prop1,prop2,...> --behavior=<behavior1,behavior2,...> [--shadcn=<components>]
```

### Required Parameters

- `--name`: Component name in PascalCase (e.g., `SubtaskList`, `TaskForm`, `NoteEditor`)
- `--props`: Comma-separated list of props (e.g., `taskId,subtasks`, `onSubmit,initialData`)
- `--behavior`: Component behaviors (e.g., `display,add,delete,reorder`, `edit,save,cancel`)

### Optional Parameters

- `--shadcn`: shadcn/ui components to use (e.g., `button,input,card,dialog`)
- `--api`: API endpoint to integrate (e.g., `/api/subtasks`)
- `--responsive`: Enable responsive design (default: `true`)
- `--dark-mode`: Support dark mode (default: `true`)

## Output/Deliverables

### 1. Component File

**Location**: `frontend/components/<ComponentName>.tsx`

**Contents**:
- TypeScript component with props interface
- Tailwind CSS styling
- shadcn/ui integration
- API hooks (if applicable)
- Loading/error states
- Accessibility attributes

### 2. Type Definitions

**Location**: `frontend/types/<ComponentName>.ts` (if complex types)

### 3. Storybook Story (Optional)

**Location**: `frontend/components/<ComponentName>.stories.tsx`

## Usage Examples

### Example 1: SubtaskList Component

```bash
/skill nextjs-component --name=SubtaskList --props=taskId,subtasks --behavior=display,add,delete,reorder --shadcn=button,checkbox,input --api=/api/subtasks
```

**Generates**: `frontend/components/SubtaskList.tsx`

```tsx
import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Plus, Trash2, GripVertical } from 'lucide-react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { createSubtask, deleteSubtask, updateSubtask, reorderSubtasks } from '@/lib/api';

interface Subtask {
  id: number;
  task_id: number;
  title: string;
  completed: boolean;
  display_order: number;
}

interface SubtaskListProps {
  taskId: number;
  subtasks: Subtask[];
}

function SortableSubtask({ subtask, onToggle, onDelete }: {
  subtask: Subtask;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: subtask.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-2 p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
    >
      <button
        {...attributes}
        {...listeners}
        className="cursor-grab active:cursor-grabbing text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        aria-label="Drag to reorder"
      >
        <GripVertical className="w-4 h-4" />
      </button>

      <Checkbox
        checked={subtask.completed}
        onCheckedChange={() => onToggle(subtask.id)}
        aria-label={`Mark "${subtask.title}" as ${subtask.completed ? 'incomplete' : 'complete'}`}
      />

      <span className={`flex-1 ${subtask.completed ? 'line-through text-gray-500' : 'text-gray-900 dark:text-gray-100'}`}>
        {subtask.title}
      </span>

      <Button
        variant="ghost"
        size="icon"
        onClick={() => onDelete(subtask.id)}
        className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
        aria-label={`Delete "${subtask.title}"`}
      >
        <Trash2 className="w-4 h-4" />
      </Button>
    </div>
  );
}

export function SubtaskList({ taskId, subtasks: initialSubtasks }: SubtaskListProps) {
  const [subtasks, setSubtasks] = useState(initialSubtasks);
  const [newSubtaskTitle, setNewSubtaskTitle] = useState('');
  const queryClient = useQueryClient();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const createMutation = useMutation({
    mutationFn: createSubtask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] });
      setNewSubtaskTitle('');
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, completed }: { id: number; completed: boolean }) =>
      updateSubtask(id, { completed }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteSubtask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] });
    },
  });

  const reorderMutation = useMutation({
    mutationFn: reorderSubtasks,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subtasks', taskId] });
    },
  });

  const handleAddSubtask = () => {
    if (!newSubtaskTitle.trim()) return;

    createMutation.mutate({
      task_id: taskId,
      title: newSubtaskTitle,
      completed: false,
      display_order: subtasks.length,
    });
  };

  const handleToggleSubtask = (id: number) => {
    const subtask = subtasks.find(s => s.id === id);
    if (!subtask) return;

    toggleMutation.mutate({ id, completed: !subtask.completed });
  };

  const handleDeleteSubtask = (id: number) => {
    deleteMutation.mutate(id);
  };

  const handleDragEnd = (event: any) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      setSubtasks((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        const newOrder = arrayMove(items, oldIndex, newIndex);

        // Update display_order
        const updates = newOrder.map((item, index) => ({
          id: item.id,
          display_order: index,
        }));
        reorderMutation.mutate(updates);

        return newOrder;
      });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          type="text"
          placeholder="Add a subtask..."
          value={newSubtaskTitle}
          onChange={(e) => setNewSubtaskTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddSubtask()}
          className="flex-1"
          aria-label="New subtask title"
        />
        <Button
          onClick={handleAddSubtask}
          disabled={createMutation.isPending || !newSubtaskTitle.trim()}
          aria-label="Add subtask"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add
        </Button>
      </div>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={subtasks.map(s => s.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-2">
            {subtasks.map((subtask) => (
              <SortableSubtask
                key={subtask.id}
                subtask={subtask}
                onToggle={handleToggleSubtask}
                onDelete={handleDeleteSubtask}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {subtasks.length === 0 && (
        <p className="text-center text-gray-500 dark:text-gray-400 py-8">
          No subtasks yet. Add one above to get started.
        </p>
      )}
    </div>
  );
}
```

### Example 2: TaskForm Component

```bash
/skill nextjs-component --name=TaskForm --props=initialData,onSubmit,onCancel --behavior=edit,save,cancel,validate --shadcn=button,input,textarea,select
```

**Generates**: Form component with validation and submission handling.

### Example 3: NoteEditor Component

```bash
/skill nextjs-component --name=NoteEditor --props=taskId,note --behavior=edit,save,autosave --shadcn=textarea
```

**Generates**: Auto-saving note editor with debouncing.

## Code Templates

### Base Component Template

```tsx
import React from 'react';
{{#if api}}
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { {{apiMethods}} } from '@/lib/api';
{{/if}}
{{#each shadcnComponents}}
import { {{this}} } from '@/components/ui/{{this}}';
{{/each}}

interface {{ComponentName}}Props {
  {{#each props}}
  {{this.name}}: {{this.type}};
  {{/each}}
}

export function {{ComponentName}}({ {{propNames}} }: {{ComponentName}}Props) {
  {{#if hasState}}
  const [state, setState] = useState(initialState);
  {{/if}}

  {{#if api}}
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: {{apiMethod}},
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['{{queryKey}}'] });
    },
  });
  {{/if}}

  return (
    <div className="{{baseClasses}}">
      {/* Component content */}
    </div>
  );
}
```

### Loading State Template

```tsx
if (isLoading) {
  return (
    <div className="flex items-center justify-center p-8">
      <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      <span className="ml-2 text-gray-600 dark:text-gray-400">Loading...</span>
    </div>
  );
}
```

### Error State Template

```tsx
if (error) {
  return (
    <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
      <p className="text-red-800 dark:text-red-200">
        <AlertCircle className="w-4 h-4 inline mr-2" />
        {error.message}
      </p>
    </div>
  );
}
```

## Best Practices

### 1. **Use TypeScript Interfaces**

```tsx
// Good - Explicit interface
interface TaskFormProps {
  initialData?: Task;
  onSubmit: (data: Task) => void;
  onCancel: () => void;
}

// Bad - No types
function TaskForm({ initialData, onSubmit, onCancel }) {
  ...
}
```

### 2. **Implement Accessibility**

```tsx
// Add ARIA labels
<button aria-label="Delete task">
  <Trash2 />
</button>

// Add keyboard navigation
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  ...
</div>
```

### 3. **Handle Loading and Error States**

```tsx
const { data, isLoading, error } = useQuery({ ... });

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return null;

return <ActualContent data={data} />;
```

### 4. **Use Tailwind CSS Classes Consistently**

```tsx
// Good - Consistent spacing, colors
<div className="space-y-4 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
  <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
    Title
  </h2>
</div>

// Bad - Inline styles
<div style={{ padding: '24px', backgroundColor: 'white' }}>
  ...
</div>
```

### 5. **Optimize Re-renders**

```tsx
// Use React.memo for expensive components
export const ExpensiveComponent = React.memo(({ data }) => {
  // Expensive rendering logic
  return <div>...</div>;
});

// Use useCallback for event handlers
const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies]);
```

### 6. **Implement Responsive Design**

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content adapts to screen size */}
</div>
```

## Advanced Features

### Form Validation with Zod

```tsx
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high']),
  due_date: z.string().datetime().optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

export function TaskForm({ onSubmit }: TaskFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('title')} />
      {errors.title && <p className="text-red-500">{errors.title.message}</p>}
      {/* ... */}
    </form>
  );
}
```

### Optimistic Updates

```tsx
const mutation = useMutation({
  mutationFn: updateTask,
  onMutate: async (newTask) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['tasks'] });

    // Snapshot previous value
    const previousTasks = queryClient.getQueryData(['tasks']);

    // Optimistically update
    queryClient.setQueryData(['tasks'], (old: Task[]) =>
      old.map(task => task.id === newTask.id ? newTask : task)
    );

    return { previousTasks };
  },
  onError: (err, newTask, context) => {
    // Rollback on error
    queryClient.setQueryData(['tasks'], context.previousTasks);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
  },
});
```

### Debounced Auto-save

```tsx
import { useDebouncedCallback } from 'use-debounce';

export function NoteEditor({ taskId, note }: NoteEditorProps) {
  const [content, setContent] = useState(note.content);

  const saveMutation = useMutation({
    mutationFn: updateNote,
  });

  const debouncedSave = useDebouncedCallback(
    (value: string) => {
      saveMutation.mutate({ id: note.id, content: value });
    },
    1000
  );

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    debouncedSave(e.target.value);
  };

  return (
    <div>
      <textarea value={content} onChange={handleChange} />
      {saveMutation.isPending && <span>Saving...</span>}
      {saveMutation.isSuccess && <span>Saved!</span>}
    </div>
  );
}
```

## Testing

### Component Test Template

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SubtaskList } from './SubtaskList';

const queryClient = new QueryClient();

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('SubtaskList', () => {
  it('renders subtasks', () => {
    const subtasks = [
      { id: 1, task_id: 1, title: 'Subtask 1', completed: false, display_order: 0 },
    ];

    render(<SubtaskList taskId={1} subtasks={subtasks} />, { wrapper });

    expect(screen.getByText('Subtask 1')).toBeInTheDocument();
  });

  it('adds new subtask', async () => {
    render(<SubtaskList taskId={1} subtasks={[]} />, { wrapper });

    const input = screen.getByPlaceholderText('Add a subtask...');
    const button = screen.getByLabelText('Add subtask');

    fireEvent.change(input, { target: { value: 'New subtask' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('New subtask')).toBeInTheDocument();
    });
  });
});
```

## Checklist

When generating components, ensure:

- [ ] TypeScript interfaces are defined for all props
- [ ] Tailwind CSS classes are used (no inline styles)
- [ ] Component is responsive (mobile, tablet, desktop)
- [ ] Dark mode is supported (dark: classes)
- [ ] Loading and error states are handled
- [ ] ARIA labels and keyboard navigation are implemented
- [ ] API integration uses React Query
- [ ] Event handlers use proper TypeScript types
- [ ] Component is exported as named export
- [ ] Tests are generated (if using test-generator skill)

## Related Skills

- `api-client` - Generate API functions to call from components
- `test-generator` - Generate tests for components
- `dark-mode` - Generate dark mode theme
