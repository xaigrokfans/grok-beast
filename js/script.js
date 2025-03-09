// website/js/script.js
const feedbackForm = document.getElementById('feedback');
const feedbackStatus = document.getElementById('feedback-status');
const timelineEvents = document.querySelectorAll('.timeline .event');

// GitHub API token - REPLACE WITH YOUR PAT
const GITHUB_TOKEN = 'YOUR_PERSONAL_ACCESS_TOKEN'; // Secure this in production!
const REPO = 'xaigrokfans/grok-beast';

// Feedback submission
feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const suggestion = document.getElementById('feedback-text').value.trim();

    if (!suggestion) {
        showStatus('Please enter a suggestion—don’t leave the beast hanging!', 'error');
        return;
    }

    try {
        const response = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
            method: 'POST',
            headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: 'Grok-beast Feedback',
                body: `**Suggestion:** ${suggestion}\n\n*Submitted via Grok-beast Unleashed*`,
                labels: ['feedback']
            })
        });

        if (response.ok) {
            showStatus('Thanks for the roar! Check it on GitHub: github.com/xaigrokfans/grok-beast/issues', 'success');
            feedbackForm.reset();
        } else {
            throw new Error('GitHub API failed');
        }
    } catch (error) {
        showStatus('Oops—cosmic interference! Try again or yell on GitHub.', 'error');
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
animateTimeline(); // Trigger on load
console.log("Grok-beast Unleashed—xAI flair activated!");
