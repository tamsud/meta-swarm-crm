# CRM Frontend

React frontend for the Meta Swarm CRM platform.

## Prerequisites

- Node.js 22+ (see `.nvmrc`)
- npm 10.9+

## Setup

```bash
# Install dependencies
npm install
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
VITE_API_URL=http://localhost:8000
```

## Running the Dev Server

```bash
# Start development server
npm run dev

# App available at http://localhost:5173
```

## Building for Production

```bash
# Type check and build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx          # App entry point
│   ├── App.tsx           # Root component with routing
│   ├── components/       # Reusable UI components
│   ├── pages/            # Route page components
│   ├── hooks/            # Custom React hooks
│   ├── services/         # API client functions
│   ├── contexts/         # React contexts (auth, etc.)
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
├── index.html            # HTML entry point
├── vite.config.ts        # Vite configuration
├── tailwind.config.ts    # TailwindCSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Type check and build for production |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build locally |

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool with HMR
- **TailwindCSS** - Utility-first styling
- **React Query** - Server state management
- **React Router** - Client-side routing
- **Axios** - HTTP client
