# Analytics Dashboard Skill

## Purpose
Create analytics dashboard with charts, metrics, and productivity insights using recharts.

## Process

### 1. Backend Analytics Endpoint
```python
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from datetime import datetime, timedelta

@router.get("/api/v1/analytics/summary")
def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Total tasks
    total = session.execute(
        select(func.count()).select_from(Task).where(Task.user_id == current_user.id)
    ).scalar_one()

    # Completed tasks
    completed = session.execute(
        select(func.count()).select_from(Task).where(
            Task.user_id == current_user.id,
            Task.completed == True
        )
    ).scalar_one()

    # Tasks by priority
    tasks_by_priority = {}
    for priority in ['high', 'medium', 'low']:
        count = session.execute(
            select(func.count()).select_from(Task).where(
                Task.user_id == current_user.id,
                Task.priority == priority
            )
        ).scalar_one()
        tasks_by_priority[priority] = count

    # Completion rate
    completion_rate = (completed / total * 100) if total > 0 else 0

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": total - completed,
        "completion_rate": round(completion_rate, 1),
        "tasks_by_priority": tasks_by_priority,
    }
```

### 2. Frontend Dashboard Component
```tsx
'use client'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, PieChart, Pie, LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts'

export default function AnalyticsDashboard() {
  const { data } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => fetch('/api/v1/analytics/summary').then(r => r.json())
  })

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Metric Cards */}
      <MetricCard title="Total Tasks" value={data?.total_tasks} />
      <MetricCard title="Completion Rate" value={`${data?.completion_rate}%`} />

      {/* Charts */}
      <PieChart width={400} height={300}>
        <Pie data={priorityData} dataKey="value" nameKey="name" />
        <Tooltip />
      </PieChart>
    </div>
  )
}
```

## Output
Complete analytics dashboard with metrics and charts.
