# Feature Specification: Authentication & Marketing Landing Page

**Feature Branch**: `001-003-auth-landing`
**Created**: 2025-12-09
**Priority**: P1 (User Request)
**Status**: Draft
**Input**: "Landing page with auth sign in/sign up, marketing features, 3D effects"

## User Scenarios & Testing

### User Story 1 - Marketing Landing Page (Priority: P1)

As a visitor, I want to see an attractive landing page that showcases the app's features with 3D effects, so I can understand the value proposition before signing up.

**Why this priority**: First impression is critical for user acquisition. Must be visually stunning with 3D effects.

**Independent Test**: Can view landing page with smooth 3D animations, see feature highlights, and navigate to sign up.

**Acceptance Scenarios**:

1. **Given** I visit the root URL, **When** the landing page loads, **Then** I see a hero section with 3D animated elements and a clear CTA
2. **Given** I scroll down the landing page, **When** I view the features section, **Then** I see interactive 3D cards showcasing app features with glassmorphism effects
3. **Given** I'm on the landing page, **When** I click "Get Started", **Then** I'm redirected to the sign-up page with smooth page transition
4. **Given** I hover over feature cards, **When** my mouse moves, **Then** cards respond with 3D transform effects and depth

---

### User Story 2 - User Authentication (Priority: P1)

As a new user, I want to sign up and sign in securely, so I can access my personal task management dashboard.

**Why this priority**: Core requirement for multi-user support. Security and UX must be excellent.

**Independent Test**: Can create account, sign in, sign out, and access protected routes. Passwords are hashed, sessions are secure.

**Acceptance Scenarios**:

1. **Given** I'm on the sign-up page, **When** I enter email/password and submit, **Then** my account is created and I'm redirected to the dashboard
2. **Given** I have an account, **When** I sign in with correct credentials, **Then** I access my personal dashboard with my tasks
3. **Given** I'm signed in, **When** I click sign out, **Then** I'm logged out and redirected to the landing page
4. **Given** I try to access /dashboard without signing in, **When** the page loads, **Then** I'm redirected to the sign-in page
5. **Given** I enter an invalid email format, **When** I submit, **Then** I see a validation error before API call
6. **Given** I enter wrong credentials, **When** I submit, **Then** I see "Invalid credentials" error message

---

### User Story 3 - Protected Dashboard (Priority: P1)

As a signed-in user, I want my tasks to be private and only accessible to me, so my data is secure.

**Why this priority**: Data privacy is essential. Each user must only see their own tasks.

**Independent Test**: User A cannot see User B's tasks. All API requests require valid authentication token.

**Acceptance Scenarios**:

1. **Given** I'm signed in as User A, **When** I view my dashboard, **Then** I only see tasks I created
2. **Given** User B creates a task, **When** User A views the dashboard, **Then** User B's task is NOT visible
3. **Given** I'm not signed in, **When** I try to call GET /api/v1/tasks, **Then** I receive 401 Unauthorized
4. **Given** my session expires, **When** I try to perform an action, **Then** I'm redirected to sign-in page

---

## Requirements

### Functional Requirements - Landing Page

- **FR-001**: System MUST display a hero section with 3D animated elements (rotating logo, parallax background)
- **FR-002**: Landing page MUST showcase 5+ key features with 3D interactive cards
- **FR-003**: Feature cards MUST have glassmorphism effect (backdrop-filter: blur)
- **FR-004**: Cards MUST respond to mouse hover with 3D transforms (perspective, rotateX, rotateY)
- **FR-005**: Page MUST have smooth scroll animations (fade-in, slide-up) on element visibility
- **FR-006**: Landing page MUST have "Get Started" and "Sign In" CTAs
- **FR-007**: Page MUST be fully responsive (mobile, tablet, desktop)
- **FR-008**: All animations MUST run at 60fps with GPU acceleration

### Functional Requirements - Authentication

