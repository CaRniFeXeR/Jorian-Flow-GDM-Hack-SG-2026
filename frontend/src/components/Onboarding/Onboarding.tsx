import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { useOnboarding } from '../../context/OnboardingContext';
import MapContainer from '../Map/MapContainer';
import WelcomeScreen from './WelcomeScreen';
import ThemeSelectionScreen from './ThemeSelectionScreen';
import PreferencesScreen from './PreferencesScreen';

const Onboarding: React.FC = () => {
    const { onboardingStep, nextStep, prevStep } = useOnboarding();
    const [direction, setDirection] = useState(0);

    const handleNext = () => {
        setDirection(1);
        nextStep();
    };

    const handlePrev = () => {
        setDirection(-1);
        prevStep();
    };

    return (
        <div className="relative w-full h-screen overflow-hidden bg-gray-50 flex flex-col">
            {/* Map at 30% top */}
            <div className="absolute top-0 left-0 right-0" style={{ height: '30vh' }}>
                <MapContainer height="30vh" showTourContent={false} />
            </div>

            {/* Onboarding Content */}
            <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-[2.5rem] shadow-2xl flex flex-col" style={{ height: '70vh' }}>
                <div className="flex-1 overflow-y-auto px-6 pt-8 pb-24">
                    <AnimatePresence mode="wait" custom={direction}>
                        {onboardingStep === 0 && (
                            <WelcomeScreen key="step0" onNext={handleNext} />
                        )}
                        {onboardingStep === 1 && (
                            <ThemeSelectionScreen key="step1" onNext={handleNext} onPrev={handlePrev} />
                        )}
                        {onboardingStep === 2 && (
                            <PreferencesScreen key="step2" onPrev={handlePrev} />
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default Onboarding;
