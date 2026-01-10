import React, { createContext, useContext, useState } from 'react';

export interface OnboardingData {
    theme: string;
    duration: number; // in minutes (15-120)
    distance: number; // in km (1-8)
}

export interface UserLocation {
    latitude: number | null;
    longitude: number | null;
}

interface OnboardingContextType {
    isOnboarding: boolean;
    onboardingStep: number;
    onboardingData: OnboardingData;
    userLocation: UserLocation;
    startOnboarding: () => void;
    nextStep: () => void;
    prevStep: () => void;
    setTheme: (theme: string) => void;
    setDuration: (duration: number) => void;
    setDistance: (distance: number) => void;
    setUserLocation: (location: UserLocation) => void;
    completeOnboarding: () => void;
}

const defaultOnboardingData: OnboardingData = {
    theme: '',
    duration: 60, // default 1 hour
    distance: 4, // default 4km
};

const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

export const OnboardingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isOnboarding, setIsOnboarding] = useState(true);
    const [onboardingStep, setOnboardingStep] = useState(0);
    const [onboardingData, setOnboardingData] = useState<OnboardingData>(defaultOnboardingData);
    const [userLocation, setUserLocation] = useState<UserLocation>({ latitude: null, longitude: null });

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

    const setUserLocationState = (location: UserLocation) => {
        setUserLocation(location);
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
        startOnboarding,
        nextStep,
        prevStep,
        setTheme,
        setDuration,
        setDistance,
        setUserLocation: setUserLocationState,
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
