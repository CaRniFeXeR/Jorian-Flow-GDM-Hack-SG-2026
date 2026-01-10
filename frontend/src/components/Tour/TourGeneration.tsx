import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import type { Tour } from '../../client/types.gen';
import MapContainer from '../Map/MapContainer';
import { getTourByIdApiV1TourIdIsDummyGet } from '../../client';

const loadingMessages = [
    'Setting up the tour...',
    'Calculating route...',
    'Considering possible attractions...',
    'Optimizing your experience...',
];

const TourGeneration: React.FC = () => {
    const { tourId } = useParams<{ tourId: string }>();
    const navigate = useNavigate();
    const [tour, setTour] = useState<Tour | null>(null);
    const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
    const [hasPoisWithLocations, setHasPoisWithLocations] = useState(false);
    const [isPolling, setIsPolling] = useState(true);

    useEffect(() => {
        if (!tourId) {
            navigate('/');
            return;
        }

        const pollTour = async () => {
            try {
                const response = await getTourByIdApiV1TourIdIsDummyGet({
                    path: { tour_id: tourId, is_dummy: import.meta.env.VITE_USE_DUMMY_DATA === 'true' },
                    baseUrl: 'http://localhost:8000',
                });

                if (response.error) {
                    console.error('Error fetching tour:', response.error);
                    return;
                }

                const tourData = response.data as Tour;
                setTour(tourData);

                // Check if POIs have locations (address or google_place_id)
                if (tourData.pois && tourData.pois.length > 0) {
                    const hasLocations = tourData.pois.some(
                        (poi) => poi.address || poi.google_place_id
                    );
                    if (hasLocations && !hasPoisWithLocations) {
                        setHasPoisWithLocations(true);
                    }
                }

                // Check if introduction is ready
                if (tourData.introduction && tourData.introduction.trim() !== '') {
                    setIsPolling(false);
                    // Navigate to tour view (which will start playing introduction)
                    navigate(`/tour/${tourId}`, { replace: true });
                }
            } catch (error) {
                console.error('Error polling tour:', error);
            }
        };

        // Initial fetch
        pollTour();

        // Poll every 10 seconds
        const pollInterval = setInterval(pollTour, 10000);

        return () => {
            clearInterval(pollInterval);
        };
    }, [tourId, navigate, hasPoisWithLocations]);

    // Rotate loading messages
    useEffect(() => {
        if (!isPolling) return;

        const messageInterval = setInterval(() => {
            setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length);
        }, 2000);

        return () => clearInterval(messageInterval);
    }, [isPolling]);


    const mapHeight = hasPoisWithLocations ? '50vh' : '30vh';

    return (
        <div className="relative w-full h-screen overflow-hidden bg-gray-50 flex flex-col">
            {/* Map at top (30% or 50% depending on POI availability) */}
            <div className="absolute top-0 left-0 right-0" style={{ height: mapHeight }}>
                <MapContainer
                    height={mapHeight}
                    showTourContent={hasPoisWithLocations && tour?.pois && tour.pois.length > 0}
                    pois={tour?.pois || []}
                />
            </div>

            {/* Loading Content */}
            <div
                className="absolute bottom-0 left-0 right-0 bg-white rounded-t-[2.5rem] shadow-2xl flex flex-col"
                style={{ height: hasPoisWithLocations ? '50vh' : '70vh' }}
            >
                <div className="flex-1 flex flex-col items-center justify-center px-6">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={loadingMessageIndex}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.3 }}
                            className="text-center"
                        >
                            <div className="mb-4">
                                <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                {loadingMessages[loadingMessageIndex]}
                            </h2>
                            <p className="text-gray-600">
                                Please wait while we prepare your personalized tour...
                            </p>
                        </motion.div>
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};

export default TourGeneration;
