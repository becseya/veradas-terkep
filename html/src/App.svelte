<script>
  import { onMount } from 'svelte';
  import Map from './lib/components/Map.svelte';
  import Sidebar from './lib/components/Sidebar.svelte';
  import { DEFAULT_FILTERS, filterLocations } from './lib/utils/filtering.js';

  let allLocations = [];
  let filteredLocations = [];
  let selectedLocation = null;
  let filters = { ...DEFAULT_FILTERS };

  onMount(async () => {
    allLocations = LOCATIONS ?? [];
    console.log('Loaded locations:', allLocations);
    filteredLocations = allLocations;
  });

  $: filteredLocations = filterLocations(allLocations, filters);

  $: if (
    selectedLocation &&
    !filteredLocations.some((location) => location.name === selectedLocation.name)
  ) {
    selectedLocation = null;
  }
</script>

<main class="layout">
  <Map locations={filteredLocations} bind:selectedLocation />

  <Sidebar bind:selectedLocation bind:filters />
</main>
