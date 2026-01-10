import React, { useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import type { PanInfo } from 'framer-motion';
import { SkipBack, SkipForward } from 'lucide-react';
import AudioControls from '../Audio/AudioControls';
import { useTour } from '../../context/TourContext';

const Drawer: React.FC = () => {
    const { currentStop, nextStop, prevStop } = useTour();
    const [isOpen, setIsOpen] = useState(false);
    const controls = useAnimation();

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
            <div className="px-6 flex flex-col h-full">
                {/* Header Section (Always visible in closed state) */}
                <div className="flex flex-col items-center mb-6">
                    <div className="flex items-center justify-between w-full mb-1">
                        <button
                            onClick={(e) => { e.stopPropagation(); prevStop(); }}
                            className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
                            aria-label="Previous Stop"
                        >
                            <SkipBack size={24} />
                        </button>

                        <h2 className="text-2xl font-bold text-slate-900 text-center tracking-tight flex-1 px-2 truncate">
                            {currentStop.name}
                        </h2>

                        <button
                            onClick={(e) => { e.stopPropagation(); nextStop(); }}
                            className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
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
                    <div className="w-full h-56 rounded-3xl overflow-hidden mb-8 shadow-lg shadow-blue-900/5 ring-1 ring-black/5">
                        <img
                            src={currentStop.imageUrl}
                            alt={currentStop.name}
                            className="w-full h-full object-cover"
                        />
                    </div>
                    <div className="prose prose-sm max-w-none text-gray-600">
                        <p>
                            This is a dummy description for {currentStop.name}. In a real application,
                            this would contain interesting facts, history, and details about the landmark.
                        </p>
                        <p className="mt-4">
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
                            incididunt ut labore et dolore magna aliqua.
                        </p>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default Drawer;
