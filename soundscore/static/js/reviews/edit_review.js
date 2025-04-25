document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing edit review page script...");

    // --- Star Rating Initialization ---
    // Use the IDs that exist in your HTML
    const ratingStarsContainer = document.getElementById('ratingStars');  // Changed
    const ratingDisplay = document.getElementById('ratingDisplay');       // Changed
    const ratingInput = document.getElementById('rating');                // Changed

    if (ratingStarsContainer && ratingDisplay && ratingInput) {
        // Get the initial rating from the hidden input's value
        const initialRating = parseInt(ratingInput.value) || 0;
        console.log(`Initial rating for edit form: ${initialRating}`);

        // Rest of your fallback logic works as is
        function setRatingEdit(rating) {
            const stars = ratingStarsContainer.querySelectorAll('.rating-star');
            stars.forEach(star => {
                const starRating = parseInt(star.dataset.rating);
                star.classList.toggle('text-yellow-400', starRating <= rating);
                star.classList.toggle('text-gray-300', starRating > rating);
            });
            ratingDisplay.textContent = rating > 0 ? `${rating}/5` : 'Select a rating';
            ratingInput.value = rating;
        }
        
        setRatingEdit(initialRating);
        ratingStarsContainer.addEventListener('click', function(event) {
            const star = event.target.closest('.rating-star');
            if (star) {
                const rating = parseInt(star.dataset.rating);
                setRatingEdit(rating);
            }
        });
    } else {
        console.error("Could not find star rating elements. Check your HTML IDs.");
    }
});