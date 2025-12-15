# View

Frontend React application (user interface).

**Tech Stack:**
- React + TypeScript
- Vite (build tool)
- Tailwind CSS + shadcn/ui
- Supabase (authentication)

**Main Components:**
- `src/pages/` - Page components (Index, Results, Login, Signup, History, etc.)
- `src/components/` - Reusable UI components (CarCard, SearchChat, Navbar, etc.)
- `src/services/api.ts` - API client for backend communication
- `src/contexts/AuthContext.tsx` - Authentication context provider
- `src/integrations/supabase/` - Supabase client configuration

**What it does:**
- Displays the car search interface
- Sends search queries to the backend API
- Shows car results in cards
- **User Authentication**: Login/signup functionality using Supabase Auth
  - Login page (`/login`) - User sign in
  - Signup page (`/signup`) - User registration
  - Protected routes (History page requires login)
  - Search history saved for logged-in users
  - Navbar shows login/logout buttons based on auth state
