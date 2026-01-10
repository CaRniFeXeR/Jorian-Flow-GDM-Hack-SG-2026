import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getTourByIdApiV1TourIdIsDummyGet } from '../../client';
import type { Tour, Poi } from '../../client/types.gen';
import MapContainer from '../Map/MapContainer';
import AudioPlayer from '../Audio/AudioPlayer';
import { useTour } from '../../context/TourContext';

const TourView: React.FC = () => {
    const { tourId } = useParams<{ tourId: string }>();
    const [tour, setTour] = useState<Tour | null>(null);
    const [currentPoiIndex, setCurrentPoiIndex] = useState(0);
    const [currentAudioText, setCurrentAudioText] = useState<string>('');
    const { goToStop } = useTour();

    useEffect(() => {
        if (!tourId) return;

        const fetchTour = async () => {
            try {
                const response = await getTourByIdApiV1TourIdIsDummyGet({
                    path: { tour_id: tourId, is_dummy: true },
                    baseUrl: 'http://localhost:8000',
                });

                if (response.error) {
                    console.error('Error fetching tour:', response.error);
                    return;
                }

                const tourData = response.data as Tour;
                setTour(tourData);

                // Set introduction as initial audio text
                if (tourData.introduction && tourData.introduction.trim() !== '') {
                    setCurrentAudioText(tourData.introduction);
                }
            } catch (error) {
                console.error('Error loading tour:', error);
            }
        };

        fetchTour();
    }, [tourId]);

    // Update audio text when POI changes
    useEffect(() => {
        if (tour?.pois && tour.pois.length > 0 && currentPoiIndex < tour.pois.length) {
            const currentPoi = tour.pois[currentPoiIndex];
            if (currentPoi?.story) {
                setCurrentAudioText(currentPoi.story);
            }
        }
    }, [tour, currentPoiIndex]);

    const handlePoiChange = (index: number) => {
        setCurrentPoiIndex(index);
        goToStop(index);
    };

    const currentPoi = tour?.pois && tour.pois.length > 0 
        ? tour.pois[currentPoiIndex] 
        : null;

    return (
        <div className="relative w-full h-screen overflow-hidden bg-gray-100 flex flex-col">
            {/* Map takes up the full screen behind the drawer */}
            <div className="absolute inset-0">
                <MapContainer 
                    showTourContent={true} 
                    pois={tour?.pois || []}
                />
            </div>

            {/* Drawer for controls - we'll create a custom drawer here */}
            {tour && (
                <motion.div
                    className="absolute bottom-0 left-0 right-0 bg-gradient-to-b from-white/95 to-slate-50/95 backdrop-blur-2xl rounded-t-[2.5rem] shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.1)] z-10"
                    style={{ height: '60vh', maxHeight: '60vh' }}
                    initial={{ y: '100%' }}
                    animate={{ y: 0 }}
                    transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                >
                    <div className="p-6 h-full overflow-y-auto">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">
                            {tour.theme}
                        </h2>
                        
                        {currentPoi && (
                            <div className="mb-4">
                                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                                    {currentPoi.poi_title || currentPoi.google_maps_name || 'POI'}
                                </h3>
                                {currentPoi.address && (
                                    <p className="text-sm text-gray-600 mb-4">
                                        {currentPoi.address}
                                    </p>
                                )}
                            </div>
                        )}

                        {/* Audio Player */}
                        {currentAudioText && (
                            <div className="mb-6">
                                <AudioPlayer
                                    text={currentAudioText}
                                    autoPlay={currentPoiIndex === 0 && !currentPoi && tour.introduction === currentAudioText}
                                />
                            </div>
                        )}

                        {/* POI List */}
                        {tour.pois && tour.pois.length > 0 && (
                            <div className="space-y-2">
                                <h4 className="text-lg font-semibold text-gray-900 mb-3">
                                    Tour Stops
                                </h4>
                                {tour.pois
                                    .sort((a, b) => (a.order || 0) - (b.order || 0))
                                    .map((poi: Poi, index: number) => (
                                        <button
                                            key={poi.google_place_id || index}
                                            onClick={() => handlePoiChange(index)}
                                            className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                                                currentPoiIndex === index
                                                    ? 'border-blue-600 bg-blue-50 shadow-lg'
                                                    : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                                            }`}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-sm font-bold text-blue-600">
                                                            {poi.order || index + 1}
                                                        </span>
                                                        <span className="font-semibold text-gray-900">
                                                            {poi.poi_title || poi.google_maps_name || `Stop ${index + 1}`}
                                                        </span>
                                                    </div>
                                                    {poi.address && (
                                                        <p className="text-sm text-gray-600">
                                                            {poi.address}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        </button>
                                    ))}
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </div>
    );
};

export default TourView;
