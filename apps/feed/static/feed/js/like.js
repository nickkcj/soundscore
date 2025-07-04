/**
 * Like System JavaScript
 * Handles like/unlike functionality with animations and optimistic UI updates
 * Manages heart animations, like counts, and server synchronization
 */

document.addEventListener('DOMContentLoaded', function() {
    /**
     * Define CSS animations for heart and count interactions
     * Only add styles once to avoid duplicates
     */
    if (!document.getElementById('heart-animation-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'heart-animation-styles';
        styleSheet.innerHTML = `
            /* Heart beat animation for like actions */
            @keyframes heartBeat {
                0% { transform: scale(1); }
                15% { transform: scale(1.25); }
                30% { transform: scale(1); }
                45% { transform: scale(1.15); }
                60% { transform: scale(1); }
            }
            
            /* Count number pop animation */
            @keyframes countPop {
                0% { transform: scale(1); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }
            
            /* CSS classes to trigger animations */
            .animate-heart {
                animation: heartBeat 0.8s;
            }
            
            .animate-count {
                animation: countPop 0.4s;
            }
        `;
        document.head.appendChild(styleSheet);
    }

    // Track pending requests to prevent race conditions and duplicate submissions
    const pendingRequests = new Map();

    /**
     * Initialize like buttons with proper event handlers and state management
     * Ensures each button only has one event listener to prevent duplicates
     */
    window.initLikeButtons = function() {
        document.querySelectorAll('.like-button:not([data-initialized])').forEach(button => {
            // Mark button as initialized to prevent multiple event bindings
            button.setAttribute('data-initialized', 'true');
            
            // Set initial visual state based on data attribute
            const isLiked = button.getAttribute('data-liked') === 'true';
            const likeIcon = button.querySelector('.heart-icon');
            
            if (isLiked) {
                // Apply liked styling for initially liked reviews
                button.classList.add('text-pink-600');
                likeIcon.classList.add('text-pink-600');
                likeIcon.setAttribute('fill', 'currentColor');
            }
            
            /**
             * Like button click handler with optimistic UI updates
             * Provides immediate feedback while waiting for server response
             */
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                
                // Get review ID and validate
                const reviewId = this.getAttribute('data-review-id');
                if (!reviewId) {
                    console.error('Like button missing review ID');
                    return;
                }
                
                // Prevent multiple simultaneous requests for the same review
                if (pendingRequests.has(reviewId)) {
                    console.log('Request already pending for review', reviewId);
                    return;
                }
                
                // Get UI elements for animation and state updates
                const countDisplay = this.querySelector('.like-count');
                const likeIcon = this.querySelector('.heart-icon');
                
                // Start visual animations immediately for better UX
                likeIcon.classList.add('animate-heart');
                countDisplay.classList.add('animate-count');
                
                // Optimistic UI update (assume success before server response)
                const wasLiked = this.classList.contains('text-pink-600');
                const originalCount = parseInt(countDisplay.textContent || '0');
                
                if (!wasLiked) {
                    // Apply liked state immediately
                    this.classList.add('text-pink-600');
                    likeIcon.classList.add('text-pink-600');
                    likeIcon.setAttribute('fill', 'currentColor');
                    countDisplay.textContent = (originalCount + 1).toString();
                } else {
                    // Apply unliked state immediately
                    this.classList.remove('text-pink-600');
                    likeIcon.classList.remove('text-pink-600');
                    likeIcon.setAttribute('fill', 'none');
                    countDisplay.textContent = Math.max(0, originalCount - 1).toString();
                }
                
                // Mark this request as pending to prevent duplicates
                pendingRequests.set(reviewId, true);
                
                try {
                    // Schedule animation cleanup after animation duration
                    setTimeout(() => {
                        likeIcon.classList.remove('animate-heart');
                        countDisplay.classList.remove('animate-count');
                    }, 800);
                    
                    // Get CSRF token for secure API request
                    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                                     document.querySelector('[name=csrfmiddlewaretoken]').value;
                    
                    // Send like toggle request to server
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
                    
                    // Parse server response
                    const data = await response.json();
                    
                    // Update UI with authoritative server data
                    countDisplay.textContent = data.count;
                    
                    // Apply correct visual state based on server response
                    if (data.liked) {
                        this.classList.add('text-pink-600');
                        likeIcon.classList.add('text-pink-600');
                        likeIcon.setAttribute('fill', 'currentColor');
                    } else {
                        this.classList.remove('text-pink-600');
                        likeIcon.classList.remove('text-pink-600');
                        likeIcon.setAttribute('fill', 'none');
                    }
                    
                    // Update data attribute to reflect current server state
                    this.setAttribute('data-liked', data.liked);
                    
                } catch (error) {
                    console.error('Error toggling like:', error);
                    
                    // Revert to original state on error to maintain data integrity
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
                    // Always clear the pending request flag
                    pendingRequests.delete(reviewId);
                }
            });
        });
    };

    // Initialize like buttons on initial page load
    initLikeButtons();
    
    // Note: If you have dynamic content loading (load more, etc.),
    // make sure to call initLikeButtons() after adding new reviews to the DOM
    // Example: document.addEventListener('reviewsLoaded', initLikeButtons);
});