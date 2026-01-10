import React from 'react';
import { AdvancedMarker, Pin } from '@vis.gl/react-google-maps';
import type { TourStop } from '../../data/tourData';

interface StopMarkerProps {
    index: number;
    stop: TourStop;
    isActive: boolean;
    onClick: () => void;
}

const StopMarker: React.FC<StopMarkerProps> = ({ index, stop, isActive, onClick }) => {
    return (
        <AdvancedMarker
            position={stop.position}
            onClick={onClick}
        >
            <Pin
                background={isActive ? '#EA4335' : '#4285F4'}
                borderColor={'#fff'}
                glyphColor={'#fff'}
                scale={isActive ? 1.2 : 1.0}
            >
                <div style={{
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '20px',
                    height: '20px'
                }}>
                    {index + 1}
                </div>
            </Pin>
        </AdvancedMarker>
    );
};

export default StopMarker;
