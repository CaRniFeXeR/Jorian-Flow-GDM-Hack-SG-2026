import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { TourProvider } from './context/TourContext'
import { OnboardingProvider } from './context/OnboardingContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <OnboardingProvider>
      <TourProvider>
        <App />
      </TourProvider>
    </OnboardingProvider>
  </StrictMode>,
)
