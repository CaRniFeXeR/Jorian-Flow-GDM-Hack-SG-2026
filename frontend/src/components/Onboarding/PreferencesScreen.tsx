import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useOnboarding } from '../../context/OnboardingContext';
import { guardrailValidationApiV1GuardrailPost } from '../../client';
import type { GuardrailResponse } from '../../client';

interface PreferencesScreenProps {
    onPrev: () => void;
}

const PreferencesScreen: React.FC<PreferencesScreenProps> = ({ onPrev }) => {
    const { onboardingData, setDuration, setDistance } = useOnboarding();
    const [isValidating, setIsValidating] = useState(false);
    const navigate = useNavigate();

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

    const handleStartGeneration = async () => {
        if (!onboardingData.theme || onboardingData.theme.trim() === '') {
            return;
        }

        setIsValidating(true);

        try {
            // Call guardrail validation API
            const response = await guardrailValidationApiV1GuardrailPost({
                body: {
                    user_address: 'Singapore', // Default to Singapore for now
                    constraints: {
                        max_time: `${onboardingData.duration}`, // Convert to string format expected by API
                        distance: `${onboardingData.distance}`, // Convert to string format
                        custom: onboardingData.theme,
                    },
                },
                baseUrl: 'http://localhost:8000',
            });

            if (response.error) {
                console.error('Error validating tour:', response.error);
                navigate('/error');
                setIsValidating(false);
                return;
            }

            const data = response.data as GuardrailResponse;

            if (!data.valid) {
                // Invalid theme, show error screen
                navigate('/error');
                setIsValidating(false);
                return;
            }

            // Valid theme, navigate to tour generation page
            navigate(`/tour/generate/${data.transaction_id}`);
            setIsValidating(false);
        } catch (error) {
            console.error('Error starting tour generation:', error);
            navigate('/error');
            setIsValidating(false);
        }
    };

    return (
        <motion.div
            key="step2"
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-2xl mx-auto"
        >
            {/* Back button */}
            <button
                onClick={onPrev}
                className="mb-4 p-2 text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Go back"
            >
                <ArrowLeft className="w-5 h-5" />
            </button>
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
            <motion.button
                whileHover={{ scale: isValidating ? 1 : 1.05 }}
                whileTap={{ scale: isValidating ? 1 : 0.95 }}
                onClick={handleStartGeneration}
                disabled={isValidating}
                className={`w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white text-lg font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center ${
                    isValidating ? 'opacity-75 cursor-not-allowed' : ''
                }`}
            >
                {isValidating ? (
                    <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                        Checking your input...
                    </>
                ) : (
                    <>
                        Start Generating Tour
                        <Sparkles className="w-5 h-5 ml-2" />
                    </>
                )}
            </motion.button>
        </motion.div>
    );
};

export default PreferencesScreen;
