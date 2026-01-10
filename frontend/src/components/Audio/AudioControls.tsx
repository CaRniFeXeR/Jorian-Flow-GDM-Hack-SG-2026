import React from 'react';
import { Play, Pause, RotateCcw, RotateCw } from 'lucide-react';
import { useTour } from '../../context/TourContext';

const AudioControls: React.FC = () => {
    const { isPlaying, setPlaying } = useTour();

    return (
        <div className="flex items-center justify-center gap-6 w-full max-w-sm mx-auto py-4">
            {/* 15s Back */}
            <button
                className="group relative flex items-center justify-center w-14 h-14 rounded-full bg-white border border-indigo-100 text-indigo-500 shadow-sm hover:shadow-md hover:border-indigo-200 hover:bg-indigo-50 active:scale-95 transition-all duration-200"
                aria-label="Rewind 15 seconds"
            >
                <div className="relative">
                    <RotateCcw size={24} strokeWidth={2} />
                    <span className="absolute top-[52%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[9px] font-extrabold text-indigo-600/90 select-none">15</span>
                </div>
            </button>

            {/* Play/Pause - Gemini FAB Style */}
            <button
                onClick={() => setPlaying(!isPlaying)}
                className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-[#4E75F6] to-[#7A5AF8] rounded-[2rem] text-white shadow-xl shadow-blue-500/25 hover:shadow-blue-500/40 hover:scale-105 active:scale-95 transition-all duration-300 ring-4 ring-white/50"
                aria-label={isPlaying ? "Pause" : "Play"}
            >
                {isPlaying ? (
                    <Pause size={36} fill="currentColor" strokeWidth={0} />
                ) : (
                    <Play size={36} fill="currentColor" strokeWidth={0} className="ml-1" />
                )}
            </button>

            {/* 15s Forward */}
            <button
                className="group relative flex items-center justify-center w-14 h-14 rounded-full bg-white border border-indigo-100 text-indigo-500 shadow-sm hover:shadow-md hover:border-indigo-200 hover:bg-indigo-50 active:scale-95 transition-all duration-200"
                aria-label="Skip forward 15 seconds"
            >
                <div className="relative">
                    <RotateCw size={24} strokeWidth={2} />
                    <span className="absolute top-[52%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[9px] font-extrabold text-indigo-600/90 select-none">15</span>
                </div>
            </button>
        </div>
    );
};

export default AudioControls;
