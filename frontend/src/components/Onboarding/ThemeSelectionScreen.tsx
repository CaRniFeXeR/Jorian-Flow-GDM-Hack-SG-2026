import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowLeft } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';
import { getThemeOptionsApiV1ThemeOptionsPost } from '../../client';
import type { ThemeOptionsResponse } from '../../client';

interface ThemeOption {
    id: string;
    label: string;
    icon: string;
    description: string;
}

interface ThemeSelectionScreenProps {
    onNext: () => void;
    onPrev: () => void;
}

const ThemeSelectionScreen: React.FC<ThemeSelectionScreenProps> = ({ onNext, onPrev }) => {
    const { onboardingData, setTheme } = useOnboarding();
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
        if (suggestedThemes.length === 0 && !isLoadingThemes) {
            setIsLoadingThemes(true);
            getThemeOptionsApiV1ThemeOptionsPost({
                body: {
                    address: 'Northumberland Road, Singapore',
                    use_dummy_data: import.meta.env.VITE_USE_DUMMY_DATA === 'true'
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
    }, [suggestedThemes.length, isLoadingThemes]);

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

    const canProceedFromStep1 = () => {
        // Can proceed from theme selection only if a theme is selected
        // If theme is "custom", user must have submitted a custom theme
        if (onboardingData.theme === 'custom') {
            return false; // Don't allow proceeding if just "custom" without submission
        }
        return onboardingData.theme !== '' || customTheme.trim() !== '';
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
                What interests you?
            </h2>
            <p className="text-gray-600 mb-8">
                Choose a theme or create your own adventure
            </p>

            {isLoadingThemes ? (
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
    );
};

export default ThemeSelectionScreen;
