importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyBX16EsUuOO25BFtLQG9mDdGU_Zhi8pAOY",
  authDomain: "veradas-terkep.firebaseapp.com",
  projectId: "veradas-terkep",
  storageBucket: "veradas-terkep.firebasestorage.app",
  messagingSenderId: "955263468077",
  appId: "1:955263468077:web:75e5b1ee0ee25f4c402ea4"
});

const messaging = firebase.messaging();
const ROOT_URL = '/';

function getTargetUrlFromPayload(payload) {
  const payloadUrl = payload?.fcmOptions?.link || payload?.data?.link || payload?.data?.url;
  return new URL(payloadUrl || ROOT_URL, self.location.origin).href;
}

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification?.title || 'Veradas-terkep';
  const targetUrl = getTargetUrlFromPayload(payload);
  const notificationOptions = {
    body: payload.notification?.body || '',
    icon: '/favicon.ico',
    data: {
      url: targetUrl
    }
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = new URL(event.notification?.data?.url || ROOT_URL, self.location.origin).href;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(async (windowClients) => {
      for (const client of windowClients) {
        const clientOrigin = new URL(client.url).origin;
        if (clientOrigin !== self.location.origin || !('focus' in client)) {
          continue;
        }

        if ('navigate' in client) {
          await client.navigate(targetUrl);
        }

        if ('focus' in client) {
          return client.focus();
        }
      }

      if (clients.openWindow) {
        return clients.openWindow(targetUrl);
      }

      return undefined;
    })
  );
});
