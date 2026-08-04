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

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// TODO icon, url,