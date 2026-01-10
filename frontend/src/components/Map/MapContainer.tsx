import { useEffect, useState, useMemo } from 'react';
import { APIProvider, Map as GoogleMap, useMap, AdvancedMarker } from '@vis.gl/react-google-maps';
import { useTour } from '../../context/TourContext';
import type { TourStop } from '../../data/tourData';
import StopMarker from './StopMarker';
import TourRoute from './TourRoute';
import { cleanMapStyles } from './mapStyles';
import type { Poi } from '../../client/types.gen';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

interface MapContentProps {
    showTourContent?: boolean;
    pois?: Poi[];
    activePoiIndex?: number | null;
    userLocation?: { lat: number; lng: number } | null;
}

const MapContent = ({ showTourContent = true, pois, activePoiIndex, userLocation }: MapContentProps) => {
    const { tour, currentStop, goToStop } = useTour();
    const map = useMap();
    // Default user position if not provided (fallback)
    const defaultUserPosition = { lat: 1.2865, lng: 103.8540 };
    const userPosition = userLocation || defaultUserPosition;
    const [poiPositions, setPoiPositions] = useState<Map<string, { lat: number; lng: number }>>(new Map());

    // Convert POIs to positions using GPS location directly from POI
    useEffect(() => {
        if (!pois || pois.length === 0 || !map) return;

        const positionsMap = new Map<string, { lat: number; lng: number }>();

        for (const poi of pois) {
            // Use GPS location directly from POI if available
            if (poi.gps_location && poi.gps_location.lat && poi.gps_location.lng) {
                const key = poi.google_place_id || poi.address || `poi-${poi.order}`;
                positionsMap.set(key, {
                    lat: poi.gps_location.lat,
                    lng: poi.gps_location.lng,
                });
            }
        }

        if (positionsMap.size > 0) {
            setPoiPositions(new Map(positionsMap));
        }
    }, [pois, map]);

    // Create stops from POIs with positions
    const poiStops = useMemo(() => {
        if (!pois || pois.length === 0) return [];
        
        return pois
            .map((poi) => {
                // Try to get position from poiPositions map first (for compatibility)
                const key = poi.google_place_id || poi.address || `poi-${poi.order}`;
                let position = poiPositions.get(key);
                
                // If not in map, try to use GPS location directly from POI
                if (!position && poi.gps_location && poi.gps_location.lat && poi.gps_location.lng) {
                    position = {
                        lat: poi.gps_location.lat,
                        lng: poi.gps_location.lng,
                    };
                }
                
                if (!position) return null;

                return {
                    id: poi.order,
                    name: poi.poi_title || poi.google_maps_name || 'Unknown',
                    position,
                    imageUrl: poi.google_place_img_url || '',
                    audioUrl: '',
                };
            })
            .filter((stop) => stop !== null)
            .sort((a, b) => (a?.id || 0) - (b?.id || 0)) as Array<{
                id: number;
                name: string;
                position: { lat: number; lng: number };
                imageUrl: string;
                audioUrl: string;
            }>;
    }, [pois, poiPositions]);

    const animateCameraTo = (target: { center: google.maps.LatLngLiteral; zoom: number; tilt?: number; heading?: number }, duration: number = 1500) => {
        if (!map) return;
        const startCenter = map.getCenter();
        const startZoom = map.getZoom();
        const startTilt = map.getTilt() || 0;
        const startHeading = map.getHeading() || 0;

        if (!startCenter || startZoom === undefined) {
            map.moveCamera({
                center: target.center,
                zoom: target.zoom,
                tilt: target.tilt ?? 0,
                heading: target.heading ?? 0
            });
            return;
        }

        const startTime = performance.now();
        const startLat = startCenter.lat();
        const startLng = startCenter.lng();

        const animate = (now: number) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const ease = 1 - Math.pow(1 - progress, 3); // easeOutCubic

            map.moveCamera({
                center: {
                    lat: startLat + (target.center.lat - startLat) * ease,
                    lng: startLng + (target.center.lng - startLng) * ease
                },
                zoom: startZoom + (target.zoom - startZoom) * ease,
                tilt: startTilt + ((target.tilt ?? 0) - startTilt) * ease,
                heading: startHeading + ((target.heading ?? 0) - startHeading) * ease
            });

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    };

    // Fly to active POI when it changes (only when showing tour content)
    useEffect(() => {
        if (showTourContent && map && activePoiIndex !== null && activePoiIndex !== undefined && pois && pois.length > 0) {
            // Sort POIs by order to match the sorted array in TourView
            const sortedPois = [...pois].sort((a, b) => (a.order || 0) - (b.order || 0));
            if (activePoiIndex < sortedPois.length) {
                const activePoi = sortedPois[activePoiIndex];
                if (activePoi?.gps_location && activePoi.gps_location.lat && activePoi.gps_location.lng) {
                    animateCameraTo({
                        center: {
                            lat: activePoi.gps_location.lat,
                            lng: activePoi.gps_location.lng,
                        },
                        zoom: 17,
                        tilt: 45,
                        heading: 0
                    });
                }
            }
        } else if (showTourContent && map && currentStop && activePoiIndex === undefined) {
            // Fallback to TourContext behavior if activePoiIndex not provided
            animateCameraTo({
                center: currentStop.position,
                zoom: 17,
                tilt: 45,
                heading: 0
            });
        }
    }, [map, currentStop, showTourContent, activePoiIndex, pois]);

    if (!showTourContent) {
        // Simple map view for onboarding
        return (
            <>
                {/* User Position Marker */}
                <AdvancedMarker
                    position={userPosition}
                >
                    <div style={{
                        width: '16px',
                        height: '16px',
                        backgroundColor: '#4285F4',
                        borderRadius: '50%',
                        border: '3px solid white',
                        boxShadow: '0 0 8px rgba(0,0,0,0.3)',
                        transform: 'translate(-50%, -50%)'
                    }} />
                </AdvancedMarker>
            </>
        );
    }

    // Use POI stops if available, otherwise use tour stops
    const stopsToShow = poiStops.length > 0 ? poiStops : tour.stops;

    // Determine active stop based on activePoiIndex if provided, otherwise use TourContext
    const getIsActive = (stop: any) => {
        if (activePoiIndex !== null && activePoiIndex !== undefined && pois) {
            const sortedPois = [...pois].sort((a, b) => (a.order || 0) - (b.order || 0));
            if (activePoiIndex < sortedPois.length) {
                const activePoi = sortedPois[activePoiIndex];
                return stop.id === activePoi.order;
            }
            return false;
        }
        return stop.id === currentStop?.id;
    };

    return (
        <>
            {stopsToShow.length >= 2 && <TourRoute stops={stopsToShow as any} />}
            {stopsToShow.map((stop, index: number) => (
                <StopMarker
                    key={stop.id}
                    index={index}
                    stop={stop as TourStop}
                    isActive={getIsActive(stop)}
                    onClick={() => {
                        if (activePoiIndex !== null && activePoiIndex !== undefined && pois) {
                            // If activePoiIndex is provided, don't use TourContext
                            return;
                        }
                        goToStop(index);
                    }}
                />
            ))}

            {/* User Position Marker */}
            <AdvancedMarker
                position={userPosition}
            >
                <div style={{
                    width: '16px',
                    height: '16px',
                    backgroundColor: '#4285F4',
                    borderRadius: '50%',
                    border: '3px solid white',
                    boxShadow: '0 0 8px rgba(0,0,0,0.3)',
                    transform: 'translate(-50%, -50%)'
                }} />
            </AdvancedMarker>

            {/* Recenter Button */}
            <button
                style={{
                    position: 'absolute',
                    top: '20px',
                    right: '20px',
                    backgroundColor: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '48px',
                    height: '48px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
                    cursor: 'pointer',
                    zIndex: 1000 // Ensure it's above the map
                }}
                onClick={() => {
                    animateCameraTo({
                        center: userPosition,
                        zoom: 16,
                        tilt: 0,
                        heading: 0
                    });
                }}
            >
                <div style={{ // Target Icon
                    width: '20px',
                    height: '20px',
                    border: '2px solid #666',
                    borderRadius: '50%',
                    position: 'relative',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <div style={{ width: '6px', height: '6px', backgroundColor: '#666', borderRadius: '50%' }} />
                    <div style={{ position: 'absolute', top: -4, left: 8, width: 2, height: 4, backgroundColor: '#666' }} />
                    <div style={{ position: 'absolute', bottom: -4, left: 8, width: 2, height: 4, backgroundColor: '#666' }} />
                    <div style={{ position: 'absolute', left: -4, top: 8, width: 4, height: 2, backgroundColor: '#666' }} />
                    <div style={{ position: 'absolute', right: -4, top: 8, width: 4, height: 2, backgroundColor: '#666' }} />
                </div>
            </button>
        </>
    );
};

interface MapContainerProps {
    height?: string;
    showTourContent?: boolean;
    pois?: Poi[];
    activePoiIndex?: number | null;
    userLocation?: { lat: number; lng: number } | null;
}

const MapContainer = ({ height = '100dvh', showTourContent = true, pois, activePoiIndex, userLocation }: MapContainerProps) => {
    // Use user location if available, otherwise default to Merlion
    const defaultCenter = userLocation || { lat: 1.2868, lng: 103.8545 };

    return (
        <div style={{ width: '100%', height }}>
            <APIProvider apiKey={API_KEY}>
                <GoogleMap
                    defaultCenter={defaultCenter}
                    defaultZoom={14}
                    disableDefaultUI={true}
                    gestureHandling={'greedy'}
                    reuseMaps={true}
                    mapId="DEMO_MAP_ID"
                    styles={cleanMapStyles}
                    // Explicitly enable gestures that might be restricted
                    zoomControl={false}
                    scrollwheel={true}
                    disableDoubleClickZoom={false}
                    draggable={true}
                >
                    <MapContent showTourContent={showTourContent} pois={pois} activePoiIndex={activePoiIndex} userLocation={userLocation} />
                </GoogleMap>
            </APIProvider>
        </div>
    );
};

export default MapContainer;
