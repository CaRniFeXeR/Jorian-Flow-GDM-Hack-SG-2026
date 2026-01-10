import React, { createContext, useContext, useState, useRef } from 'react';
import { getThemeOptionsApiV1ThemeOptionsPost } from '../client';
import type { ThemeOptionsResponse } from '../client';

export interface OnboardingData {
    theme: string;
    duration: number; // in minutes (15-120)
    distance: number; // in km (1-8)
    address: string; // geocoded address
}

export interface UserLocation {
    latitude: number | null;
    longitude: number | null;
}

export interface ThemeOption {
    id: string;
    label: string;
    icon: string;
    description: string;
}

interface OnboardingContextType {
    isOnboarding: boolean;
    onboardingStep: number;
    onboardingData: OnboardingData;
    userLocation: UserLocation;
    suggestedThemes: ThemeOption[];
    isLoadingThemes: boolean;
    startOnboarding: () => void;
    nextStep: () => void;
    prevStep: () => void;
    setTheme: (theme: string) => void;
    setDuration: (duration: number) => void;
    setDistance: (distance: number) => void;
    setAddress: (address: string) => void;
    setUserLocation: (location: UserLocation) => void;
    fetchThemes: () => Promise<void>;
    completeOnboarding: () => void;
}

const defaultOnboardingData: OnboardingData = {
    theme: '',
    duration: 60, // default 1 hour
    distance: 4, // default 4km
    address: '', // geocoded address
};

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

export const OnboardingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isOnboarding, setIsOnboarding] = useState(true);
    const [onboardingStep, setOnboardingStep] = useState(0);
    const [onboardingData, setOnboardingData] = useState<OnboardingData>(defaultOnboardingData);
    const [userLocation, setUserLocation] = useState<UserLocation>({ latitude: null, longitude: null });
    const [suggestedThemes, setSuggestedThemes] = useState<ThemeOption[]>([]);
    const [isLoadingThemes, setIsLoadingThemes] = useState(false);
    const fetchingThemesRef = useRef(false);

    const startOnboarding = () => {
        setIsOnboarding(true);
        setOnboardingStep(0);
    };

    const nextStep = () => {
        setOnboardingStep((prev) => prev + 1);
    };

    const prevStep = () => {
        setOnboardingStep((prev) => Math.max(0, prev - 1));
    };

    const setTheme = (theme: string) => {
        setOnboardingData((prev) => ({ ...prev, theme }));
    };

    const setDuration = (duration: number) => {
        setOnboardingData((prev) => ({ ...prev, duration }));
    };

    const setDistance = (distance: number) => {
        setOnboardingData((prev) => ({ ...prev, distance }));
    };

    const setAddress = (address: string) => {
        setOnboardingData((prev) => ({ ...prev, address }));
    };

    const setUserLocationState = (location: UserLocation) => {
        setUserLocation(location);
    };

    const fetchThemes = async () => {
        // Don't fetch if already fetching (use ref to prevent race conditions)
        if (fetchingThemesRef.current) {
            return;
        }

        // Don't fetch if themes are already loaded (check state)
        if (suggestedThemes.length > 0) {
            return;
        }

        // Don't fetch if we don't have user location
        if (userLocation.latitude === null || userLocation.longitude === null) {
            console.warn('Cannot fetch themes: user location not available');
            return;
        }

        // Mark as fetching and set loading state
        fetchingThemesRef.current = true;
        setIsLoadingThemes(true);

        try {
            const response = await getThemeOptionsApiV1ThemeOptionsPost({
                body: {
                    latitude: userLocation.latitude,
                    longitude: userLocation.longitude,
                    use_dummy_data: import.meta.env.VITE_USE_DUMMY_DATA === 'true'
                },
                baseUrl: 'http://localhost:8000'
            });

            if (response.error) {
                console.error('Error fetching theme options:', response.error);
                setSuggestedThemes([]);
                setIsLoadingThemes(false);
                return;
            }

            const data = response.data as ThemeOptionsResponse;
            const themes = data?.themes || {};
            const geocodedAddress = data?.address || '';

            // Store the geocoded address in context
            if (geocodedAddress) {
                setAddress(geocodedAddress);
            }

            // Parse theme names to extract emoji and label
            const parseThemeName = (themeName: string): { emoji: string; label: string } => {
                const emojiRegex = /^(\p{Emoji}+)\s*(.*)$/u;
                const match = themeName.match(emojiRegex);
                
                if (match) {
                    return {
                        emoji: match[1],
                        label: match[2] || themeName
                    };
                }
                
                return {
                    emoji: themeName.charAt(0),
                    label: themeName
                };
            };

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
            fetchingThemesRef.current = false;
        } catch (error) {
            console.error('Error fetching theme options:', error);
            setSuggestedThemes([]);
            setIsLoadingThemes(false);
            fetchingThemesRef.current = false;
        }
    };

    const completeOnboarding = () => {
        setIsOnboarding(false);
        // Here you would typically trigger tour generation with onboardingData
        console.log('Onboarding completed:', onboardingData);
    };

    const value = {
        isOnboarding,
        onboardingStep,
        onboardingData,
        userLocation,
        suggestedThemes,
        isLoadingThemes,
        startOnboarding,
        nextStep,
        prevStep,
        setTheme,
        setDuration,
        setDistance,
        setAddress,
        setUserLocation: setUserLocationState,
        fetchThemes,
        completeOnboarding,
    };

    return <OnboardingContext.Provider value={value}>{children}</OnboardingContext.Provider>;
};

export const useOnboarding = () => {
    const context = useContext(OnboardingContext);
    if (!context) {
        throw new Error('useOnboarding must be used within an OnboardingProvider');
    }
    return context;
};
