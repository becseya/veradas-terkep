<script>
  import { onMount } from 'svelte';
  import L from 'leaflet';

  export let locations = [];
  export let selectedLocation = null;

  let mapElement;
  let map;
  let markersLayer;

  function createCustomIcon(isFixed) {
    const color = isFixed ? '#6f7b86' : '#bf3f2f';
    const iconClass = isFixed ? 'fa-solid fa-hospital' : 'fa-solid fa-ambulance';

    return L.divIcon({
      className: 'custom-div-icon',
      html: `<div class='marker-pin' style='background-color: ${color};'><i class='${iconClass}' style='color: white;'></i></div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15]
    });
  }

  function renderMarkers(currentLocations) {
    if (!markersLayer) {
      return;
    }

    markersLayer.clearLayers();

    currentLocations.forEach((location) => {
      const marker = L.marker(location.coords, {
        icon: createCustomIcon(location.isFixedLocation)
      }).addTo(markersLayer);

      marker.on('click', () => {
        selectedLocation = location;
      });
    });
  }

  onMount(() => {
    map = L.map(mapElement, {
      zoomControl: true
    }).setView([47.1625, 19.5033], 8);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 16,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);
    renderMarkers(locations);
  });

  $: renderMarkers(locations);
</script>

<div class="map-root" bind:this={mapElement}></div>
