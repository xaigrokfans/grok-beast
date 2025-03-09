// website/js/script.js
const feedbackForm = document.getElementById('feedback');
const feedbackStatus = document.getElementById('feedback-status');
const timelineEvents = document.querySelectorAll('.timeline .event');

// Simulated API call via workflow_dispatch (manual for now)
feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const suggestion = document.getElementById('feedback-text').value.trim();

    if (!suggestion) {
        showStatus('Please enter a suggestion—don’t leave the beast hanging!', 'error');
        return;
    }

const response = await fetch('/.netlify/functions/submit-feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suggestion })
});
if (response.ok) {
    showStatus('Thanks for the roar! Check it on GitHub!', 'success');
    feedbackForm.reset();
} else {
    throw new Error('API failed');
}

});

function showStatus(message, type) {
    feedbackStatus.textContent = message;
    feedbackStatus.style.display = 'block';
    feedbackStatus.style.color = type === 'success' ? '#00b7eb' : '#ff4500';
    setTimeout(() => { feedbackStatus.style.display = 'none'; }, 5000);
}

// Timeline animation on scroll
function animateTimeline() {
    const triggerBottom = window.innerHeight * 0.8;
    timelineEvents.forEach(event => {
        const eventTop = event.getBoundingClientRect().top;
        if (eventTop < triggerBottom) {
            event.classList.add('visible');
        }
    });
}

// Smooth scroll for nav links
document.querySelectorAll('nav a').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = anchor.getAttribute('href').substring(1);
        document.getElementById(targetId).scrollIntoView({ behavior: 'smooth' });
    });
});

// Init
window.addEventListener('scroll', animateTimeline);
animateTimeline();
console.log("Grok-beast Unleashed—xAI flair activated!");
