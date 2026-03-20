document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const resultContainer = document.getElementById('resultContainer');
    const predictedPriceElement = document.getElementById('predictedPrice');
    const loader = document.getElementById('loader');
    const btnText = document.querySelector('.btn-text');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Check if running via file protocol
        if (window.location.protocol === 'file:') {
            alert('Error: You are running the HTML file directly. Please use http://localhost:8000 instead to communicate with the backend.');
            return;
        }

        // Show loading state
        loader.style.display = 'block';
        btnText.style.opacity = '0.5';
        resultContainer.classList.add('hidden');

        const formData = new FormData(form);
        const data = {
            bedrooms: parseInt(formData.get('bedrooms')),
            bathrooms: parseFloat(formData.get('bathrooms')),
            sqft_living: parseFloat(formData.get('sqft_living')),
            floors: parseFloat(formData.get('floors')),
            waterfront: formData.get('waterfront') ? 1 : 0,
            view: parseInt(formData.get('view')),
            yr_built: parseInt(formData.get('yr_built'))
        };

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                let errorMsg = 'Failed to get prediction';
                const errorText = await response.text();
                try {
                    const errorJson = JSON.parse(errorText);
                    errorMsg = errorJson.detail || errorMsg;
                } catch (e) {
                    errorMsg = errorText || errorMsg;
                }

                if (window.location.port === '5500') {
                    errorMsg += '\n\nTIP: You are using Port 5500 (Live Server). Please use Port 8000 for full backend connectivity.';
                }
                
                throw new Error(errorMsg);
            }

            const result = await response.json();
            
            // Format number with commas
            const formattedPrice = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(result.predicted_price);

            predictedPriceElement.textContent = formattedPrice;
            
            // Show result with animation
            resultContainer.classList.remove('hidden');
            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            console.error('Error:', error);
            alert('Error: ' + error.message);
        } finally {
            // Hide loading state
            loader.style.display = 'none';
            btnText.style.opacity = '1';
        }
    });
});
