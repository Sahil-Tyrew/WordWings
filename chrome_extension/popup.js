// popup.js

// Get references to DOM elements from the popup's HTML
const textInput = document.getElementById("textInput");
const readAloudBtn = document.getElementById("readAloudBtn");
const simplifyTextBtn = document.getElementById("simplifyTextBtn");
const chunkTextBtn = document.getElementById("chunkTextBtn");
const outputDiv = document.getElementById("output");

// Function to perform text-to-speech using the Web Speech API
function readAloud() {
  const text = textInput.value.trim();
  if (!text) {
    alert("Please enter some text to read aloud.");
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  speechSynthesis.speak(utterance);
}

// Function to simplify text via your backend
async function simplifyText() {
  const text = textInput.value.trim();
  if (!text) {
    alert("Please enter some text to simplify.");
    return;
  }
  
  outputDiv.textContent = "Simplifying...";
  
  try {
    const response = await fetch("http://127.0.0.1:5001/simplify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, use_ai: false })
    });
    
    const result = await response.json();
    if (result.simplified) {
      outputDiv.textContent = result.simplified;
    } else if (result.error) {
      outputDiv.textContent = "Error: " + result.error;
    } else {
      outputDiv.textContent = "Unexpected response from the simplification service.";
    }
  } catch (error) {
    console.error("Simplification error:", error);
    outputDiv.textContent = "Error calling the simplification service.";
  }
}

// Function to chunk text via your backend
async function chunkText() {
  const text = textInput.value.trim();
  if (!text) {
    alert("Please enter some text to chunk.");
    return;
  }
  
  outputDiv.textContent = "Chunking text...";
  
  try {
    const response = await fetch("http://127.0.0.1:5001/chunk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    });
    
    const result = await response.json();
    if (result.chunked) {
      // If chunked is an array, join with newlines; otherwise, display as-is.
      outputDiv.textContent = Array.isArray(result.chunked)
        ? result.chunked.join("\n\n")
        : result.chunked;
    } else if (result.error) {
      outputDiv.textContent = "Error: " + result.error;
    } else {
      outputDiv.textContent = "Unexpected response from the chunking service.";
    }
  } catch (error) {
    console.error("Chunking error:", error);
    outputDiv.textContent = "Error calling the chunking service.";
  }
}

// Attach event listeners to the buttons
readAloudBtn.addEventListener("click", readAloud);
simplifyTextBtn.addEventListener("click", simplifyText);
chunkTextBtn.addEventListener("click", chunkText);
