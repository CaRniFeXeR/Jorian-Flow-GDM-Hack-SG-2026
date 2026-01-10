import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';

interface PreferencesScreenProps {
    onPrev: () => void;
    onNext: () => void;
}

const PreferencesScreen: React.FC<PreferencesScreenProps> = ({ onPrev, onNext }) => {
    const { onboardingData, setDuration, setDistance } = useOnboarding();

    const formatDuration = (minutes: number): string => {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (mins === 0) {
            return `${hours}h`;
        }
        return `${hours}h ${mins}min`;
    };

    const formatDistance = (km: number): string => {
        return `${km} km`;
    };

    return (
        <motion.div
            key="step1"
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-2xl mx-auto"
        >
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Customize your tour
            </h2>
            <p className="text-gray-600 mb-8">
                Set your preferred duration and walking distance
            </p>

            {/* Duration Slider */}
            <div className="mb-10">
                <div className="flex justify-between items-center mb-4">
                    <label className="text-lg font-semibold text-gray-900">
                        Tour Duration
                    </label>
                    <span className="text-xl font-bold text-blue-600">
                        {formatDuration(onboardingData.duration)}
                    </span>
                </div>
                <input
                    type="range"
                    min="15"
                    max="120"
                    step="15"
                    value={onboardingData.duration}
                    onChange={(e) => setDuration(parseInt(e.target.value))}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    style={{
                        background: `linear-gradient(to right, #2563eb 0%, #2563eb ${((onboardingData.duration - 15) / (120 - 15)) * 100}%, #e5e7eb ${((onboardingData.duration - 15) / (120 - 15)) * 100}%, #e5e7eb 100%)`,
                    }}
                />
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                    <span>15 min</span>
                    <span>2 hours</span>
                </div>
            </div>

            {/* Distance Slider */}
            <div className="mb-10">
                <div className="flex justify-between items-center mb-4">
                    <label className="text-lg font-semibold text-gray-900">
                        Walking Distance
                    </label>
                    <span className="text-xl font-bold text-blue-600">
                        {formatDistance(onboardingData.distance)}
                    </span>
                </div>
                <input
                    type="range"
                    min="1"
                    max="8"
                    step="0.5"
                    value={onboardingData.distance}
                    onChange={(e) => setDistance(parseFloat(e.target.value))}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    style={{
                        background: `linear-gradient(to right, #2563eb 0%, #2563eb ${((onboardingData.distance - 1) / (8 - 1)) * 100}%, #e5e7eb ${((onboardingData.distance - 1) / (8 - 1)) * 100}%, #e5e7eb 100%)`,
                    }}
                />
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                    <span>1 km</span>
                    <span>8 km</span>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex justify-between mt-8">
                <button
                    onClick={onPrev}
                    className="px-6 py-3 flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
                >
                    <ArrowLeft className="w-5 h-5 mr-2" />
                    Back
                </button>
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={onNext}
                    className="px-8 py-3 flex items-center bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
                >
                    Continue
                    <ArrowRight className="w-5 h-5 ml-2" />
                </motion.button>
            </div>
        </motion.div>
    );
};

export default PreferencesScreen;
