import React from 'react';
import { Map } from '@vis.gl/react-google-maps';
import PinLayer from './PinLayer';
import RouteLayer from './RouteLayer';
import MapUpdater from './MapUpdater';

interface MapContainerProps {
    currentStop: {
        location: { lat: number; lng: number };
    };
    stops: {
        id: number;
        location: { lat: number; lng: number };
    }[];
}

const MapContainer: React.FC<MapContainerProps> = ({ currentStop, stops }) => {
    return (
        <Map
            mapId="DEMO_MAP_ID" // Required for AdvancedMarker
            defaultCenter={stops[0].location}
            defaultZoom={15}
            gestureHandling={'greedy'} // Standard mobile gestures
            disableDefaultUI={true} // Cleaner look
            className="w-full h-full"
        >
            <MapUpdater center={currentStop.location} />
            <PinLayer stops={stops} />
            <RouteLayer stops={stops} />
        </Map>
    );
};

export default MapContainer;
