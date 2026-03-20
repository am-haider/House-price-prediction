document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const resultContainer = document.getElementById('resultContainer');
    const predictedPriceElement = document.getElementById('predictedPrice');
    const loader = document.getElementById('loader');
    const btnText = document.querySelector('.btn-text');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

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
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get prediction');
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
