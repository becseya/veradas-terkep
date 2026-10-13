<script>
  import { onMount } from 'svelte';
  import FilterPanel from './FilterPanel.svelte';
  import InspectorPanel from './InspectorPanel.svelte';
  import SubscribePanel from './SubscribePanel.svelte';
  import { mapState } from '../stores/mapState.js';

  export let filters;

  let filtersCollapsed = false;
  let isMobile = false;

  onMount(() => {
    const mediaQuery = window.matchMedia('(max-width: 768px)');

    const syncViewportState = () => {
      isMobile = mediaQuery.matches;
    };

    syncViewportState();
    mediaQuery.addEventListener('change', syncViewportState);

    return () => mediaQuery.removeEventListener('change', syncViewportState);
  });

  $: filtersCollapsed = $mapState.selectedLocation ? true : isMobile;
</script>

<aside class="sidebar-shell">
  <InspectorPanel
    visible={Boolean($mapState.selectedLocation)}
    bind:location={$mapState.selectedLocation}
  />

  <FilterPanel
    bind:collapsed={filtersCollapsed}
    bind:filters
  />

  <SubscribePanel />
</aside>
