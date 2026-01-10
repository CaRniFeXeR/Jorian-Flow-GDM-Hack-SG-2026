import React from 'react';
import { AdvancedMarker, Pin } from '@vis.gl/react-google-maps';

interface PinLayerProps {
    stops: {
        id: number;
        location: { lat: number; lng: number };
    }[];
}

const PinLayer: React.FC<PinLayerProps> = ({ stops }) => {
    return (
        <>
            {stops.map((stop) => (
                <AdvancedMarker
                    key={stop.id}
                    position={stop.location}
                >
                    <Pin
                        background={'#2563eb'}
                        borderColor={'#1d4ed8'}
                        glyphColor={'#ffffff'}
                    >
                        <span className="text-sm font-bold">{stop.id}</span>
                    </Pin>
                </AdvancedMarker>
            ))}
        </>
    );
};

export default PinLayer;
