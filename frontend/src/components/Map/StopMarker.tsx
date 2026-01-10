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
                borderColor={'#FFFFFF'}
                glyphColor={'#FFFFFF'}
                glyph={(index + 1).toString()}
                scale={isActive ? 1.2 : 1}
            />
        </AdvancedMarker>
    );
};

export default StopMarker;
