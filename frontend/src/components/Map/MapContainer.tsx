import React, { useEffect, useState, useMemo } from 'react';
import { APIProvider, Map, useMap, AdvancedMarker } from '@vis.gl/react-google-maps';
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
}

const MapContent = ({ showTourContent = true, pois }: MapContentProps) => {
    const { tour, currentStop, goToStop } = useTour();
    const map = useMap();
    // Dummy user position near the first stop
    const [userPosition] = useState({ lat: 1.2865, lng: 103.8540 });
    const [poiPositions, setPoiPositions] = useState<Map<string, { lat: number; lng: number }>>(new Map());

    // Convert POIs to positions using Google Geocoding
    useEffect(() => {
        if (!pois || pois.length === 0 || !window.google || !map) return;

        const geocoder = new google.maps.Geocoder();
        const positionsMap = new Map<string, { lat: number; lng: number }>();

        // Create a dummy div for PlacesService (it requires a DOM element)
        const dummyDiv = document.createElement('div');

        const geocodePois = async () => {
            for (const poi of pois) {
                if (poi.google_place_id) {
                    // Use place_id if available
                    try {
                        const service = new google.maps.places.PlacesService(dummyDiv);
                        service.getDetails(
                            {
                                placeId: poi.google_place_id,
                                fields: ['geometry'],
                            },
                            (place, status) => {
                                if (status === google.maps.places.PlacesServiceStatus.OK && place?.geometry?.location) {
                                    positionsMap.set(poi.google_place_id, {
                                        lat: place.geometry.location.lat(),
                                        lng: place.geometry.location.lng(),
                                    });
                                    setPoiPositions(new Map(positionsMap));
                                }
                            }
                        );
                    } catch (error) {
                        console.error('Error getting place details:', error);
                        // Fallback to geocoding address if place details fail
                        if (poi.address) {
                            geocoder.geocode({ address: poi.address }, (results, status) => {
                                if (status === google.maps.GeocoderStatus.OK && results && results[0]) {
                                    const location = results[0].geometry.location;
                                    positionsMap.set(poi.google_place_id || poi.address || '', {
                                        lat: location.lat(),
                                        lng: location.lng(),
                                    });
                                    setPoiPositions(new Map(positionsMap));
                                }
                            });
                        }
                    }
                } else if (poi.address) {
                    // Fallback to geocoding address
                    geocoder.geocode({ address: poi.address }, (results, status) => {
                        if (status === google.maps.GeocoderStatus.OK && results && results[0]) {
                            const location = results[0].geometry.location;
                            positionsMap.set(poi.google_place_id || poi.address || '', {
                                lat: location.lat(),
                                lng: location.lng(),
                            });
                            setPoiPositions(new Map(positionsMap));
                        }
                    });
                }
            }
        };

        geocodePois();
    }, [pois, map]);

    // Create stops from POIs with positions
    const poiStops = useMemo(() => {
        if (!pois || pois.length === 0) return [];
        
        return pois
            .map((poi) => {
                const position = poiPositions.get(poi.google_place_id || poi.address || '');
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

    // Fly to current stop when it changes (only when showing tour content)
    useEffect(() => {
        if (showTourContent && map && currentStop) {
            animateCameraTo({
                center: currentStop.position,
                zoom: 17,
                tilt: 45,
                heading: 0
            });
        }
    }, [map, currentStop, showTourContent]);

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

    return (
        <>
            {stopsToShow.length >= 2 && <TourRoute stops={stopsToShow as any} />}
            {stopsToShow.map((stop, index: number) => (
                <StopMarker
                    key={stop.id}
                    index={index}
                    stop={stop as TourStop}
                    isActive={stop.id === currentStop?.id}
                    onClick={() => goToStop(index)}
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
}

const MapContainer = ({ height = '100dvh', showTourContent = true, pois }: MapContainerProps) => {
    const defaultCenter = { lat: 1.2868, lng: 103.8545 }; // Default to Merlion

    return (
        <div style={{ width: '100%', height }}>
            <APIProvider apiKey={API_KEY}>
                <Map
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
                    <MapContent showTourContent={showTourContent} pois={pois} />
                </Map>
            </APIProvider>
        </div>
    );
};

export default MapContainer;
