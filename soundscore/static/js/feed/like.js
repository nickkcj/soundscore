document.addEventListener('DOMContentLoaded', function() {
    // Define heart animation styles once
    if (!document.getElementById('heart-animation-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'heart-animation-styles';
        styleSheet.innerHTML = `
            @keyframes heartBeat {
                0% { transform: scale(1); }
                15% { transform: scale(1.25); }
                30% { transform: scale(1); }
                45% { transform: scale(1.15); }
                60% { transform: scale(1); }
            }
            
            @keyframes countPop {
                0% { transform: scale(1); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }
            
            .animate-heart {
                animation: heartBeat 0.8s;
            }
            
            .animate-count {
                animation: countPop 0.4s;
            }
        `;
        document.head.appendChild(styleSheet);
    }

    document.querySelectorAll('.like-button').forEach(button => {
        // Set initial state based on data attribute
        const isLiked = button.getAttribute('data-liked') === 'true';
        const likeIcon = button.querySelector('.heart-icon');
        
        if (isLiked) {
            button.classList.add('text-pink-600');
            likeIcon.classList.add('text-pink-600');
            likeIcon.setAttribute('fill', 'currentColor');
        }
        
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const reviewId = this.getAttribute('data-review-id');
            const countDisplay = this.querySelector('.like-count');
            const likeIcon = this.querySelector('.heart-icon');
            
            // Start animation immediately for better UX
            likeIcon.classList.add('animate-heart');
            countDisplay.classList.add('animate-count');
            
            // Toggle visual state immediately (optimistic UI)
            const wasLiked = this.classList.contains('text-pink-600');
            
            if (!wasLiked) {
                this.classList.add('text-pink-600');
                likeIcon.classList.add('text-pink-600');
                likeIcon.setAttribute('fill', 'currentColor');
                countDisplay.textContent = (parseInt(countDisplay.textContent || '0') + 1).toString();
            } else {
                this.classList.remove('text-pink-600');
                likeIcon.classList.remove('text-pink-600');
                likeIcon.setAttribute('fill', 'none');
                const currentCount = parseInt(countDisplay.textContent || '0');
                if (currentCount > 0) {
                    countDisplay.textContent = (currentCount - 1).toString();
                }
            }
            
            try {
                // Remove animation classes after animation completes
                setTimeout(() => {
                    likeIcon.classList.remove('animate-heart');
                    countDisplay.classList.remove('animate-count');
                }, 800);
                
                // Get CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Send the like/unlike request
                const response = await fetch('/comments/likes/toggle/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ review_id: reviewId })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Update the UI based on the response
                countDisplay.textContent = data.count;
                
                if (data.liked) {
                    this.classList.add('text-pink-600');
                    likeIcon.classList.add('text-pink-600');
                    likeIcon.setAttribute('fill', 'currentColor');
                } else {
                    this.classList.remove('text-pink-600');
                    likeIcon.classList.remove('text-pink-600');
                    likeIcon.setAttribute('fill', 'none');
                }
                
                // Update the data attribute to reflect current state
                this.setAttribute('data-liked', data.liked);
                
            } catch (error) {
                console.error('Error toggling like:', error);
                alert('Something went wrong with the like operation. Please try again.');
            }
        });
    });
});