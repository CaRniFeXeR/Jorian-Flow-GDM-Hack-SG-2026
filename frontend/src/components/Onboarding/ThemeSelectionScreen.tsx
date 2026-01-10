import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useOnboarding } from '../../context/OnboardingContext';
import { guardrailValidationApiV1GuardrailPost } from '../../client';
import type { GuardrailResponse } from '../../client';

interface ThemeSelectionScreenProps {
    onPrev: () => void;
}

const ThemeSelectionScreen: React.FC<ThemeSelectionScreenProps> = ({ onPrev }) => {
    const { onboardingData, setTheme, suggestedThemes, isLoadingThemes, userLocation } = useOnboarding();
    const [customTheme, setCustomTheme] = useState('');
    const [showCustomInput, setShowCustomInput] = useState(false);
    const [isValidating, setIsValidating] = useState(false);
    const navigate = useNavigate();

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

    const canProceedFromStep2 = () => {
        // Can proceed from theme selection only if a theme is selected
        // If theme is "custom", user must have submitted a custom theme
        if (onboardingData.theme === 'custom') {
            return false; // Don't allow proceeding if just "custom" without submission
        }
        return onboardingData.theme !== '' || customTheme.trim() !== '';
    };

    const handleStartGeneration = async () => {
        if (!onboardingData.theme || onboardingData.theme.trim() === '') {
            return;
        }

        setIsValidating(true);

        try {
            // Call guardrail validation API
            // Address should be available from theme options response
            const userAddress = onboardingData.address || 'Singapore'; // Fallback to Singapore if not set
            
            const response = await guardrailValidationApiV1GuardrailPost({
                body: {
                    constraints: {
                        max_time: `${onboardingData.duration}`, // Convert to string format expected by API
                        distance: `${onboardingData.distance}`, // Convert to string format
                        custom: onboardingData.theme,
                        address: userAddress,
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
                className="mb-1 px-4 py-2 flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors"
            >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back
            </button>

            <h2 className="text-3xl font-bold text-gray-900 mb-2">
                What interests you?
            </h2>
            <p className="text-gray-600 mb-8">
                Choose a theme or create your own adventure
            </p>

            {!userLocation.latitude || !userLocation.longitude ? (
                <div className="flex flex-col justify-center items-center py-12">
                    <div className="text-gray-700 text-lg font-medium mb-2">
                        Getting your location...
                    </div>
                    <div className="text-gray-500 text-sm">
                        Please allow location access to get personalized theme suggestions
                    </div>
                </div>
            ) : isLoadingThemes ? (
                <div className="flex flex-col justify-center items-center py-12">
                    <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                    <div className="text-gray-700 text-lg font-medium">
                        Finding suggestions for your current location
                    </div>
                    <div className="text-gray-500 text-sm mt-2">
                        This may take a few moments...
                    </div>
                </div>
            ) : suggestedThemes.length > 0 ? (
                <div className="grid grid-cols-2 gap-4 mb-6">
                    {suggestedThemes.map((theme, index) => {
                        // Parse emoji and label from theme string (format: "🏛️ Historical Heritage Walk")
                        const emojiRegex = /^(\p{Emoji}+)\s*(.*)$/u;
                        const match = theme.match(emojiRegex);
                        const emoji = match ? match[1] : theme.charAt(0);
                        const label = match ? match[2] : theme;
                        
                        return (
                            <motion.button
                                key={`theme-${index}`}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => handleThemeSelect(theme)}
                                className={`p-6 rounded-2xl border-2 transition-all ${
                                    onboardingData.theme === theme
                                        ? 'border-blue-600 bg-blue-50 shadow-lg'
                                        : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                                }`}
                            >
                                <div className="text-4xl mb-2">{emoji}</div>
                                <div className="text-sm font-semibold text-gray-900">
                                    {label}
                                </div>
                            </motion.button>
                        );
                    })}
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

            {/* Start Generating Button - Full Width */}
            <div className="mt-8">
                <motion.button
                    whileHover={{ scale: isValidating || !canProceedFromStep2() ? 1 : 1.05 }}
                    whileTap={{ scale: isValidating || !canProceedFromStep2() ? 1 : 0.95 }}
                    onClick={handleStartGeneration}
                    disabled={isValidating || !canProceedFromStep2()}
                    className={`w-full px-8 py-4 flex items-center justify-center rounded-xl font-semibold transition-all ${
                        canProceedFromStep2() && !isValidating
                            ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg hover:shadow-xl'
                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
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
            </div>
        </motion.div>
    );
};

export default ThemeSelectionScreen;
