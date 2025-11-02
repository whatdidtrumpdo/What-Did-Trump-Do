console.log("Script is running!");
window.addEventListener('DOMContentLoaded', async () => {
  const resultDiv = document.getElementById('result');
  const data = {
    sentiment: "Positive",
    shortTermOutlook: "Rising",
    longTermOutlook: "Stable",
    newsSummary: "Tech stocks are trending upward this week."
  };
  try {
    const response = await fetch('/analyze', { method: 'POST' });
    const data = await response.json();

    if (data.error) {
      resultDiv.innerText = "Error: " + data.error;
    } else {
      resultDiv.innerHTML = `
        <p><strong>Sentiment:</strong> ${data.sentiment}</p>
        <p><strong>Short-Term Outlook:</strong> ${data.shortTermOutlook}</p>
        <p><strong>Long-Term Outlook:</strong> ${data.longTermOutlook}</p>
        <p><strong>Summary:</strong> ${data.newsSummary}</p>
      `;
    }
    
  } catch (err) {
    resultDiv.innerText = "An error occurred: " + err;
  }
});
