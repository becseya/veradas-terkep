<script>
  import { onMount } from "svelte";

  // TODO proper unsubscribe, UX, chapta for subscribe

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
  let subscribed = false;
  let statusText = "Ellenorizzuk az elozo feliratkozast...";
  let busy = false;

  function initFirebase() {
    if (typeof window === "undefined" || !window.firebase) {
      statusText = "A Firebase SDK nem toltodott be.";
      return false;
    }

    if (!window.firebase.apps.length) {
      window.firebase.initializeApp(firebaseConfig);
    }

    db = window.firebase.firestore();
    messaging = window.firebase.messaging();
    return true;
  }

  async function ensureMessagingServiceWorker() {
    if (!("serviceWorker" in navigator)) {
      throw new Error("A bongeszo nem tamogatja a service worker-t.");
    }

    await navigator.serviceWorker.register("/firebase-messaging-sw.js");
  }

  async function gCheckSubscription() {
    if (!initFirebase()) {
      return;
    }

    try {
      await ensureMessagingServiceWorker();
      const token = await messaging.getToken({ vapidKey: PUBLIC_VAPID_KEY });
      if (token) {
        const snapshot = await db.collection("subscriptions").doc(token).get();
        if (snapshot.exists) {
          subscribed = true;
          statusText = "Mar fel vagy iratkozva az ertesitesekre.";
          return;
        }
      }
      statusText = "Iratkozz fel, hogy ertesitest kapj az uj veradasokrol.";
    } catch (err) {
      statusText =
        "Nincs aktiv feliratkozas, vagy nincs engedelyezve az ertesites.";
    }
  }

  async function gSubscribe() {
    if (!initFirebase()) {
      return;
    }

    busy = true;

    try {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        alert("Az ertesitesek engedelyezese szukseges a funkciohoz!");
        statusText = "Az ertesitesi engedely hianyzik.";
        return;
      }

      await ensureMessagingServiceWorker();

      const token = await messaging.getToken({
        vapidKey: PUBLIC_VAPID_KEY,
      });

      if (token) {
        await db.collection("subscriptions").doc(token).set({
          name: "foo",
          bar: 5,
        });

        subscribed = true;
        statusText = "Sikeres feliratkozas!";
        alert(
          "Sikeres feliratkozas! Ertesiteni fogunk, ha uj veradas lesz a kornyekeden.",
        );
      } else {
        statusText = "Nem sikerult azonositot lekerdezni.";
        alert(
          "Nem sikerult azonositot lekerni. Ellenorizd a bongeszo beallitasait!",
        );
      }
    } catch (error) {
      console.error("Subscription error:", error);
      statusText = "Hiba tortent a feliratkozas soran.";
      alert("Hiba tortent a feliratkozas soran. Reszletek a konzolban.");
    } finally {
      busy = false;
    }
  }

  onMount(async () => {
    await gCheckSubscription();
  });
</script>

<section class="panel panel-subscribe">
  <header class="panel-header panel-header-static">
    <h3>Ertesitesek</h3>
  </header>

  <div class="panel-body">
    <p class="subscribe-copy">
      Kapj push ertesitest, ha uj veradasi idopont jelenik meg a kornyekeden.
    </p>

    <button
      class="subscribe-btn"
      on:click={gSubscribe}
      disabled={busy || subscribed}
    >
      {#if busy}
        Folyamatban...
      {:else if subscribed}
        Feliratkozva
      {:else}
        Feliratkozas
      {/if}
    </button>

    <p class="subscribe-meta">{statusText}</p>
  </div>
</section>
