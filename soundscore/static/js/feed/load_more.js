console.log('-------- feed.js loaded --------');

// Create a global Set to track review IDs without duplicates
window.loadedReviewIds = new Set();

// Add this function at the top of your file (or at a proper location)
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// When the page loads, initialize all buttons
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOMContentLoaded fired");
    
    // Store initial review IDs for filtering
    const initialReviewIds = Array.from(document.querySelectorAll('[data-review-id]'))
        .map(el => el.getAttribute('data-review-id'));
    console.log("Initial loaded review IDs:", initialReviewIds);
    
    // Get load more button
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (!loadMoreBtn) {
        console.error("Load more button not found!");
        return;
    }
    
    // IMPORTANT FIX: Find the container where reviews should be appended
    // This should match the class used in your redesigned template
    const reviewsContainer = document.querySelector('.space-y-10');
    if (!reviewsContainer) {
        console.error("Reviews container not found! Looking for element with class 'space-y-10'");
        // Try other potential container selectors if the main one isn't found
        const alternativeContainers = [
            document.querySelector('.reviews-container'),
            document.querySelector('#reviews-list'),
            document.querySelector('.feed-items')
        ];
        
        // Log what containers we do find on the page
        console.log("Available containers with similar classes:", 
            [...document.querySelectorAll('[class*="reviews"],[class*="feed"],[id*="reviews"],[id*="feed"]')]
            .map(el => `${el.tagName}.${el.className}#${el.id}`));
    }
    
    loadMoreBtn.addEventListener('click', function() {
        // Get current page number from button data attribute
        let currentPage = parseInt(loadMoreBtn.getAttribute('data-page')) || 1;
        
        // Get sort order
        const sortToggleBtn = document.getElementById('sort-toggle');
        const sortOrder = sortToggleBtn ? sortToggleBtn.getAttribute('data-sort-order') || 'desc' : 'desc';
        
        // Show loading state
        loadMoreBtn.disabled = true;
        loadMoreBtn.innerHTML = '<span>Loading...</span>';
        
        // Get IDs of reviews already displayed to avoid duplicates
        const displayedReviewIds = Array.from(document.querySelectorAll('[data-review-id]'))
            .map(el => el.getAttribute('data-review-id')).join(',');
        
        // Fetch more reviews
        fetch(`/comments/feed/load-more/?page=${currentPage}&page_size=5&exclude_ids=${displayedReviewIds}&sort_order=${sortOrder}&comments_per_review=10`)
            .then(response => response.json())
            .then(data => {
                console.log("Load more response:", data);
                
                // Find container again in case it was modified since page load
                const reviewsContainer = document.querySelector('.space-y-10');
                
                if (!reviewsContainer) {
                    console.error("CRITICAL ERROR: Reviews container not found when trying to append new reviews!");
                    console.log("Current HTML structure:", document.body.innerHTML);
                    throw new Error("Reviews container not found");
                }
                
                // Process and append reviews
                if (data.reviews && data.reviews.length > 0) {
                    data.reviews.forEach(review => {
                        try {
                            // Create a container for the new review
                            const reviewElement = document.createElement('div');
                            reviewElement.className = "bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden transform transition-all duration-200 hover:shadow-lg";
                            reviewElement.setAttribute('data-review-id', review.id);
                            
                            // Set the inner HTML for the review
                            reviewElement.innerHTML = generateReviewHTML(review);
                            
                            // Append to container
                            reviewsContainer.appendChild(reviewElement);
                            
                            // Initialize interaction features on new review
                            initializeNewReview(reviewElement);
                        } catch (err) {
                            console.error("Error creating review element:", err);
                        }
                    });
                    
                    // Update page number for next load
                    loadMoreBtn.setAttribute('data-page', (currentPage + 1).toString());
                }
                
                // Update button state
                loadMoreBtn.disabled = !data.has_more;
                if (!data.has_more) {
                    loadMoreBtn.classList.add('opacity-50');
                }
                
                // Reset button text
                loadMoreBtn.innerHTML = `
                    <span>Load more</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                `;
            })
            .catch(error => {
                console.error("Error:", error);
                loadMoreBtn.disabled = false;
                loadMoreBtn.innerHTML = '<span>Error loading. Try again</span>';
            });
    });
    
    // Helper function to format review HTML
    function generateReviewHTML(review) {
        // Create stars display
        let starsHTML = '';
        for (let i = 1; i <= 5; i++) {
            starsHTML += `<svg class="w-3.5 h-3.5 ${i <= review.rating ? 'fill-current' : 'text-gray-300'}" viewBox="0 0 20 20">
                            <path d="M10 15l-5.878 3.09L5.5 12.5 1 8.91l6.122-.89L10 2.5l2.878 5.52 6.122.89-4.5 3.59 1.378 5.59z"/>
                          </svg>`;
        }
        
        // Format review text section
        const reviewTextSection = review.text ? `
            <div class="px-6 pb-5">
                <p class="text-gray-700 text-sm italic line-clamp-4 bg-gray-50 p-4 rounded-lg border-l-4 border-pink-200">"${review.text}"</p>
            </div>` : '';
        
        // Return complete HTML
        return `
            <!-- User header -->
            <div class="flex items-center px-6 pt-5 pb-3 border-b border-gray-50">
                <div class="w-12 h-12 rounded-full bg-gray-200 overflow-hidden mr-4 ring-2 ring-pink-100">
                    <img src="${review.soundscore_user?.profile_picture || '/static/images/default.jpg'}" 
                         class="w-full h-full object-cover" alt="">
                </div>
                <div class="flex-1">
                    <a href="/profile/${review.soundscore_user?.username}" 
                       class="font-semibold text-gray-900 hover:underline hover:text-pink-600 transition-colors">
                      @${review.soundscore_user?.username}
                    </a>
                    <div class="text-xs text-gray-500">${review.created_at?.slice(0, 10)}</div>
                </div>
                <div class="flex items-center bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-full px-3 py-1.5 shadow-sm">
                    <div class="flex items-center text-yellow-400">
                        ${starsHTML}
                    </div>
                    <span class="ml-2 text-xs font-medium text-gray-700">${review.rating}/5</span>
                </div>
            </div>
            
            <!-- Album content -->
            <div class="px-6 py-4">
                <div class="flex items-center space-x-5">
                    <div class="w-24 h-24 rounded-lg overflow-hidden flex-shrink-0 shadow-md">
                        <img src="${review.soundscore_album?.cover_image || '/static/images/default_album.png'}" 
                             alt="Cover" class="w-full h-full object-cover">
                    </div>
                    <div>
                        <h3 class="font-bold text-gray-800 text-lg mb-1">${review.soundscore_album?.title}</h3>
                        <p class="text-sm text-gray-600 bg-gray-50 px-2 py-1 rounded-full inline-block">${review.soundscore_album?.artist}</p>
                    </div>
                </div>
            </div>
            
            ${reviewTextSection}
            
            <!-- Interaction bar -->
            <div class="flex items-center justify-around px-6 py-3.5 border-t border-gray-100 bg-gray-50">
                <button class="like-button flex items-center text-gray-500 hover:text-pink-600 transition-colors group" 
                        data-review-id="${review.id}" 
                        data-liked="${review.is_liked || false}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="heart-icon h-5 w-5 transition-all duration-300 ${review.is_liked ? 'text-pink-600 fill-current' : ''} group-hover:scale-110" 
                         fill="${review.is_liked ? 'currentColor' : 'none'}" 
                         viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <span class="ml-2 text-xs like-count transition-all duration-300 font-medium">${review.like_count || 0}</span>
                </button>
                
                <button class="flex items-center text-gray-500 hover:text-pink-600 transition-colors group comment-button" data-review-id="${review.id}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <span class="ml-2 text-xs font-medium">Comment (${review.comment_count || 0})</span>
                </button>
                
                <button class="flex items-center text-gray-500 hover:text-pink-600 transition-colors group">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                    <span class="ml-2 text-xs font-medium">Share</span>
                </button>
            </div>
        `;
    }
    
    // Function to initialize features on newly created review elements
    function initializeNewReview(reviewElement) {
        console.log("Initializing new review:", reviewElement.getAttribute('data-review-id'));
        
        // Initialize like button
        const likeButton = reviewElement.querySelector('.like-button');
        if (likeButton) {
            likeButton.addEventListener('click', function() {
                const reviewId = this.getAttribute('data-review-id');
                const liked = this.getAttribute('data-liked') === 'true';
                
                fetch('/comments/feed/toggle-like/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ review_id: reviewId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update UI
                        const heartIcon = this.querySelector('.heart-icon');
                        const likeCount = this.querySelector('.like-count');
                        
                        this.setAttribute('data-liked', (!liked).toString());
                        
                        if (!liked) {
                            // Like
                            heartIcon.classList.add('text-pink-600', 'fill-current');
                            heartIcon.setAttribute('fill', 'currentColor');
                        } else {
                            // Unlike
                            heartIcon.classList.remove('text-pink-600', 'fill-current');
                            heartIcon.setAttribute('fill', 'none');
                        }
                        
                        likeCount.textContent = data.like_count;
                    }
                })
                .catch(error => console.error('Error toggling like:', error));
            });
        }
        
        // Initialize comment button
        console.log("Initializing comment buttons");
        const commentBtn = reviewElement.querySelector('.comment-button');
        if (commentBtn) {
            commentBtn.addEventListener('click', function() {
                // Your comment handling logic
                console.log("Comment button clicked for review:", this.getAttribute('data-review-id'));
            });
        }
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let value = `; ${document.cookie}`;
        let parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    // Initialize comment buttons
    console.log("Initializing comment buttons");
    document.querySelectorAll('.comment-button').forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const formContainer = document.querySelector(`.comment-form-container[data-review-id="${reviewId}"]`);
            
            if (formContainer) {
                formContainer.classList.toggle('hidden');
                const textarea = formContainer.querySelector('textarea');
                if (textarea && !formContainer.classList.contains('hidden')) {
                    textarea.focus();
                }
            }
        });
    });
    
    // Initialize comment forms
    console.log("Initializing comment forms");
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const reviewId = this.getAttribute('data-review-id');
            const textField = this.querySelector('textarea[name="text"]');
            const parentField = this.querySelector('input[name="parent_id"]');
            const successMsg = this.closest('.comment-form-container').querySelector('.comment-success');
            
            if (textField && textField.value.trim()) {
                const commentData = {
                    review_id: reviewId,
                    text: textField.value.trim()
                };
                
                if (parentField && parentField.value) {
                    commentData.parent_id = parentField.value;
                }
                
                fetch('/comments/feed/post-comment/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(commentData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        textField.value = '';
                        if (successMsg) {
                            successMsg.classList.remove('hidden');
                            setTimeout(() => {
                                successMsg.classList.add('hidden');
                            }, 3000);
                        }
                        
                        // Update comment count
                        const commentBtn = document.querySelector(`.comment-button[data-review-id="${reviewId}"]`);
                        if (commentBtn) {
                            const countSpan = commentBtn.querySelector('span');
                            if (countSpan) {
                                const currentCount = parseInt(countSpan.textContent.match(/\d+/) || '0');
                                countSpan.textContent = `Comment (${currentCount + 1})`;
                            }
                        }
                    }
                })
                .catch(error => console.error('Error posting comment:', error));
            }
        });
    });
});

