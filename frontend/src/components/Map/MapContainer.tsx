import { useEffect, useState } from 'react';
import { APIProvider, Map, useMap, AdvancedMarker } from '@vis.gl/react-google-maps';
import { useTour } from '../../context/TourContext';
import type { TourStop } from '../../data/tourData';
import StopMarker from './StopMarker';
import TourRoute from './TourRoute';
import { cleanMapStyles } from './mapStyles';

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || '';

interface MapContentProps {
    showTourContent?: boolean;
}

const MapContent = ({ showTourContent = true }: MapContentProps) => {
    const { tour, currentStop, goToStop } = useTour();
    const map = useMap();
    // Dummy user position near the first stop
    const [userPosition] = useState({ lat: 1.2865, lng: 103.8540 });

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

    return (
        <>
            <TourRoute stops={tour.stops} />
            {tour.stops.map((stop: TourStop, index: number) => (
                <StopMarker
                    key={stop.id}
                    index={index}
                    stop={stop}
                    isActive={stop.id === currentStop.id}
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
}

const MapContainer = ({ height = '100dvh', showTourContent = true }: MapContainerProps) => {
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
                    <MapContent showTourContent={showTourContent} />
                </Map>
            </APIProvider>
        </div>
    );
};

export default MapContainer;
