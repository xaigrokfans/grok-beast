// website/js/script.js
document.getElementById('feedback').addEventListener('submit', (e) => {
    e.preventDefault();
    const suggestion = e.target.querySelector('textarea').value;
    alert(`Thanks for the roar! Your suggestion: "${suggestion}" will fuel the beast. Join us on GitHub!`);
    e.target.reset();
});

// Placeholder for future timeline animation
console.log("Grok-beast Unleashed—xAI flair activated!");
