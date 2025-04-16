// contentScript.js

// Function to read aloud the selected text or the entire page's text.
function readAloudSelectedText() {
  const text = window.getSelection().toString() || document.body.innerText;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  speechSynthesis.speak(utterance);
}

// Function to simplify the selected text by calling your backend.
async function simplifySelectedText() {
  const text = window.getSelection().toString();
  if (!text) {
    alert("Please select some text to simplify.");
    return;
  }

  // Debug logging
  console.log("Sending text for simplification:", text);
  console.log("Calling endpoint: http://127.0.0.1:5001/simplify");
  
  try {
    const response = await fetch("http://127.0.0.1:5001/simplify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    
    console.log("Response status:", response.status);
    const result = await response.json();
    
    if (result && result.simplified) {
      alert("Simplified Text:\n" + result.simplified);
      console.log("Simplified result:", result.simplified);
    } else {
      alert("Unexpected response from simplification service.");
      console.log("Response JSON:", result);
    }
  } catch (error) {
    console.error("Error simplifying text:", error);
    alert("Error simplifying text; check console for details.");
  }
}

// Listen for messages sent from background.js (via context menu or keyboard commands)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.command === "readAloud") {
    readAloudSelectedText();
  } else if (message.command === "simplifyText") {
    simplifySelectedText();
  }
});
