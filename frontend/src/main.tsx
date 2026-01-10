import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { TourProvider } from './context/TourContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <TourProvider>
      <App />
    </TourProvider>
  </StrictMode>,
)
