export interface TourStop {
    id: number;
    name: string;
    position: { lat: number; lng: number };
    imageUrl: string;
    audioUrl: string;
}

import tourJson from './tour.json';

export const tourData: { stops: TourStop[] } = {
    stops: tourJson.map((stop: any) => ({
        ...stop,
        position: stop.location
    }))
};
