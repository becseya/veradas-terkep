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

  function initFirebase() {
    if (typeof window === "undefined" || !window.firebase) {
      throw new Error("A Firebase SDK nem töltődött be.");
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
      throw new Error('Nincs kiválasztott helyszín.');
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

  async function ensureMessagingServiceWorker() {
    if (!("serviceWorker" in navigator)) {
      throw new Error("A böngésző nem támogatja a service worker-t.");
    }

    await navigator.serviceWorker.register("/firebase-messaging-sw.js");
  }

  async function getToken() {
    await ensureMessagingServiceWorker();
    return await messaging.getToken({ vapidKey: PUBLIC_VAPID_KEY });
  }

 async function unSubscribe() {
    busy = true;

    try {
      const token = await getToken();
      await db.collection('subscriptions').doc(token).delete();

      $mapState.subscriptionZone.coords = null;
      panelState = STATES.GET_LOC;
    } catch (error) {
      console.error('unSubscribe error:', error);
      alert('Hiba történt a leiratkozás során. Kérlek próbáld újra.');
    } finally {
      busy = false;
    }
  }

  async function gCheckSubscription() {
    try {
      initFirebase();

      if (Notification.permission === 'granted') {
        const token = await getToken();

        if (token) {
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
        }
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
        throw new Error("Hiányzik az értesítési engedély. Kérlek engedélyezd a böngésző beállításaiban!");
      }

      const token = await getToken();

      if (!token)  {
        throw new Error("Nem sikerült lekérni a tokent.");
      }
    
      await db.collection("subscriptions").doc(token).set({
        details: exportState(),
        lastSeen: serverTimestamp()
      });

      panelState = STATES.SUBSCRIBED;
      collapsed = true;
      alert(
        "Sikeres feliratkozás! Értesíteni fogunk, ha új véradás lesz a környékeden.",
      );
    } catch (error) {
      console.error("Subscription error:", error);
      alert("Hiba történt a feliratkozás során.");
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
  title="Értesítések"
  toggleLabel="rejt / mutat"
>
  {#if panelState === STATES.INIT}
    <p class="subscribe-loading">
      <i class="fa-solid fa-spinner fa-spin"></i>
      Feliratkozási állapot ellenőrzése...
    </p>
  {:else if panelState === STATES.SUBSCRIBED}
    <p class="subscribe-copy">Már sikeresen feliratkoztál.</p>
    <button class="subscribe-btn subscribe-btn-secondary" on:click={unSubscribe} disabled={busy}>
      {busy ? 'Folyamatban...' : 'Leiratkozás'}
    </button>
  {:else if panelState === STATES.GET_LOC}
    <p class="subscribe-copy">Válaszd ki a helyszínt a térkép segítségével.</p>
  {:else}
    <p class="subscribe-copy">
      A leszúrt helyszín kattintással módosítható. Állítsd be a távolságot, majd véglegesítsd!
    </p>

    <label class="radius-wrap" for="zone-radius">
      <span>Távolság: {$mapState.subscriptionZone.radiusKm} km</span>
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
      {busy ? 'Folyamatban...' : 'Feliratkozás'}
    </button>
  {/if}
</CollapsiblePanel>
