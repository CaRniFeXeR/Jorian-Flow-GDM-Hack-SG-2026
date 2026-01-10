import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Sparkles } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import MapContainer from '../Map/MapContainer';
import { getThemeOptionsApiV1ThemeOptionsPost } from '../../client';
import type { ThemeOptionsResponse } from '../../client';

interface ThemeOption {
    id: string;
    label: string;
    icon: string;
    description: string;
}

const Onboarding: React.FC = () => {
    const {
        onboardingStep,
        onboardingData,
        nextStep,
        prevStep,
        setTheme,
        setDuration,
        setDistance,
        completeOnboarding,
    } = useOnboarding();

    const [customTheme, setCustomTheme] = useState('');
    const [showCustomInput, setShowCustomInput] = useState(false);
    const [suggestedThemes, setSuggestedThemes] = useState<ThemeOption[]>([]);
    const [isLoadingThemes, setIsLoadingThemes] = useState(false);

    // Extract emoji and label from theme name
    const parseThemeName = (themeName: string): { emoji: string; label: string } => {
        // Check if theme name starts with an emoji (usually first 2-4 characters)
        const emojiRegex = /^(\p{Emoji}+)\s*(.*)$/u;
        const match = themeName.match(emojiRegex);
        
        if (match) {
            return {
                emoji: match[1],
                label: match[2] || themeName
            };
        }
        
        // If no emoji found, return first character as fallback or empty
        return {
            emoji: themeName.charAt(0),
            label: themeName
        };
    };

    // Fetch theme options from API
    useEffect(() => {
        if (onboardingStep === 1 && suggestedThemes.length === 0 && !isLoadingThemes) {
            setIsLoadingThemes(true);
            getThemeOptionsApiV1ThemeOptionsPost({
                body: {
                    address: 'Singapore',
                    use_dummy_data: true
                },
                baseUrl: 'http://localhost:8000'
            })
            .then(response => {
                if (response.error) {
                    console.error('Error fetching theme options:', response.error);
                    setSuggestedThemes([]);
                    setIsLoadingThemes(false);
                    return;
                }
                
                const data = response.data as ThemeOptionsResponse;
                const themes = data?.themes || {};
                const parsedThemes: ThemeOption[] = Object.entries(themes).map(([themeName, description], index) => {
                    const { emoji, label } = parseThemeName(themeName);
                    return {
                        id: `theme-${index}`,
                        label: label,
                        icon: emoji,
                        description: description as string
                    };
                });
                setSuggestedThemes(parsedThemes);
                setIsLoadingThemes(false);
            })
            .catch(error => {
                console.error('Error fetching theme options:', error);
                setIsLoadingThemes(false);
                // Fallback to empty themes if API fails
                setSuggestedThemes([]);
            });
        }
    }, [onboardingStep, suggestedThemes.length, isLoadingThemes]);

    const handleThemeSelect = (theme: string) => {
        setTheme(theme);
        if (theme === 'custom') {
            setShowCustomInput(true);
        } else {
            setShowCustomInput(false);
        }
    };

    const handleCustomThemeSubmit = () => {
        if (customTheme.trim()) {
            setTheme(customTheme.trim());
            setShowCustomInput(false);
        }
    };

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

    const canProceedFromStep1 = () => {
        // Can proceed from theme selection only if a theme is selected
        // If theme is "custom", user must have submitted a custom theme
        if (onboardingData.theme === 'custom') {
            return false; // Don't allow proceeding if just "custom" without submission
        }
        return onboardingData.theme !== '' || customTheme.trim() !== '';
    };

    const slideVariants = {
        enter: (direction: number) => ({
            x: direction > 0 ? 300 : -300,
            opacity: 0,
        }),
        center: {
            x: 0,
            opacity: 1,
        },
        exit: (direction: number) => ({
            x: direction < 0 ? 300 : -300,
            opacity: 0,
        }),
    };

    const [direction, setDirection] = useState(0);

    const handleNext = () => {
        // Step 0 (welcome): Always can proceed
        // Step 1 (theme selection): Check if theme is selected
        if (onboardingStep === 1 && !canProceedFromStep1()) return;
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
                        {/* Step 0: Welcome */}
                        {onboardingStep === 0 && (
                            <motion.div
                                key="step0"
                                custom={direction}
                                variants={slideVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                transition={{ duration: 0.3 }}
                                className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto"
                            >
                                <motion.div
                                    initial={{ scale: 0.8, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ delay: 0.1 }}
                                    className="mb-8"
                                >
                                    <Sparkles className="w-20 h-20 text-blue-600" />
                                </motion.div>
                                <h1 className="text-4xl font-bold text-gray-900 mb-4 text-center">
                                    Welcome to Jorian Flow
                                </h1>
                                <p className="text-lg text-gray-600 mb-8 text-center max-w-md">
                                    Discover personalized walking tours tailored to your interests. Let's create your perfect adventure.
                                </p>
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleNext}
                                    className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white text-lg font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-shadow"
                                >
                                    Get Started
                                    <ArrowRight className="inline-block ml-2 w-5 h-5" />
                                </motion.button>
                            </motion.div>
                        )}

                        {/* Step 1: Theme Selection */}
                        {onboardingStep === 1 && (
                            <motion.div
                                key="step1"
                                custom={direction}
                                variants={slideVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                transition={{ duration: 0.3 }}
                                className="max-w-2xl mx-auto"
                            >
                                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                                    What interests you?
                                </h2>
                                <p className="text-gray-600 mb-8">
                                    Choose a theme or create your own adventure
                                </p>

                                {isLoadingThemes ? (
                                    <div className="flex justify-center items-center py-12">
                                        <div className="text-gray-500">Loading theme suggestions...</div>
                                    </div>
                                ) : suggestedThemes.length > 0 ? (
                                    <div className="grid grid-cols-2 gap-4 mb-6">
                                        {suggestedThemes.map((theme) => (
                                            <motion.button
                                                key={theme.id}
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                onClick={() => handleThemeSelect(theme.label)}
                                                className={`p-6 rounded-2xl border-2 transition-all ${
                                                    onboardingData.theme === theme.label
                                                        ? 'border-blue-600 bg-blue-50 shadow-lg'
                                                        : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                                                }`}
                                            >
                                                <div className="text-4xl mb-2">{theme.icon}</div>
                                                <div className="text-sm font-semibold text-gray-900">
                                                    {theme.label}
                                                </div>
                                            </motion.button>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-gray-500 text-center py-4 mb-6">
                                        No theme suggestions available. Please enter a custom theme.
                                    </div>
                                )}

                                {!showCustomInput ? (
                                    <motion.button
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => handleThemeSelect('custom')}
                                        className="w-full p-4 rounded-xl border-2 border-dashed border-gray-300 text-gray-600 hover:border-blue-400 hover:text-blue-600 transition-colors font-medium"
                                    >
                                        + Or type your own theme
                                    </motion.button>
                                ) : (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        className="mb-6"
                                    >
                                        <input
                                            type="text"
                                            value={customTheme}
                                            onChange={(e) => setCustomTheme(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleCustomThemeSubmit()}
                                            placeholder="e.g., Hidden gems, Street art, Coffee culture..."
                                            className="w-full p-4 rounded-xl border-2 border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
                                            autoFocus
                                        />
                                        <div className="flex gap-2 mt-3">
                                            <button
                                                onClick={handleCustomThemeSubmit}
                                                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                                            >
                                                Use This Theme
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setShowCustomInput(false);
                                                    setCustomTheme('');
                                                    if (onboardingData.theme === 'custom') {
                                                        setTheme('');
                                                    }
                                                }}
                                                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </motion.div>
                                )}

                                {onboardingData.theme && !showCustomInput && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-4 p-4 bg-blue-50 rounded-xl border border-blue-200"
                                    >
                                        <p className="text-sm text-blue-900 font-medium">
                                            Selected: <span className="font-bold">{onboardingData.theme}</span>
                                        </p>
                                    </motion.div>
                                )}

                                {/* Navigation */}
                                <div className="flex justify-between mt-8">
                                    <button
                                        onClick={handlePrev}
                                        className="px-6 py-3 flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                    >
                                        <ArrowLeft className="w-5 h-5 mr-2" />
                                        Back
                                    </button>
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={handleNext}
                                        disabled={!canProceedFromStep1()}
                                        className={`px-8 py-3 flex items-center rounded-xl font-semibold transition-all ${
                                            canProceedFromStep1()
                                                ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg hover:shadow-xl'
                                                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                        }`}
                                    >
                                        Continue
                                        <ArrowRight className="w-5 h-5 ml-2" />
                                    </motion.button>
                                </div>
                            </motion.div>
                        )}

                        {/* Step 2: Preferences */}
                        {onboardingStep === 2 && (
                            <motion.div
                                key="step2"
                                custom={direction}
                                variants={slideVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
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
                                <div className="flex justify-between">
                                    <button
                                        onClick={handlePrev}
                                        className="px-6 py-3 flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
                                    >
                                        <ArrowLeft className="w-5 h-5 mr-2" />
                                        Back
                                    </button>
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={completeOnboarding}
                                        className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white text-lg font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-shadow flex items-center"
                                    >
                                        Start Generating Tour
                                        <Sparkles className="w-5 h-5 ml-2" />
                                    </motion.button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default Onboarding;
