# Test Generator Skill

## Purpose
Generate unit and integration tests for backend and frontend.

## Process

### Backend Test (pytest)
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_{resource}():
    response = client.post("/api/v1/{resources}", json={
        "title": "Test",
        "description": "Test description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"

def test_get_{resource}s():
    response = client.get("/api/v1/{resources}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Frontend Test (Jest)
```tsx
import { render, screen } from '@testing-library/react'
import Component from './Component'

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component title="Test" />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
```

## Output
Complete test files with coverage.
