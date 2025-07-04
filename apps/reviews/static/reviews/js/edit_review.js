/**
 * Handles the star rating UI for the edit review page.
 * Allows users to click stars to set the rating and updates the display.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Initializing edit review page script...");

    // Get star rating elements by their IDs
    const ratingStarsContainer = document.getElementById('ratingStars');
    const ratingDisplay = document.getElementById('ratingDisplay');
    const ratingInput = document.getElementById('rating');

    if (ratingStarsContainer && ratingDisplay && ratingInput) {
        // Set the initial rating from the hidden input's value
        const initialRating = parseInt(ratingInput.value) || 0;
        console.log(`Initial rating for edit form: ${initialRating}`);

        /**
         * Set the rating visually and update the hidden input.
         */
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

        // Listen for star clicks to update rating
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