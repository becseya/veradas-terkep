import { writable } from 'svelte/store';

// Shared selected state for map, sidebar, and app-level effects.
export const mapState = writable({
    selectedLocation: null,
});
