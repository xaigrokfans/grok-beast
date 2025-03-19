import fetch from 'node-fetch';

export const handler = async (event, context) => {
  try {
    const body = JSON.parse(event.body || '{}');
    const suggestion = body.suggestion;
    if (!suggestion) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Suggestion is required' }) };
    }

    const token = process.env.GITHUB_TOKEN;
    if (!token) {
      throw new Error('GitHub token not configured');
    }

    const timestamp = new Date().toISOString();
    const response = await fetch('https://api.github.com/repos/xaigrokfans/grok-beast/issues', {
      method: 'POST',
      headers: {
        'Authorization': `token ${token}`,
        'Accept': 'application/vnd.github+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: `Grok-beast Feedback - ${timestamp}`,
        body: `**Suggestion:** ${suggestion}\n\n*Submitted via Grok-beast Unleashed on ${timestamp}*`,
        labels: ['feedback']
      })
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status} - ${await response.text()}`);
    }

    return { statusCode: 200, body: JSON.stringify({ message: 'Feedback submitted successfully' }) };
  } catch (error) {
    return { statusCode: 500, body: JSON.stringify({ error: error.message || 'Internal server error' }) };
  }
};
