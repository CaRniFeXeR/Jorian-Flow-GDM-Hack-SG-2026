import React, { useState, useEffect } from 'react';
import { motion, useAnimation } from 'framer-motion';
import type { PanInfo } from 'framer-motion';
import { SkipBack, SkipForward } from 'lucide-react';
import AudioControls from '../Audio/AudioControls';
import TourStopsList from './TourStopsList';
import type { Tour, Poi } from '../../client/types.gen';
import type { AudioPlayerRef } from '../Audio/AudioPlayer';

interface TourDrawerProps {
    tour: Tour;
    currentStopIndex: number | null; // null means introduction
    currentPoi: Poi | null;
    currentAudioText: string;
    sortedPois: Poi[];
    onNext: () => void;
    onPrev: () => void;
    onPoiClick: (poi: Poi) => void;
    audioPlayerRef: React.RefObject<AudioPlayerRef | null>;
}

const TourDrawer: React.FC<TourDrawerProps> = ({
    tour,
    currentStopIndex,
    currentPoi,
    currentAudioText,
    sortedPois,
    onNext,
    onPrev,
    onPoiClick,
    audioPlayerRef,
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const controls = useAnimation();

    // Sync audio player state with isPlaying
    useEffect(() => {
        if (audioPlayerRef.current) {
            const interval = setInterval(() => {
                if (audioPlayerRef.current) {
                    const playing = audioPlayerRef.current.isPlaying();
                    setIsPlaying(playing);
                }
            }, 100);
            return () => clearInterval(interval);
        }
    }, [audioPlayerRef]);

    const toggleDrawer = () => {
        setIsOpen(!isOpen);
        controls.start(isOpen ? "closed" : "open");
    };

    const onDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
        if (info.offset.y < -100 && !isOpen) {
            setIsOpen(true);
            controls.start("open");
        }
        else if (info.offset.y > 100 && isOpen) {
            setIsOpen(false);
            controls.start("closed");
        } else {
            controls.start(isOpen ? "open" : "closed");
        }
    };

    const variants = {
        open: { y: "15%" },
        closed: { y: "85%" }
    };

    const currentTitle = currentStopIndex === null 
        ? tour.theme || 'Tour Introduction'
        : currentPoi?.poi_title || currentPoi?.google_maps_name || 'Stop';

    const currentImage = currentPoi?.google_place_img_url || '';

    const currentDescription = currentStopIndex === null
        ? tour.introduction || ''
        : currentPoi?.story || '';

    return (
        <motion.div
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.2}
            onDragEnd={onDragEnd}
            animate={controls}
            initial="closed"
            variants={variants}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="absolute bottom-0 left-0 right-0 bg-gradient-to-b from-white/95 to-slate-50/95 backdrop-blur-2xl rounded-t-[2.5rem] shadow-[0_-10px_40px_-15px_rgba(0,0,0,0.1)] z-10 h-screen flex flex-col border-t border-white/50"
            style={{ touchAction: "none", backgroundColor: "#fff" }}
        >
            {/* Handle */}
            <div className="w-full flex justify-center pt-4 pb-2 cursor-pointer" onClick={toggleDrawer}>
                <div className="w-16 h-1.5 bg-slate-200/80 rounded-full" />
            </div>

            {/* Content */}
            <div className="px-2 flex flex-col h-full">
                {/* Header Section (Always visible in closed state) */}
                <div className="flex flex-col items-center mb-6">
                    <div className="flex items-center justify-between w-full mb-1">
                        <button
                            onClick={(e) => { e.stopPropagation(); onPrev(); }}
                            disabled={currentStopIndex === null}
                            className={`p-2 rounded-full transition-colors ${
                                currentStopIndex === null
                                    ? 'text-slate-300 cursor-not-allowed'
                                    : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'
                            }`}
                            aria-label="Previous Stop"
                        >
                            <SkipBack size={24} />
                        </button>

                        <h2 className="text-2xl font-bold text-slate-900 text-center tracking-tight flex-1 px-2 truncate">
                            {currentTitle}
                        </h2>

                        <button
                            onClick={(e) => { e.stopPropagation(); onNext(); }}
                            disabled={currentStopIndex !== null && sortedPois.length > 0 && currentStopIndex >= sortedPois.length - 1}
                            className={`p-2 rounded-full transition-colors ${
                                currentStopIndex !== null && sortedPois.length > 0 && currentStopIndex >= sortedPois.length - 1
                                    ? 'text-slate-300 cursor-not-allowed'
                                    : 'text-slate-400 hover:text-blue-600 hover:bg-blue-50'
                            }`}
                            aria-label="Next Stop"
                        >
                            <SkipForward size={24} />
                        </button>
                    </div>
                    <p className="text-sm text-slate-500 font-medium tracking-wide uppercase mb-6">Audio Tour</p>

                    {/* Audio Controls */}
                    <AudioControls />
                </div>

                {/* Expanded Content (Visible when open) */}
                <div className="flex-1 overflow-y-auto pb-24 no-scrollbar">
                    {/* Introduction or POI Image */}
                    {currentStopIndex === null ? (
                        <div className="mb-8">
                            <div className="prose prose-sm max-w-none text-gray-600">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Welcome to your tour!</h3>
                                <div className="whitespace-pre-line">
                                    {currentDescription}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <>
                            {currentImage && (
                                <div className="w-full h-56 rounded-3xl overflow-hidden mb-8 shadow-lg shadow-blue-900/5 ring-1 ring-black/5">
                                    <img
                                        src={currentImage}
                                        alt={currentTitle}
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                            )}
                            <div className="prose prose-sm max-w-none text-gray-600 mb-8">
                                {currentPoi?.address && (
                                    <p className="text-sm text-gray-500 mb-4">{currentPoi.address}</p>
                                )}
                                <div className="whitespace-pre-line">
                                    {currentDescription}
                                </div>
                            </div>
                        </>
                    )}

                    {/* Tour Stops List */}
                    <TourStopsList
                        sortedPois={sortedPois}
                        currentStopIndex={currentStopIndex}
                        onPoiClick={onPoiClick}
                    />
                </div>
            </div>
        </motion.div>
    );
};

export default TourDrawer;
