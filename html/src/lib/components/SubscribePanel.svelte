<script>
  import { onMount } from "svelte";
  import CollapsiblePanel from './CollapsiblePanel.svelte';
  import { mapState } from '../stores/mapState.js';

  const STATES = {
    INIT: 'ST_init',
    SUBSCRIBED: 'ST_subscribed',
    GET_LOC: 'ST_get_loc',
    FINALIZE: 'ST_finalize'
  };

  const firebaseConfig = {
    apiKey: "AIzaSyBX16EsUuOO25BFtLQG9mDdGU_Zhi8pAOY",
    authDomain: "veradas-terkep.firebaseapp.com",
    projectId: "veradas-terkep",
    storageBucket: "veradas-terkep.firebasestorage.app",
    messagingSenderId: "955263468077",
    appId: "1:955263468077:web:75e5b1ee0ee25f4c402ea4",
  };

  const PUBLIC_VAPID_KEY =
    "BAoFSf3todU-9F3s_8oaXmOAnrucllfpO9hM7xnBK-QtuPgMVhq8FMWOBYJC4HZdVKWIKlM9XIZTYSoDnojWgZo";

  let db;
  let messaging;
  let panelState = STATES.INIT;
  let busy = false;
  let collapsed = true;

  function ensureFirebase() {
    if (typeof window === "undefined" || !window.firebase) {
      throw new Error("A Firebase SDK nem toltodott be.");
    }

    if (!window.firebase.apps.length) {
      window.firebase.initializeApp(firebaseConfig);
    }

    db = window.firebase.firestore();
    messaging = window.firebase.messaging();
  }

  function serverTimestamp() {
    return window.firebase.firestore.FieldValue.serverTimestamp();
  }

  function exportState() {
    const zone = $mapState.subscriptionZone;
    if (!zone.coords) {
      throw new Error('Nincs kivalasztott helyszin.');
    }

    return JSON.stringify({
      zones: [{
        lat: zone.coords[0],
        lng: zone.coords[1],
        radiusKm: zone.radiusKm,
        filter: 0,
      }],
      snoozeUntil: '1970-01-01T00:00:00Z'
    });
  }

  function restoreState(details) {
    if (!details || typeof details !== 'string') {
      throw new Error('Invalid details payload.');
    }

    const parsed = JSON.parse(details);
    const firstZone = parsed?.zones?.[0];

    if (!firstZone) {
      throw new Error('Invalid details payload.');
    }

    $mapState.subscriptionZone.coords = [firstZone.lat, firstZone.lng];
    $mapState.subscriptionZone.radiusKm = firstZone.radiusKm;
  }

  async function bootstrapToken(ensureServiceWorker = true) {

    ensureFirebase();

    if (ensureServiceWorker) {
      if (!("serviceWorker" in navigator)) {
        throw new Error("A bongeszo nem tamogatja a service worker-t.");
      }

      await navigator.serviceWorker.register("/firebase-messaging-sw.js");
    }

    const token = await messaging.getToken({ vapidKey: PUBLIC_VAPID_KEY });
    if (!token)  {
      throw new Error("Nem sikerult a token lekerni. Ellenorizd a bongeszo beallitasait!");
    }

    return token;
  }

 async function unSubscribe() {
    busy = true;

    try {
      const token = await bootstrapToken(false);
      await db.collection('subscriptions').doc(token).delete();

      $mapState.subscriptionZone.coords = null;
      panelState = STATES.GET_LOC;
    } catch (error) {
      console.error('unSubscribe error:', error);
      alert('Hiba tortent a leiratkozas soran.');
    } finally {
      busy = false;
    }
  }

  async function gCheckSubscription() {
    try {
      const token = await bootstrapToken();
      const subscriptionRef = db.collection("subscriptions").doc(token);
      const snapshot = await subscriptionRef.get();
      if (snapshot.exists) {
        await subscriptionRef.update({
          lastSeen: serverTimestamp()
        });

        restoreState(snapshot.data()?.details);
        panelState = STATES.SUBSCRIBED;
        return;
      }
    } catch (err) {
      console.error('checkSubscription error:', err);
    }

    $mapState.subscriptionZone.coords = null;
    panelState = STATES.GET_LOC;
    collapsed = false;
  }

  async function gSubscribe() {
    busy = true;

    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        throw new Error("Az ertesitesi engedely hianyzik.");
      }

      const token = await bootstrapToken();
    
      await db.collection("subscriptions").doc(token).set({
        details: exportState(),
        lastSeen: serverTimestamp()
      });

      panelState = STATES.SUBSCRIBED;
      collapsed = true;
      alert(
        "Sikeres feliratkozas! Ertesiteni fogunk, ha uj veradas lesz a kornyekeden.",
      );
    } catch (error) {
      console.error("Subscription error:", error);
      alert("Hiba tortent a feliratkozas soran.");
    } finally {
      busy = false;
    }
  }

  function onRadiusChange(event) {
    $mapState.subscriptionZone.radiusKm = Number(event.currentTarget.value);
  }

  $: if (panelState === STATES.GET_LOC && $mapState.subscriptionZone.coords) {
    panelState = STATES.FINALIZE;
  }

  $: $mapState.subscriptionZone.isEditable = panelState !== STATES.SUBSCRIBED;

  onMount(async () => {
    await gCheckSubscription();
  });
</script>

<CollapsiblePanel
  bind:collapsed
  sectionClass="panel-subscribe"
  title="Ertesitesek"
  toggleLabel="Ertesitesek lenyitása/felcsukása"
>
  {#if panelState === STATES.INIT}
    <p class="subscribe-loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
      Feliratkozasi allapot ellenorzese...
    </p>
  {:else if panelState === STATES.SUBSCRIBED}
    <p class="subscribe-copy">Mar sikeresen feliratkoztal.</p>
    <button class="subscribe-btn subscribe-btn-secondary" on:click={unSubscribe} disabled={busy}>
      {busy ? 'Folyamatban...' : 'Leiratkozas'}
    </button>
  {:else if panelState === STATES.GET_LOC}
    <p class="subscribe-copy">Valaszd ki a helyszint a terkep segitsegevel.</p>
  {:else}
    <p class="subscribe-copy">
      A kijelolt helyszin kattintassal modosithato. Allitsd be a sugarat, majd mentsd a
      feliratkozast.
    </p>

    <label class="radius-wrap" for="zone-radius">
      <span>Sugar: {$mapState.subscriptionZone.radiusKm} km</span>
      <input
        id="zone-radius"
        type="range"
        min="1"
        max="30"
        step="0.1"
        value={$mapState.subscriptionZone.radiusKm}
        on:input={onRadiusChange}
        disabled={busy}
      />
    </label>

    <button class="subscribe-btn" on:click={gSubscribe} disabled={busy}>
      {busy ? 'Folyamatban...' : 'Feliratkozas'}
    </button>
  {/if}
</CollapsiblePanel>
