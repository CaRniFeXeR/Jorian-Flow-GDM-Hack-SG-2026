import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getTourByIdApiV1TourIdIsDummyGet } from '../../client';
import type { Tour, Poi } from '../../client/types.gen';
import MapContainer from '../Map/MapContainer';
import TourDrawer from './TourDrawer';
import AudioPlayer, { type AudioPlayerRef } from '../Audio/AudioPlayer';

const TourView: React.FC = () => {
    const { tourId, stopOrder } = useParams<{ tourId: string; stopOrder?: string }>();
    const navigate = useNavigate();
    const [tour, setTour] = useState<Tour | null>(null);
    const [currentStopIndex, setCurrentStopIndex] = useState<number | null>(null); // null means introduction
    const [currentAudioText, setCurrentAudioText] = useState<string>('');
    const audioPlayerRef = useRef<AudioPlayerRef>(null);

    // Fetch tour data
    useEffect(() => {
        if (!tourId) return;

        const fetchTour = async () => {
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
            } catch (error) {
                console.error('Error loading tour:', error);
            }
        };

        fetchTour();
    }, [tourId]);

    // Update stop index based on route parameter
    useEffect(() => {
        if (!tour) return;

        if (!stopOrder) {
            setCurrentStopIndex(null); // Introduction
            if (tour.introduction) {
                setCurrentAudioText(tour.introduction);
            }
            return;
        }

        const orderNum = parseInt(stopOrder, 10);
        if (!isNaN(orderNum) && tour.pois) {
            // Find POI by order in sorted array
            const sortedPois = [...tour.pois].sort((a, b) => (a.order || 0) - (b.order || 0));
            const poiIndex = sortedPois.findIndex(poi => poi.order === orderNum);
            if (poiIndex !== -1) {
                setCurrentStopIndex(poiIndex);
                const poi = sortedPois[poiIndex];
                if (poi?.story) {
                    setCurrentAudioText(poi.story);
                }
            }
        }
    }, [tour, stopOrder]);

    // Initialize audio text with introduction if no stopOrder
    useEffect(() => {
        if (tour && !stopOrder && currentStopIndex === null && tour.introduction) {
            setCurrentAudioText(tour.introduction);
        }
    }, [tour, stopOrder, currentStopIndex]);

    // Pan map to POI location when on a stop
    useEffect(() => {
        if (tour && currentStopIndex !== null && tour.pois && currentStopIndex < tour.pois.length) {
            const poi = tour.pois[currentStopIndex];
            if (poi?.gps_location) {
                // MapContainer will handle panning via activePoiIndex prop
            }
        }
    }, [tour, currentStopIndex]);

    const sortedPois = tour?.pois ? [...tour.pois].sort((a, b) => (a.order || 0) - (b.order || 0)) : [];
    const currentPoi = currentStopIndex !== null && sortedPois[currentStopIndex] ? sortedPois[currentStopIndex] : null;

    const handleNextStop = () => {
        if (!tour) return;
        
        if (currentStopIndex === null) {
            // From introduction, go to first POI
            if (sortedPois.length > 0) {
                const firstOrder = sortedPois[0].order;
                navigate(`/tour/${tourId}/${firstOrder}`);
            }
        } else if (currentStopIndex < sortedPois.length - 1) {
            // Go to next POI
            const nextOrder = sortedPois[currentStopIndex + 1].order;
            navigate(`/tour/${tourId}/${nextOrder}`);
        }
    };

    const handlePrevStop = () => {
        if (!tour) return;
        
        if (currentStopIndex === null) {
            // Can't go back from introduction
            return;
        } else if (currentStopIndex === 0) {
            // Go back to introduction
            navigate(`/tour/${tourId}`);
        } else {
            // Go to previous POI
            const prevOrder = sortedPois[currentStopIndex - 1].order;
            navigate(`/tour/${tourId}/${prevOrder}`);
        }
    };

    const handlePoiClick = (poi: Poi) => {
        if (!tour) return;
        navigate(`/tour/${tourId}/${poi.order}`);
    };

    return (
        <div className="relative w-full h-screen overflow-hidden bg-gray-100 flex flex-col">
            {/* Map takes up the full screen behind the drawer */}
            <div className="absolute inset-0">
                <MapContainer 
                    showTourContent={true} 
                    pois={tour?.pois || []}
                    activePoiIndex={currentStopIndex}
                />
            </div>

            {/* Hidden Audio Player */}
            {currentAudioText && (
                <AudioPlayer
                    ref={audioPlayerRef}
                    text={currentAudioText}
                    autoPlay={currentStopIndex === null}
                    hidden={true}
                />
            )}

            {/* Drawer Component */}
            {tour && (
                <TourDrawer
                    tour={tour}
                    currentStopIndex={currentStopIndex}
                    currentPoi={currentPoi}
                    currentAudioText={currentAudioText}
                    sortedPois={sortedPois}
                    onNext={handleNextStop}
                    onPrev={handlePrevStop}
                    onPoiClick={handlePoiClick}
                    audioPlayerRef={audioPlayerRef}
                />
            )}
        </div>
    );
};

export default TourView;
