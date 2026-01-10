import React from 'react';
import { Play, Pause, RotateCcw, RotateCw, SkipBack, SkipForward } from 'lucide-react';
import { useTour } from '../../context/TourContext';

const AudioControls: React.FC = () => {
    const { isPlaying, setPlaying, nextStop, prevStop } = useTour();

    return (
        <div className="flex items-center justify-between w-full max-w-sm mx-auto px-4 py-8">
            {/* Prev Station */}
            <button
                onClick={prevStop}
                className="p-3 text-slate-400 hover:text-blue-600 transition-all rounded-full hover:bg-blue-50 active:bg-blue-100"
                aria-label="Previous Stop"
            >
                <SkipBack size={26} strokeWidth={1.5} />
            </button>

            {/* 15s Back */}
            <button
                className="p-3 text-slate-500 hover:text-blue-600 transition-all rounded-full hover:bg-blue-50 active:bg-blue-100 relative group"
                aria-label="Rewind 15 seconds"
            >
                <div className="relative">
                    <RotateCcw size={30} strokeWidth={1.5} />
                    <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[10px] font-bold pt-1.5 select-none text-current opacity-80">15</span>
                </div>
            </button>

            {/* Play/Pause - Gemini FAB Style */}
            <button
                onClick={() => setPlaying(!isPlaying)}
                className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full text-white shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 active:scale-95 transition-all duration-300 border-[3px] border-white/20"
                aria-label={isPlaying ? "Pause" : "Play"}
            >
                {isPlaying ? (
                    <Pause size={38} fill="currentColor" strokeWidth={0} />
                ) : (
                    <Play size={38} fill="currentColor" strokeWidth={0} className="ml-1" />
                )}
            </button>

            {/* 15s Forward */}
            <button
                className="p-3 text-slate-500 hover:text-blue-600 transition-all rounded-full hover:bg-blue-50 active:bg-blue-100 relative group"
                aria-label="Skip forward 15 seconds"
            >
                <div className="relative">
                    <RotateCw size={30} strokeWidth={1.5} />
                    <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-[10px] font-bold pt-1.5 select-none text-current opacity-80">15</span>
                </div>
            </button>

            {/* Next Station */}
            <button
                onClick={nextStop}
                className="p-3 text-slate-400 hover:text-blue-600 transition-all rounded-full hover:bg-blue-50 active:bg-blue-100"
                aria-label="Next Stop"
            >
                <SkipForward size={26} strokeWidth={1.5} />
            </button>
        </div>
    );
};

export default AudioControls;
