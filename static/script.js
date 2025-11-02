HEAD
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

document.querySelectorAll('.sector-selection button').forEach(button => {
    button.addEventListener('click', async () => {
        const sector = button.dataset.sector;
        document.getElementById('loading').classList.remove('hidden');
        document.getElementById('results').classList.add('hidden');
        document.getElementById('error-message').classList.add('hidden');
        document.getElementById('selected-sector-display').textContent = sector;

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sector: sector })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Something went wrong on the server.');
            }

            const data = await response.json();
            document.getElementById('sentiment').textContent = data.sentiment;
            document.getElementById('short-term').textContent = data.shortTermOutlook;
            document.getElementById('long-term').textContent = data.longTermOutlook;
            document.getElementById('stocks').textContent = data.stocksAffected.map(s => `${s.ticker}: ${s.movement}`).join(', ');
            document.getElementById('news-summary').textContent = data.newsSummary;

            if (data.audioContent) {
                const audioPlayer = document.getElementById('audio-player');
                audioPlayer.src = `data:audio/mpeg;base64,${data.audioContent}`;
                audioPlayer.load();
                audioPlayer.play();
            } else {
                document.getElementById('audio-player').src = ''; // Clear if no audio
            }

            document.getElementById('results').classList.remove('hidden');

        } catch (error) {
            console.error('Fetch error:', error);
            document.getElementById('error-message').textContent = `Error: ${error.message}`;
            document.getElementById('error-message').classList.remove('hidden');
        } finally {
            document.getElementById('loading').classList.add('hidden');
        }
    });
});
