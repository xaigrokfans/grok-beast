// functions/submit-feedback.js
exports.handler = async (event) => {
    const { suggestion } = JSON.parse(event.body);
    if (!suggestion) return { statusCode: 400, body: 'Missing suggestion' };

    const response = await fetch('https://api.github.com/repos/xaigrokfans/grok-beast/issues', {
        method: 'POST',
        headers: {
            'Authorization': `token ${process.env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: 'Grok-beast Feedback',
            body: `**Suggestion:** ${suggestion}\n\n*Submitted via Grok-beast Unleashed*`,
            labels: ['feedback']
        })
    });

    return {
        statusCode: response.ok ? 200 : 500,
        body: JSON.stringify({ message: response.ok ? 'Success' : 'Error' })
    };
};
