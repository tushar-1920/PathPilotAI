import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyAFzJ5bpG3DBFAoKUCBxJ5UTOOsQyrr9c8",
  authDomain: "pathpilot-f5937.firebaseapp.com",
  projectId: "pathpilot-f5937",
  storageBucket: "pathpilot-f5937.firebasestorage.app",
  messagingSenderId: "717751369641",
  appId: "1:717751369641:web:6563ed8dd5a58473eaceb8",
  measurementId: "G-XLYS0TLMSN"
};

const app  = initializeApp(firebaseConfig);
const auth = getAuth(app);

export async function signInWithGoogle() {
  try {
    const provider = new GoogleAuthProvider();
    const result   = await signInWithPopup(auth, provider);
    const idToken  = await result.user.getIdToken();

    const res = await fetch("/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idToken })
    });

    const data = await res.json();
    if (data.success) {
      window.location.href = data.redirect;
    } else {
      alert("Google login failed: " + data.error);
    }
  } catch (err) {
    console.error("Google sign-in error:", err);
    alert("Google sign-in failed. Please try again.");
  }
}