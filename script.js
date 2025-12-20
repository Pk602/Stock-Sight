// Get form elements
const form = document.getElementById('stock-form');
const resultBox = document.getElementById('result-section');
const output = document.getElementById('prediction-output');

// Submit event handler
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Get values from form fields
  const data = {
    companySymbol: document.getElementById('symbol').value,
    predictionDate: document.getElementById('date').value
  };

  try {
    // Make POST request to Flask backend
    const response = await fetch('https://stock-sight-1-d4b2.onrender.com/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Server error');
    }

    // Parse response
    const result = await response.json();

    // Show prediction
    if (result.estimatedPrice !== undefined) {
      output.textContent = result.estimatedPrice.toFixed(2);
    } else {
      output.textContent = 'Error: Prediction result not found.';
    }

    resultBox.style.display = 'block';

  } catch (error) {
    // Display error
    output.textContent = `Error predicting: ${error.message || error}. Check server.`;
    resultBox.style.display = 'block';
    console.error(error);
  }
});
