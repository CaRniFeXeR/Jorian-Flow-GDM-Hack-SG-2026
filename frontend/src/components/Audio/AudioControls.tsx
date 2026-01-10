import React from 'react';
import { Play, Pause, RotateCcw, RotateCw, SkipBack, SkipForward } from 'lucide-react';

interface AudioControlsProps {
    isPlaying: boolean;
    onTogglePlay: () => void;
    onNext: () => void;
    onPrev: () => void;
}

const AudioControls: React.FC<AudioControlsProps> = ({ isPlaying, onTogglePlay, onNext, onPrev }) => {
    return (
        <div className="flex items-center justify-between w-full max-w-sm mx-auto px-4 py-4">
            {/* Prev Station */}
            <button onClick={onPrev} className="p-2 text-gray-600 hover:text-gray-900">
                <SkipBack size={24} />
            </button>

            {/* 15s Back */}
            <button className="p-2 text-gray-600 hover:text-gray-900 relative">
                <RotateCcw size={24} />
                <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[8px] font-bold pt-1">15</span>
            </button>

            {/* Play/Pause */}
            <button
                onClick={onTogglePlay}
                className="p-4 bg-blue-600 rounded-full text-white hover:bg-blue-700 shadow-lg"
            >
                {isPlaying ? <Pause size={32} fill="currentColor" /> : <Play size={32} fill="currentColor" />}
            </button>

            {/* 15s Forward */}
            <button className="p-2 text-gray-600 hover:text-gray-900 relative">
                <RotateCw size={24} />
                <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[8px] font-bold pt-1">15</span>
            </button>

            {/* Next Station */}
            <button onClick={onNext} className="p-2 text-gray-600 hover:text-gray-900">
                <SkipForward size={24} />
            </button>
        </div>
    );
};

export default AudioControls;
