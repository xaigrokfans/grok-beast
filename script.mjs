// website/script.mjs
const feedbackForm = document.getElementById('feedback');
const feedbackStatus = document.getElementById('feedback-status');

feedbackForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const suggestion = document.getElementById('feedback-text').value.trim();

  if (!suggestion) {
    showStatus('Please enter a suggestion—don’t leave the beast hanging!', 'error');
    return;
  }

  try {
    const response = await fetch('/.netlify/functions/submit-feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ suggestion })
    });
    const result = await response.json();

    if (response.ok) {
      showStatus('Thanks for the roar! Check it on GitHub: github.com/xaigrokfans/grok-beast/issues', 'success');
      feedbackForm.reset();
    } else {
      throw new Error(result.error || 'Submission failed');
    }
  } catch (error) {
    console.error('Fetch error:', error);
    showStatus('Oops—cosmic interference! Try again or yell on GitHub.', 'error');
  }
});

function showStatus(message, type) {
  feedbackStatus.textContent = message;
  feedbackStatus.style.display = 'block';
  feedbackStatus.style.color = type === 'success' ? '#00b7eb' : '#ff4500';
  setTimeout(() => { feedbackStatus.style.display = 'none'; }, 5000);
}

// Other features (timeline, smooth scroll) omitted for brevity
console.log("Grok-beast Unleashed—xAI flair activated!");
