import React, { useEffect } from 'react';
import { useMap } from '@vis.gl/react-google-maps';

interface MapUpdaterProps {
    center: { lat: number; lng: number };
}

const MapUpdater: React.FC<MapUpdaterProps> = ({ center }) => {
    const map = useMap();

    useEffect(() => {
        if (map) {
            map.panTo(center);
            map.setZoom(16);
        }
    }, [map, center]);

    return null;
};

export default MapUpdater;
