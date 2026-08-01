<script>
  import { onMount } from 'svelte';
  import Map from './lib/components/Map.svelte';
  import Sidebar from './lib/components/Sidebar.svelte';
  import { DEFAULT_FILTERS, filterLocations } from './lib/utils/filtering.js';
  import { mapState } from './lib/stores/mapState.js';

  let allLocations = [];
  let filteredLocations = [];
  let filters = { ...DEFAULT_FILTERS };

  onMount(async () => {
    allLocations = LOCATIONS ?? [];
    console.log('Loaded locations:', allLocations);
    filteredLocations = allLocations;
  });

  $: filteredLocations = filterLocations(allLocations, filters);

  $: if (
    $mapState.selectedLocation &&
    !filteredLocations.some((location) => location.name === $mapState.selectedLocation.name)
  ) {
    $mapState.selectedLocation = null;
  }
</script>

<main class="layout">
  <Map locations={filteredLocations} />

  <Sidebar bind:filters />
</main>
