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

    // Track pending requests to prevent race conditions
    const pendingRequests = new Map();

    // Ensure each button only has one event listener
    window.initLikeButtons = function() {
        document.querySelectorAll('.like-button:not([data-initialized])').forEach(button => {
            // Mark this button as initialized to prevent multiple bindings
            button.setAttribute('data-initialized', 'true');
            
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
                if (!reviewId) {
                    console.error('Like button missing review ID');
                    return;
                }
                
                // Prevent multiple clicks while request is pending
                if (pendingRequests.has(reviewId)) {
                    console.log('Request already pending for review', reviewId);
                    return;
                }
                
                const countDisplay = this.querySelector('.like-count');
                const likeIcon = this.querySelector('.heart-icon');
                
                // Start animation
                likeIcon.classList.add('animate-heart');
                countDisplay.classList.add('animate-count');
                
                // Toggle visual state (optimistic UI)
                const wasLiked = this.classList.contains('text-pink-600');
                const originalCount = parseInt(countDisplay.textContent || '0');
                
                if (!wasLiked) {
                    this.classList.add('text-pink-600');
                    likeIcon.classList.add('text-pink-600');
                    likeIcon.setAttribute('fill', 'currentColor');
                    countDisplay.textContent = (originalCount + 1).toString();
                } else {
                    this.classList.remove('text-pink-600');
                    likeIcon.classList.remove('text-pink-600');
                    likeIcon.setAttribute('fill', 'none');
                    countDisplay.textContent = Math.max(0, originalCount - 1).toString();
                }
                
                // Mark this request as pending
                pendingRequests.set(reviewId, true);
                
                try {
                    // Remove animation classes after animation completes
                    setTimeout(() => {
                        likeIcon.classList.remove('animate-heart');
                        countDisplay.classList.remove('animate-count');
                    }, 800);
                    
                    // Get CSRF token - Get it from the meta tag instead of form field
                    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                                     document.querySelector('[name=csrfmiddlewaretoken]').value;
                    
                    // Send request
                    const response = await fetch('/feed/comments/likes/toggle/', {
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
                    
                    // Trust the server's count completely
                    countDisplay.textContent = data.count;
                    
                    // Set the correct visual state based on server response
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
                    
                    // Revert to original state on error
                    countDisplay.textContent = originalCount.toString();
                    if (wasLiked) {
                        this.classList.add('text-pink-600');
                        likeIcon.classList.add('text-pink-600');
                        likeIcon.setAttribute('fill', 'currentColor');
                    } else {
                        this.classList.remove('text-pink-600');
                        likeIcon.classList.remove('text-pink-600');
                        likeIcon.setAttribute('fill', 'none');
                    }
                } finally {
                    // Clear the pending request
                    pendingRequests.delete(reviewId);
                }
            });
        });
    };

    // Initialize like buttons when the page loads
    initLikeButtons();
    
    // If you have a load more function, make sure it calls initLikeButtons() after adding new content
    // Example: After adding new reviews to the DOM
    // document.addEventListener('reviewsLoaded', initLikeButtons);
});