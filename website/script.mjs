// website/script.mjs
const feedbackForm = document.getElementById('feedback');
const feedbackStatus = document.getElementById('feedback-status');
const domainSelect = document.getElementById('domain-select'); // New dropdown
const solverTicker = document.getElementById('solver-ticker'); // New ticker div

// Feedback submission
feedbackForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const suggestion = document.getElementById('feedback-text').value.trim();
  const domain = domainSelect.value;

  if (!suggestion) {
    showStatus('Please enter a suggestion—don’t leave the beast hanging!', 'error');
    return;
  }

  showStatus('Submitting...', 'info');
  try {
    const response = await fetch('/.netlify/functions/submit-feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion, timestamp: new Date().toISOString() })
    });
    const result = await response.json();

    if (response.ok) {
      showStatus(`Thanks for the roar! Check it on GitHub: github.com/xaigrokfans/grok-beast/issues`, 'success');
      feedbackForm.reset();
    } else {
      throw new Error(result.error || 'Submission failed');
    }
  } catch (error) {
    showStatus('Oops—cosmic interference! Try again or yell on GitHub.', 'error');
  }
});

// Solver status ticker
async function updateSolverTicker() {
  try {
    const domain = domainSelect.value;
    const response = await fetch(`/solver-status?domain=${domain}`);
    const status = await response.json();
    if (response.ok) {
      const { problem, fitness, runtime } = status.latest;
      solverTicker.textContent = `Beast solving ${domain}: ${problem} | Fitness: ${fitness.toFixed(4)} | Time: ${runtime.toFixed(2)}s`;
      solverTicker.style.color = '#00b7eb';
    } else {
      throw new Error(status.error || 'Status fetch failed');
    }
  } catch (error) {
    solverTicker.textContent = `Solver offline for ${domainSelect.value}—cosmic dust in the gears!`;
   // solverTicker.textContent = 'Solver offline—cosmic dust in the gears!';
    solverTicker.style.color = '#ff4500';
  }
}

// Utility to show feedback status
function showStatus(message, type) {
  feedbackStatus.textContent = message;
  feedbackStatus.style.display = 'block';
  feedbackStatus.style.color = type === 'success' ? '#00b7eb' : type === 'info' ? '#ffd700' : '#ff4500';
  if (type !== 'info') setTimeout(() => { feedbackStatus.style.display = 'none'; }, 5000);
}

// Initialize ticker and periodic updates
updateSolverTicker();
setInterval(updateSolverTicker, 10000); // Update every 10s
