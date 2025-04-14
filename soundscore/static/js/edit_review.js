document.addEventListener('DOMContentLoaded', function() {
    console.log("Edit review script running."); // Check if script runs

    const ratingStarsContainer = document.getElementById('ratingStars');
    const ratingInput = document.getElementById('rating');
    const ratingDisplay = document.getElementById('ratingDisplay');
    const stars = ratingStarsContainer ? ratingStarsContainer.querySelectorAll('.rating-star') : null; // Check container first

    // --- DEBUG LOGS ---
    console.log("Rating Input Element:", ratingInput);
    console.log("Rating Stars Container:", ratingStarsContainer);
    console.log("Stars Found:", stars);
    console.log("Initial Rating Value from Input:", ratingInput ? ratingInput.value : 'Input not found');
    // --- END DEBUG LOGS ---

    // Check if elements were found before proceeding
    if (!ratingStarsContainer || !ratingInput || !ratingDisplay || !stars) {
        console.error("One or more rating elements not found in the DOM!");
        return; // Stop execution if elements are missing
    }

    // Function to update star appearance and hidden input
    function updateRating(ratingValue) {
        stars.forEach(star => {
            const starRating = parseInt(star.dataset.rating);
            if (starRating <= ratingValue) {
                star.classList.remove('text-gray-300');
                star.classList.add('text-yellow-400');
            } else {
                star.classList.remove('text-yellow-400');
                star.classList.add('text-gray-300');
            }
        });
        ratingInput.value = ratingValue;
        ratingDisplay.textContent = ratingValue ? `${ratingValue} / 5 Stars` : 'Select a rating';
        console.log("updateRating called with:", ratingValue); 
    }

     // Initialize stars based on current rating from hidden input
     const initialRating = parseInt(ratingInput.value);
     console.log("Parsed Initial Rating:", initialRating); // Log parsed value

     if (!isNaN(initialRating) && initialRating >= 1 && initialRating <= 5) { // Use !isNaN for better check
         updateRating(initialRating);
     } else {
         updateRating(0); // Ensure display text is correct if no initial rating
     }
 
     // Add click event listeners to stars
     stars.forEach(star => {
         star.addEventListener('click', function() {
             const ratingValue = parseInt(this.dataset.rating);
             console.log("Star clicked! Rating:", ratingValue); // Log click event
             updateRating(ratingValue);
         });
     });
 });