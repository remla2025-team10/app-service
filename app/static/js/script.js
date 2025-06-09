// A user visits page 
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/metrics/user_visit', { method: 'POST' });
});

// A user leaves page
window.addEventListener('beforeunload', function() {
    navigator.sendBeacon('/api/metrics/user_leave');
});

function displayRandomGif() {
    const randomNumber = Math.floor(Math.random() * 5) + 1; // Random number between 1-5
    const gifPath = `/static/pic/${randomNumber}.gif`;
    
    const gifImg = document.createElement('img');
    gifImg.src = gifPath;
    gifImg.alt = 'Random reaction GIF';
    
    return gifImg;
}

function displayRandomThankyouGif() {
    const randomNumber = Math.floor(Math.random() * 5) + 1;
    const gifPath = `/static/pic/t${randomNumber}.gif`;

    const gifImg = document.createElement('img');
    gifImg.src = gifPath;
    gifImg.alt = 'Thank you GIF';

    return gifImg;
}

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
            
            // Create random GIF element
            const gifImg = displayRandomGif();
            
            // Add new feedback container
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback-container';
            
            
                        // Create feedback section (left side)
            const feedbackContent = document.createElement('div');
            feedbackContent.className = 'feedback-content';
            feedbackContent.innerHTML = `
                <p><strong>Was this analysis helpful?</strong></p>
                <div class="feedback-buttons">
                    <button class="feedback-btn" data-value="yes">👍 Yes</button>
                    <button class="feedback-btn" data-value="no">👎 No</button>
                </div>
            `;
            
            // Create GIF container (right side)
            const gifContainer = document.createElement('div');
            gifContainer.id = 'random-gif-container';
            gifContainer.appendChild(gifImg);
            
            // Add both sections to the feedback container
            feedbackDiv.appendChild(feedbackContent);
            feedbackDiv.appendChild(gifContainer);
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
            
                        // Get the container that was created earlier
                        const gifContainer = feedbackDiv.querySelector('#random-gif-container');
                        
                        // Clear the container properly
                        while (gifContainer.firstChild) {
                            gifContainer.removeChild(gifContainer.firstChild);
                        }
                        
                        // Show thank you GIF
                        const thankYouGif = displayRandomThankyouGif();
                        gifContainer.appendChild(thankYouGif);
            
                        // Replace feedback content with thank you message
                        feedbackDiv.querySelector('.feedback-content').innerHTML = '<p><strong>Thank you for your feedback!</strong></p>';
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