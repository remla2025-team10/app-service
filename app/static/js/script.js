// A user visits page 
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/metrics/user_visit', { method: 'POST' });
});

// A user leaves page
window.addEventListener('beforeunload', function() {
    navigator.sendBeacon('/api/metrics/user_leave');
});

document.getElementById('analyze-btn').addEventListener('click', async function() {
    const reviewText = document.getElementById('review').value.trim();
    
    if (!reviewText) {
        alert('Please enter a review first!');
        return;
    }
    
    // Show loader
    document.getElementById('loader').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    
    try {
        // Send click event to metrics API
        fetch('/api/metrics/click', {method: 'POST'});

        // Send review text to the model API for sentiment analysis
        const response = await fetch('/api/models/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: reviewText
            })
        });
        
        const data = await response.json();
        
        // Hide loader
        document.getElementById('loader').style.display = 'none';
        
        // Show result
        const resultDiv = document.getElementById('result');
        const sentimentResult = document.getElementById('sentiment-result');
        // TODO consider removing this if not needed
        // const confidenceScore = document.getElementById('confidence-score');
        
        // Reset classes
        resultDiv.classList.remove('positive', 'negative', 'neutral');
        
        if (data.result) {
            sentimentResult.textContent = `Sentiment: ${data.result.prediction}`;
        } else {
            sentimentResult.textContent = 'Error: Could not analyze sentiment';
            resultDiv.classList.add('neutral');
        }
        
        resultDiv.style.display = 'block';

        if (data.result) {
            // remove existing feedback container if it exists
            const existingFeedback = resultDiv.querySelector('.feedback-container');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            // Add new feedback container
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback-container';
            feedbackDiv.innerHTML = `
                <p><strong>Was this analysis helpful?</strong></p>
                <button class="feedback-btn" data-value="yes">👍 Yes</button>
                <button class="feedback-btn" data-value="no">👎 No</button>
            `;
            resultDiv.appendChild(feedbackDiv);
            
            // Feedback buttons
            feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const value = this.getAttribute('data-value');
                    try {
                        await fetch('/api/metrics/feedback', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                feedback: value,
                                sentiment: data.result.prediction
                            })
                        });
                        feedbackDiv.innerHTML = '<p>Thank you for your feedback!</p>';
                    } catch (error) {
                        console.error('Error sending feedback:', error);
                    }
                });
            });
        }

    } catch (error) {
        // Hide loader
        document.getElementById('loader').style.display = 'none';
        alert('Error analyzing sentiment: ' + error.message);
    }
});