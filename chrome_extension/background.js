// background.js

// Create context menu items on extension installation.
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "readAloud",
    title: "Read Aloud",
    contexts: ["selection", "page"]
  });
  chrome.contextMenus.create({
    id: "simplifyText",
    title: "Simplify Text",
    contexts: ["selection"]
  });
});

// When a context menu item is clicked, send a message to the content script.
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "readAloud") {
    chrome.tabs.sendMessage(tab.id, { command: "readAloud" });
  } else if (info.menuItemId === "simplifyText") {
    chrome.tabs.sendMessage(tab.id, { command: "simplifyText" });
  }
});

// Listen for keyboard commands defined in your manifest.json.
chrome.commands.onCommand.addListener((command) => {
  let msg = {};
  if (command === "read-aloud") {
    msg = { command: "readAloud" };
  } else if (command === "simplify-text") {
    msg = { command: "simplifyText" };
  }
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, msg);
  });
});
