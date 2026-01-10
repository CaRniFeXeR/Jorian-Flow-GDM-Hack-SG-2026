import React, { useEffect, useState } from 'react';
import { useMap, MapsComponent } from '@vis.gl/react-google-maps';

interface RouteLayerProps {
    stops: {
        id: number;
        location: { lat: number; lng: number };
    }[];
}

const RouteLayer: React.FC<RouteLayerProps> = ({ stops }) => {
    const map = useMap();
    const [directionsRenderer, setDirectionsRenderer] = useState<google.maps.DirectionsRenderer | null>(null);

    useEffect(() => {
        if (!map) return;

        // Initialize DirectionsRenderer if not already
        const dr = new google.maps.DirectionsRenderer({
            map,
            suppressMarkers: true, // We use our own markers
            polylineOptions: {
                strokeColor: '#2563eb',
                strokeOpacity: 0, // Hide the solid line
                strokeWeight: 0,
                icons: [{
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillOpacity: 1,
                        scale: 3,
                        fillColor: '#2563eb',
                    },
                    offset: '0',
                    repeat: '10px' // Dotted line effect
                }]
            }
        });

        setDirectionsRenderer(dr);

        return () => {
            dr.setMap(null);
        };
    }, [map]);

    useEffect(() => {
        if (!directionsRenderer || stops.length < 2) return;

        const directionsService = new google.maps.DirectionsService();

        // Create waypoints (excluding start and end)
        const waypoints = stops.slice(1, -1).map(stop => ({
            location: stop.location,
            stopover: true
        }));

        directionsService.route({
            origin: stops[0].location,
            destination: stops[stops.length - 1].location,
            waypoints: waypoints,
            travelMode: google.maps.TravelMode.WALKING
        }, (result, status) => {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(result);
            } else {
                console.error(`Directions request failed: ${status}`);
                // Fallback: draw straight lines if directions fail (optional)
            }
        });
    }, [directionsRenderer, stops]);

    return null;
};

export default RouteLayer;
