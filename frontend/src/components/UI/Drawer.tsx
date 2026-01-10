import React, { useState } from 'react';
import { motion, useAnimation } from 'framer-motion';
import type { PanInfo } from 'framer-motion';
import AudioControls from '../Audio/AudioControls';

interface DrawerProps {
    currentStop: {
        name: string;
        imageUrl: string;
    };
    isPlaying: boolean;
    onTogglePlay: () => void;
    onNext: () => void;
    onPrev: () => void;
}

const Drawer: React.FC<DrawerProps> = ({ currentStop, isPlaying, onTogglePlay, onNext, onPrev }) => {
    const [isOpen, setIsOpen] = useState(false);
    const controls = useAnimation();

    const toggleDrawer = () => {
        setIsOpen(!isOpen);
        controls.start(isOpen ? "closed" : "open");
    };

    const onDragEnd = (_event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
        // If dragged up significantly, open
        if (info.offset.y < -100 && !isOpen) {
            setIsOpen(true);
            controls.start("open");
        }
        // If dragged down significantly, close
        else if (info.offset.y > 100 && isOpen) {
            setIsOpen(false);
            controls.start("closed");
        } else {
            // Snap back to current state
            controls.start(isOpen ? "open" : "closed");
        }
    };

    const variants = {
        open: { y: "15%" }, // Takes up most of the screen, leaving some map visible
        closed: { y: "85%" } // Only shows the header and controls
    };

    return (
        <motion.div
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }} // Constraints handled by controls
            dragElastic={0.2}
            onDragEnd={onDragEnd}
            animate={controls}
            initial="closed"
            variants={variants}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-[0_-5px_20px_rgba(0,0,0,0.1)] z-10 h-screen flex flex-col"
            style={{ touchAction: "none" }} // Important for drag
        >
            {/* Handle */}
            <div className="w-full flex justify-center pt-3 pb-1 cursor-pointer" onClick={toggleDrawer}>
                <div className="w-12 h-1.5 bg-gray-300 rounded-full" />
            </div>

            {/* Content */}
            <div className="px-6 flex flex-col h-full">
                {/* Header Section (Always visible in closed state) */}
                <div className="flex flex-col items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-800 text-center mb-1">{currentStop.name}</h2>
                    <p className="text-sm text-gray-500 mb-4">Audio Tour</p>

                    {/* Audio Controls */}
                    <AudioControls
                        isPlaying={isPlaying}
                        onTogglePlay={onTogglePlay}
                        onNext={onNext}
                        onPrev={onPrev}
                    />
                </div>

                {/* Expanded Content (Visible when open) */}
                <div className="flex-1 overflow-y-auto pb-24">
                    <div className="w-full h-48 rounded-2xl overflow-hidden mb-6 shadow-md">
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
