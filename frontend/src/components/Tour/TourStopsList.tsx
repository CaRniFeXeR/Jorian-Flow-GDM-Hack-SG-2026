import React from 'react';
import type { Poi } from '../../client/types.gen';

interface TourStopsListProps {
    sortedPois: Poi[];
    currentStopIndex: number | null;
    onPoiClick: (poi: Poi) => void;
}

const TourStopsList: React.FC<TourStopsListProps> = ({
    sortedPois,
    currentStopIndex,
    onPoiClick,
}) => {
    if (sortedPois.length === 0) {
        return null;
    }

    return (
        <div className="space-y-2 mb-24" >
            <h4 className="text-lg font-semibold text-gray-900 mb-3">Tour Stops</h4>
            {sortedPois.map((poi) => {
                const isCurrent = currentStopIndex !== null && sortedPois[currentStopIndex]?.order === poi.order;
                const isVisited = currentStopIndex !== null && 
                    sortedPois.findIndex(p => p.order === poi.order) < currentStopIndex;
                const isUpcoming = currentStopIndex === null || 
                    sortedPois.findIndex(p => p.order === poi.order) > currentStopIndex;

                return (
                    <button
                        key={poi.google_place_id || poi.order}
                        onClick={(e) => {
                            e.stopPropagation();
                            onPoiClick(poi);
                        }}
                        className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                            isCurrent
                                ? 'border-blue-600 bg-blue-50 shadow-lg'
                                : isVisited
                                ? 'border-green-300 bg-green-50/50 hover:border-green-400'
                                : isUpcoming
                                ? 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                                : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                        }`}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-sm font-bold ${
                                        isCurrent ? 'text-blue-600' : 
                                        isVisited ? 'text-green-600' : 
                                        'text-gray-400'
                                    }`}>
                                        {poi.order}
                                    </span>
                                    <span className="font-semibold text-gray-900">
                                        {poi.poi_title || poi.google_maps_name || `Stop ${poi.order}`}
                                    </span>
                                    {isVisited && (
                                        <span className="text-xs text-green-600 font-medium">✓ Visited</span>
                                    )}
                                    {isCurrent && (
                                        <span className="text-xs text-blue-600 font-medium">Current</span>
                                    )}
                                </div>
                                {poi.address && (
                                    <p className="text-sm text-gray-600">
                                        {poi.address}
                                    </p>
                                )}
                            </div>
                        </div>
                    </button>
                );
            })}
        </div>
    );
};

export default TourStopsList;
