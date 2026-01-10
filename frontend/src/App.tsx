import { useState } from 'react';
import { APIProvider } from '@vis.gl/react-google-maps';
import MapContainer from './components/Map/MapContainer';
import Drawer from './components/UI/Drawer'; // Import Drawer component
import tourData from './data/tour.json';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

function App() {
  const [currentStopIndex, setCurrentStopIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleNext = () => {
    setCurrentStopIndex((prev) => (prev + 1) % tourData.length);
  };

  const handlePrev = () => {
    setCurrentStopIndex((prev) => (prev - 1 + tourData.length) % tourData.length);
  };

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <APIProvider apiKey={API_KEY}>
      <div className="relative w-full h-screen overflow-hidden bg-gray-100 flex flex-col">
        {/* Map takes up the full screen behind the drawer */}
        <div className="absolute inset-0">
          <MapContainer
            currentStop={tourData[currentStopIndex]}
            stops={tourData}
          />
        </div>

        {/* Drawer for controls */}
        <Drawer
          currentStop={tourData[currentStopIndex]}
          isPlaying={isPlaying}
          onTogglePlay={togglePlay}
          onNext={handleNext}
          onPrev={handlePrev}
        />
      </div>
    </APIProvider>
  );
}

export default App;
