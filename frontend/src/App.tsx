import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MapContainer from './components/Map/MapContainer';
import Drawer from './components/UI/Drawer';
import Onboarding from './components/Onboarding/Onboarding';
import TourGeneration from './components/Tour/TourGeneration';
import ErrorScreen from './components/Tour/ErrorScreen';
import TourView from './components/Tour/TourView';
import { useOnboarding } from './context/OnboardingContext';

function AppContent() {
  const { isOnboarding } = useOnboarding();

  if (isOnboarding) {
    return <Onboarding />;
  }

  return (
    <div className="relative w-full h-screen overflow-hidden bg-gray-100 flex flex-col">
      {/* Map takes up the full screen behind the drawer */}
      <div className="absolute inset-0">
        <MapContainer />
      </div>

      {/* Drawer for controls */}
      <Drawer />
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AppContent />} />
        <Route path="/tour/generate/:tourId" element={<TourGeneration />} />
        <Route path="/tour/:tourId/:stopOrder?" element={<TourView />} />
        <Route path="/error" element={<ErrorScreen />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
