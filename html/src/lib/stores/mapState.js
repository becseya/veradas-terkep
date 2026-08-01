import { writable } from 'svelte/store';

const DEFAULT_ZONE_RADIUS_KM = 2.5;

// Shared selected state for map, sidebar, and app-level effects.
export const mapState = writable({
    selectedLocation: null,
    subscriptionZone: {
        coords: null,
        radiusKm: DEFAULT_ZONE_RADIUS_KM,
    }
});
