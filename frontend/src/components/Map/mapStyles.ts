export const cleanMapStyles = [
    // 1. Start by hiding all labels globally
    {
        "featureType": "all",
        "elementType": "labels",
        "stylers": [{ "visibility": "off" }]
    },
    // 2. Bring back Street Names (minimalist)
    {
        "featureType": "road",
        "elementType": "labels",
        "stylers": [{ "visibility": "on" }]
    },
    // 3. Bring back specific Landmarks (POIs) 
    // You can be specific here to avoid "too many things"
    {
        "featureType": "poi.park",
        "elementType": "labels",
        "stylers": [{ "visibility": "on" }]
    },
    {
        "featureType": "poi.attraction",
        "elementType": "labels",
        "stylers": [{ "visibility": "on" }]
    },
    // 4. Hide transit and other clutter entirely
    {
        "featureType": "transit",
        "stylers": [{ "visibility": "off" }]
    }
];