// Make these functions global so they can be called from anywhere
window.initCommentButtons = function() {
    console.log('Initializing comment buttons');
    document.querySelectorAll('.comment-button:not([data-initialized])').forEach(button => {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const reviewId = this.getAttribute('data-review-id');
            const formContainer = document.querySelector(`.comment-form-container[data-review-id="${reviewId}"]`);
            if (formContainer) {
                formContainer.classList.toggle('hidden');
                const textarea = formContainer.querySelector('textarea');
                if (textarea && !formContainer.classList.contains('hidden')) {
                    textarea.focus();
                }
            }
        });
    });
}

// Global function to submit a comment
window.submitComment = function(formElement) {
    const reviewId = formElement.getAttribute('data-review-id');
    const textField = formElement.querySelector('textarea[name="text"]');
    const parentField = formElement.querySelector('input[name="parent_id"]');
    const successMsg = formElement.closest('.comment-form-container').querySelector('.comment-success');
    
    if (textField && textField.value.trim()) {
        const commentData = {
            review_id: reviewId,
            text: textField.value.trim()
        };
        
        if (parentField && parentField.value) {
            commentData.parent_id = parentField.value;
        }
        
        fetch('/comments/feed/post-comment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(commentData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                textField.value = '';
                if (successMsg) {
                    successMsg.classList.remove('hidden');
                    setTimeout(() => {
                        successMsg.classList.add('hidden');
                    }, 3000);
                }
                
                // Update comment count
                const commentBtn = document.querySelector(`.comment-button[data-review-id="${reviewId}"]`);
                if (commentBtn) {
                    const countSpan = commentBtn.querySelector('span');
                    if (countSpan) {
                        const currentCount = parseInt(countSpan.textContent.match(/\d+/) || '0');
                        countSpan.textContent = `Comment (${currentCount + 1})`;
                    }
                }
            }
        })
        .catch(error => console.error('Error posting comment:', error));
    }
}

// Global function to initialize like buttons
window.initLikeButtons = function() {
    console.log('Initializing like buttons');
    document.querySelectorAll('.like-button:not([data-initialized])').forEach(button => {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const liked = this.getAttribute('data-liked') === 'true';
            
            fetch('/comments/feed/toggle-like/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ review_id: reviewId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    const heartIcon = this.querySelector('.heart-icon');
                    const likeCount = this.querySelector('.like-count');
                    
                    this.setAttribute('data-liked', (!liked).toString());
                    
                    if (!liked) {
                        // Like
                        heartIcon.classList.add('text-pink-600', 'fill-current');
                        heartIcon.setAttribute('fill', 'currentColor');
                    } else {
                        // Unlike
                        heartIcon.classList.remove('text-pink-600', 'fill-current');
                        heartIcon.setAttribute('fill', 'none');
                    }
                    
                    likeCount.textContent = data.like_count;
                }
            })
            .catch(error => console.error('Error toggling like:', error));
        });
    });
}

// Initial call to load more reviews if needed
document.addEventListener('DOMContentLoaded', function() {
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (loadMoreBtn) {
        loadMoreBtn.click();
    }
});