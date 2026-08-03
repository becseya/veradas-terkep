<script>
  import { onMount } from 'svelte';
  import L from 'leaflet';
  import { mapState } from '../stores/mapState.js';

  export let locations = [];

  let mapElement;
  let map;
  let markersLayer;
  let subscriptionLayer;

  const colorRedPrimary = 'var(--accent)';
  const colorRedFiller = '#d96b5d';
  const colorGreyPrimary = '#6f7b86';

  function createCustomIcon(isFixed) {
    const color = isFixed ? colorGreyPrimary : colorRedPrimary;
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
        $mapState.selectedLocation = location;
      });
    });
  }

  function renderSubscriptionZone(zone) {
    if (!subscriptionLayer) {
      return;
    }

    subscriptionLayer.clearLayers();

    if (!zone.coords) {
      return;
    }

    let colorPrimary = colorRedPrimary;
    let colorFiller = colorRedFiller;

    if ($mapState.subscriptionZone.isEditable) {
      colorPrimary = colorGreyPrimary;
      colorFiller = colorGreyPrimary;
    }

    L.circle(zone.coords, {
      radius: zone.radiusKm * 1000,
      color: colorPrimary,
      weight: 2,
      fillColor: colorFiller,
      fillOpacity: 0.2,
      className: 'cursor-inherit',
    }).addTo(subscriptionLayer);

    L.circleMarker(zone.coords, {
      radius: 6,
      color: colorPrimary,
      fillColor: colorPrimary,
      fillOpacity: 0.95,
      weight: 2,
      className: 'cursor-inherit',
    }).addTo(subscriptionLayer);
  }

  onMount(() => {
    map = L.map(mapElement, {
      zoomControl: true
    }).setView([47.1625, 19.5033], 8);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 16,
      minZoom: 7,
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    markersLayer = L.layerGroup().addTo(map);
    subscriptionLayer = L.layerGroup().addTo(map);

    map.on('click', (event) => {
      if ($mapState.subscriptionZone.isEditable) {
        $mapState.subscriptionZone.coords = [event.latlng.lat, event.latlng.lng];
      }
    });

    renderMarkers(locations);
  });

  $: renderMarkers(locations);
  $: renderSubscriptionZone($mapState.subscriptionZone);
</script>

<div class="map-root" bind:this={mapElement}></div>

<style>
  :global(.cursor-inherit) {
    cursor: inherit;
  }
</style>
