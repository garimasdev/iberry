// Scripts for  and  messaging
importScripts("https://www.gstatic.com/firebasejs/8.6.3/firebase-app.js"); 
importScripts("https://www.gstatic.com/firebasejs/8.6.3/firebase-messaging.js");  

// Initialize the  app in the service worker by passing the generated config
const firebaseConfig = {
  apiKey: "AIzaSyB3YnNXnBSDkuJp3QZKYYgnM52Jwawipoc",
  authDomain: "iberry-81920.firebaseapp.com",
  projectId: "iberry-81920",
  storageBucket: "iberry-81920.appspot.com",
  messagingSenderId: "661156171796",
  appId: "1:661156171796:web:eabde955604c4b64bd9701",
  measurementId: "G-9M4YJQ5DLL"
};

// function speak(text) {
//   const utterThis = self.SpeechSynthesisUtterance(text);

//   utterThis.onend = function (event) {
//     console.log("SpeechSynthesisUtterance.onend");
//   };

//   utterThis.onerror = function (event) {
//     console.log("SpeechSynthesisUtterance.onerror");
//   };

//   // const selectedOption = voiceSelect.selectedOptions[0].getAttribute("data-name");

//   // for (let i = 0; i < voices.length; i++) {
//   //   if (voices[i].name === selectedOption) {
//   //     utterThis.voice = voices[i];
//   //     break;
//   //   }
//   // }
//   // console.log("The voice name", pitch.value)
//   // console.log("The voice name", rate.value)
//   utterThis.pitch = 1;
//   utterThis.rate = 1;
//   // speechSynthesis.speak(utterThis);
//   // synth.speak(utterThis);
// }

firebase.initializeApp(firebaseConfig); 
const messaging=firebase.messaging(); 
messaging.onBackgroundMessage(function(payload) {
console.log('Received background message ', payload);

// Check if the browser supports the SpeechSynthesis API
const notificationTitle = payload.notification.title;
console.log("Notification title", notificationTitle)
// const audio=new Audio("/static/iphone_sound.mp3"); 
// audio.play(); 
const notificationOptions = {
    body: payload.notification.body,
};

self.registration.showNotification(notificationTitle, notificationOptions);
// speak(notificationTitle);
});


