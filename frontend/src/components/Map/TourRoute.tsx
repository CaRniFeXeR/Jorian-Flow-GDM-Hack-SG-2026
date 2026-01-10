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
        if (!directionsRenderer || stops.length < 2) return;

        const directionsService = new google.maps.DirectionsService();

        const waypoints = stops.slice(1, -1).map(stop => ({
            location: stop.position,
            stopover: true
        }));

        directionsService.route({
            origin: stops[0].position,
            destination: stops[stops.length - 1].position,
            waypoints: waypoints,
            travelMode: google.maps.TravelMode.WALKING
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
