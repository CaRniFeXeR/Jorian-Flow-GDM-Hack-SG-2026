import React, { useEffect, useState } from 'react';
import { useMap } from '@vis.gl/react-google-maps';
import type { TourStop } from '../../data/tourData';

interface TourRouteProps {
    stops: TourStop[];
}

const TourRoute: React.FC<TourRouteProps> = ({ stops }) => {
    const map = useMap();
    const [directionsRenderer, setDirectionsRenderer] = useState<google.maps.DirectionsRenderer | null>(null);

    useEffect(() => {
        if (!map) return;

        const dr = new google.maps.DirectionsRenderer({
            map,
            suppressMarkers: true,
            polylineOptions: {
                strokeColor: '#4285F4',
                strokeOpacity: 0,
                strokeWeight: 0,
                icons: [{
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        fillOpacity: 1,
                        scale: 3,
                        fillColor: '#4285F4',
                    },
                    offset: '0',
                    repeat: '12px'
                }]
            }
        });

        setDirectionsRenderer(dr);

        return () => {
            dr.setMap(null);
        };
    }, [map]);

    useEffect(() => {
        // Need at least 2 stops: user location (start) + at least 1 POI + user location (end)
        // Or at least 1 POI between start and end user locations
        if (!directionsRenderer || stops.length < 3) return;

        const directionsService = new google.maps.DirectionsService();

        // The route should start and end at user location (first and last stop)
        // and go through all POIs (middle stops) as waypoints
        const userLocation = stops[0].position;
        const poiStops = stops.slice(1, -1); // All stops except first (user start) and last (user end)

        if (poiStops.length === 0) {
            // No POIs, just return (no route to draw)
            return;
        }

        const waypoints = poiStops.map(stop => ({
            location: stop.position,
            stopover: true
        }));

        // Route: user location -> POIs -> back to user location
        directionsService.route({
            origin: userLocation,
            destination: userLocation, // Tour ends back at starting location
            waypoints: waypoints, // All POIs are intermediate waypoints
            travelMode: google.maps.TravelMode.WALKING,
            optimizeWaypoints: false // Keep the order as specified
        }, (result, status) => {
            if (status === google.maps.DirectionsStatus.OK) {
                directionsRenderer.setDirections(result);
            } else {
                console.error(`Directions request failed: ${status}`);
            }
        });
    }, [directionsRenderer, stops]);

    return null;
};

export default TourRoute;