- **FR-009**: System MUST support email/password registration
- **FR-010**: Passwords MUST be hashed using bcrypt (minimum 10 rounds)
- **FR-011**: System MUST validate email format before submission
- **FR-012**: Passwords MUST be minimum 8 characters with at least 1 number, 1 uppercase, 1 lowercase
- **FR-013**: System MUST issue JWT tokens on successful sign-in (expiry: 7 days)
- **FR-014**: System MUST store JWT in httpOnly cookies (secure in production)
- **FR-015**: All /api/v1/* endpoints MUST require valid JWT token
- **FR-016**: System MUST provide sign-out functionality (clear JWT cookie)
- **FR-017**: Protected routes MUST redirect to /signin if not authenticated
- **FR-018**: Sign-in page MUST have "Remember me" checkbox (30-day expiry)
- **FR-019**: System MUST prevent duplicate email registration

### Functional Requirements - User Data Isolation

- **FR-020**: All Task model records MUST have user_id foreign key
- **FR-021**: GET /tasks MUST filter by current user's user_id
- **FR-022**: POST /tasks MUST automatically set user_id from JWT token
- **FR-023**: Users MUST NOT be able to access other users' tasks via API manipulation
- **FR-024**: Database migration MUST add user_id to existing tasks (set to default user)

### Non-Functional Requirements

- **NFR-001**: Landing page MUST achieve Lighthouse score >90 (Performance, Accessibility)
- **NFR-002**: Authentication API responses MUST be < 300ms (p95)
- **NFR-003**: JWT secret MUST be stored in environment variables, not hardcoded
- **NFR-004**: Password validation MUST happen client-side and server-side
- **NFR-005**: HTTPS MUST be enforced in production
- **NFR-006**: CORS MUST be configured to allow only frontend origin

## Technical Architecture

### Technology Stack

#### Backend (NEW)
- **Auth Library**: `python-jose[cryptography]` (JWT), `passlib[bcrypt]` (password hashing)
- **Middleware**: FastAPI dependency injection for JWT validation
- **Session Management**: JWT tokens in httpOnly cookies

#### Frontend (NEW)
- **Auth State**: Custom React Context (AuthContext)
- **Route Protection**: Higher-order component (withAuth)
- **Form Validation**: `react-hook-form` + `zod` schema validation
- **3D Effects**: `framer-motion` (animations), `react-spring` (physics), custom CSS transforms
- **Landing Page**: Custom components with Tailwind CSS

### Data Model Evolution

```python
# NEW User model
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# UPDATED Task model (add user_id)
class Task(SQLModel, table=True):
    # ... existing fields ...
    user_id: int = Field(foreign_key="user.id", index=True)  # NEW
```

### API Endpoints

```
Base URL: http://localhost:8000/api/v1

# Authentication (NEW)
POST   /auth/register          # Register new user
POST   /auth/login             # Sign in (returns JWT cookie)
POST   /auth/logout            # Sign out (clears JWT cookie)
GET    /auth/me                # Get current user info
POST   /auth/refresh           # Refresh JWT token

# Protected Task Endpoints (UPDATED)
GET    /tasks                  # Now filtered by user_id from JWT
POST   /tasks                  # user_id auto-set from JWT
...                            # All other task endpoints require auth
```

### Project Structure (NEW)

```
backend/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py         # Auth endpoints
│   │   ├── dependencies.py   # get_current_user dependency
│   │   ├── jwt.py            # JWT encode/decode
│   │   └── password.py       # bcrypt hashing
│   ├── middleware/
│   │   └── auth_middleware.py # JWT validation middleware
│   └── models.py             # User model added

frontend/
├── app/
│   ├── (landing)/
│   │   ├── page.tsx          # Landing page
│   │   └── layout.tsx        # Landing layout (no header)
│   ├── (auth)/
│   │   ├── signin/page.tsx   # Sign-in page
│   │   └── signup/page.tsx   # Sign-up page
│   ├── (protected)/
│   │   ├── dashboard/page.tsx # Protected dashboard
│   │   └── layout.tsx         # Protected layout (with auth check)
│   └── layout.tsx            # Root layout
├── components/
│   ├── landing/
│   │   ├── Hero3D.tsx        # 3D hero section
│   │   ├── FeatureCard3D.tsx # 3D feature cards
│   │   ├── AnimatedSection.tsx
│   │   └── GlassCard.tsx     # Glassmorphism card
│   └── auth/
│       ├── SignInForm.tsx
│       ├── SignUpForm.tsx
│       └── AuthGuard.tsx     # Protected route HOC
├── contexts/
│   └── AuthContext.tsx       # Auth state management
└── lib/
    └── auth.ts               # Auth utilities
```

## 3D Effects Specification

### Hero Section 3D Effects

1. **3D Rotating Logo**
   - Continuous slow rotation on X/Y axes
   - Responds to mouse movement (parallax effect)
   - GPU-accelerated with `transform: translateZ()`
   - Smooth transitions with `transition: transform 0.3s ease-out`

2. **Parallax Background Layers**
   - 3 layers: background, midground, foreground
   - Each layer moves at different speeds on scroll
   - Creates depth perception

3. **Floating Elements**
   - Task cards floating with `react-spring` physics
   - Gentle up/down animation (3px range)
   - Staggered animation delays

### Feature Cards 3D Effects

1. **Glassmorphism**
   ```css
   backdrop-filter: blur(10px);
   background: rgba(255, 255, 255, 0.1);
   border: 1px solid rgba(255, 255, 255, 0.2);
   ```

2. **3D Hover Transform**
   ```css
   perspective: 1000px;
   transform-style: preserve-3d;

   &:hover {
     transform: rotateX(5deg) rotateY(5deg) translateZ(20px);
   }
   ```

3. **Shine Effect**
   - Gradient overlay moves on hover
   - Creates "light reflection" effect

4. **Shadow Depth**
   - Multiple box-shadows for depth
   - Shadow changes on hover to simulate lifting

### Scroll Animations

- Elements fade in and slide up when entering viewport
- Use Intersection Observer API for performance
- Staggered animations (50ms delay between elements)

## Implementation Timeline

### Phase 1: Backend Auth (3-4 hours)
- [ ] Create User model and migration
- [ ] Add user_id to Task model (migration)
- [ ] Implement JWT utilities (encode/decode)
- [ ] Implement password hashing (bcrypt)
- [ ] Create auth routes (register, login, logout, me)
- [ ] Add get_current_user dependency
- [ ] Protect task routes with auth dependency
- [ ] Test auth flow with Postman

### Phase 2: Landing Page 3D Effects (4-5 hours)
- [ ] Install framer-motion, react-spring
- [ ] Create Hero3D component with rotating logo
- [ ] Create GlassCard component
- [ ] Create FeatureCard3D with hover effects
- [ ] Implement parallax scrolling
- [ ] Add scroll animations (fade-in, slide-up)
- [ ] Optimize for 60fps (will-change, GPU acceleration)

### Phase 3: Auth Frontend (3-4 hours)
- [ ] Create AuthContext with sign-in/sign-up/sign-out
- [ ] Create SignInForm with validation
- [ ] Create SignUpForm with validation
- [ ] Create AuthGuard for protected routes
- [ ] Update dashboard to use protected layout
- [ ] Add sign-out button to dashboard
- [ ] Test full auth flow

### Total: 10-13 hours

## Success Criteria

- ✅ Landing page loads with 3D effects at 60fps
- ✅ All 3D hover effects work smoothly
- ✅ Glassmorphism effects render correctly
- ✅ User can sign up with email/password
- ✅ User can sign in and access dashboard
- ✅ User can sign out
- ✅ Protected routes redirect to sign-in if not authenticated
- ✅ Each user only sees their own tasks
- ✅ JWT tokens are secure (httpOnly cookies)
- ✅ Lighthouse score >90 on landing page
- ✅ All auth APIs respond <300ms

## Dependencies

### Backend (requirements.txt additions)
```
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4            # Password hashing
python-multipart==0.0.6           # Form data
```

### Frontend (package.json additions)
```json
{
  "dependencies": {
    "framer-motion": "^10.16.16",
    "react-spring": "^9.7.3",
    "react-hook-form": "^7.49.2",
    "zod": "^3.22.4"
  }
}
```

## Out of Scope

- ❌ OAuth (Google, GitHub) - Future enhancement
- ❌ Email verification - Future enhancement
- ❌ Password reset - Future enhancement
- ❌ Two-factor authentication - Future enhancement
- ❌ User profile management - Future enhancement

## Risk Mitigation

1. **Security**: Use well-tested libraries (python-jose, passlib), follow OWASP guidelines
2. **Performance**: Use GPU acceleration for 3D effects, test on low-end devices
3. **UX**: Clear error messages, loading states, smooth transitions
4. **Data Migration**: Existing tasks assigned to default user, migration script tested on backup
