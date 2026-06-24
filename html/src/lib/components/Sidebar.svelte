<script>
  import FilterPanel from './FilterPanel.svelte';
  import InspectorPanel from './InspectorPanel.svelte';

  export let selectedLocation = null;
  export let filters;

  let filtersCollapsed = false;

  $: if (selectedLocation) {
    filtersCollapsed = true;
  }
</script>

<aside class="sidebar-shell">
  <InspectorPanel
    visible={Boolean(selectedLocation)}
    bind:location={selectedLocation}
  />

  <FilterPanel
    bind:collapsed={filtersCollapsed}
    bind:filters
  />
</aside>
