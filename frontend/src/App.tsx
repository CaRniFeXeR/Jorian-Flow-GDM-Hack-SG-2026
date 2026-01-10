import MapContainer from './components/Map/MapContainer';
import Drawer from './components/UI/Drawer';
import Onboarding from './components/Onboarding/Onboarding';
import { useOnboarding } from './context/OnboardingContext';

function App() {
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

export default App;
