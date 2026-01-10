import React, { createContext, useContext, useState } from 'react';
import { tourData, type TourStop } from '../data/tourData';

interface TourContextType {
    tour: { stops: TourStop[] };
    currentStop: TourStop;
    currentStopIndex: number;
    goToStop: (index: number) => void;
    nextStop: () => void;
    prevStop: () => void;
    isPlaying: boolean;
    setPlaying: (playing: boolean) => void;
}

const TourContext = createContext<TourContextType | undefined>(undefined);

export const TourProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentStopIndex, setCurrentStopIndex] = useState(0);
    const [isPlaying, setPlaying] = useState(false);

    const goToStop = (index: number) => {
        if (index >= 0 && index < tourData.stops.length) {
            setCurrentStopIndex(index);
        }
    };

    const nextStop = () => {
        setCurrentStopIndex((prev) => (prev + 1) % tourData.stops.length);
    };

    const prevStop = () => {
        setCurrentStopIndex((prev) => (prev - 1 + tourData.stops.length) % tourData.stops.length);
    };

    const value = {
        tour: tourData,
        currentStop: tourData.stops[currentStopIndex],
        currentStopIndex,
        goToStop,
        nextStop,
        prevStop,
        isPlaying,
        setPlaying
    };

    return <TourContext.Provider value={value}>{children}</TourContext.Provider>;
};

export const useTour = () => {
    const context = useContext(TourContext);
    if (!context) {
        throw new Error('useTour must be used within a TourProvider');
    }
    return context;
};
