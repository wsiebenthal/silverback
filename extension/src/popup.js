const result = document.querySelector("#result");

document.querySelector("#options").addEventListener("click", () => {
  chrome.runtime.openOptionsPage();
});

document.querySelector("#test").addEventListener("click", async () => {
  result.textContent = "Sending…";
  try {
    const response = await chrome.runtime.sendMessage({
      type: "privacy_trigger",
      state: "approach",
      source: "popup",
    });
    result.textContent = JSON.stringify(response, null, 2);
  } catch (error) {
    result.textContent = String(error);
  }
});
