const switchField = document.querySelector("#switch-patterns");
const closeField = document.querySelector("#close-patterns");
const safeField = document.querySelector("#safe-url");
const status = document.querySelector("#status");

function lines(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

async function restore() {
  const stored = await chrome.storage.local.get({
    switchPatterns: [],
    closePatterns: [],
    safeUrl: "about:blank",
  });
  switchField.value = stored.switchPatterns.join("\n");
  closeField.value = stored.closePatterns.join("\n");
  safeField.value = stored.safeUrl || "about:blank";
}

document.querySelector("#patterns").addEventListener("submit", async (event) => {
  event.preventDefault();
  await chrome.storage.local.set({
    switchPatterns: lines(switchField.value),
    closePatterns: lines(closeField.value),
    safeUrl: safeField.value.trim() || "about:blank",
  });
  status.textContent = "Saved.";
});

restore();
