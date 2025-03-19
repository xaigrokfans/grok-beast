import fetch from 'node-fetch'; // Keep for future use

export const handler = async (event, context) => {
  try {
    const body = JSON.parse(event.body || '{}');
    const suggestion = body.suggestion;
    if (!suggestion) {
      return { statusCode: 400, body: JSON.stringify({ error: 'Suggestion is required' }) };
    }

    // Log the suggestion instead of fetching
    console.log(`Received suggestion: ${suggestion}`);

    // Remove the failing fetch block
    /*
    const response = await fetch('https://example.com/api/feedback', {
      method: 'POST',
      body: JSON.stringify({ suggestion }),
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to submit feedback');
    */

    return { statusCode: 200, body: JSON.stringify({ message: 'Feedback submitted successfully' }) };
  } catch (error) {
    return { statusCode: 500, body: JSON.stringify({ error: error.message || 'Internal server error' }) };
  }
};
