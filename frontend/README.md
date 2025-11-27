# Resume Analyzer - React Frontend

Modern React frontend built with Next.js, TypeScript, Tailwind CSS, and shadcn/ui for the Resume Analyzer application.

## 🚀 Features

- **Modern Hero Section**: Beautiful animated hero section with retro grid background
- **Resume Analysis**: Interactive form to analyze resumes against job descriptions
- **Real-time Results**: Instant feedback with detailed scoring breakdown
- **Skills Matching**: Visual representation of matched and missing skills
- **Dark Mode Support**: Full dark mode support throughout the application
- **Responsive Design**: Mobile-first responsive design

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (FastAPI)

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
npm start
```

## 🎨 Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **Icons**: lucide-react

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Main landing page
│   │   └── globals.css       # Global styles
│   ├── components/
│   │   ├── ui/
│   │   │   └── hero-section-dark.tsx
│   │   └── resume-analyzer.tsx
│   └── lib/
│       └── utils.ts
└── package.json
```

## 🔌 API Integration

Connects to FastAPI backend at `http://localhost:8000/analyze`

## �� License

MIT License
