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
    console.log('DOMContentLoaded fired');
    
    // Find all initial reviews and store their IDs (without duplicates)
    document.querySelectorAll('[data-review-id]').forEach(review => {
        const id = review.getAttribute('data-review-id');
        if (id) window.loadedReviewIds.add(parseInt(id));
    });
    
    console.log('Initial loaded review IDs:', [...window.loadedReviewIds]);
    
    // Initialize the buttons on the initial page load
    initCommentButtons();
    initLikeButtons();
    initCommentForms(); // Add this to handle comment form submissions
    
    const loadMoreBtn = document.getElementById('load-more-btn');
    
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            // Get the current page
            const currentPage = parseInt(loadMoreBtn.getAttribute('data-page'));
            const hasMore = loadMoreBtn.getAttribute('data-has-more') === 'true';
            
            if (!hasMore) {
                loadMoreBtn.textContent = 'No more reviews';
                loadMoreBtn.disabled = true;
                return;
            }
            
            // Show loading state
            loadMoreBtn.textContent = 'Loading...';
            loadMoreBtn.disabled = true;
            
            // Get sort order from toggle button
            const sortToggle = document.getElementById('sort-toggle');
            const sortOrder = sortToggle ? sortToggle.getAttribute('data-sort-order') : 'desc';
            
            // Convert Set to Array for the API call
            const excludeIds = [...window.loadedReviewIds];
            
            // Make AJAX request with the loaded IDs (as a comma-separated string)
            fetch(`/comments/feed/load-more/?page=${currentPage}&page_size=5&exclude_ids=${excludeIds.join(',')}&sort_order=${sortOrder}`)
                .then(response => response.json())
                .then(data => {
                    console.log('Load more response:', data);
                    
                    if (data.error) {
                        console.error('Error loading more reviews:', data.error);
                        loadMoreBtn.textContent = 'Try again';
                        loadMoreBtn.disabled = false;
                        return;
                    }
                    
                    // Process the reviews
                    const reviews = data.reviews;
                    
                    // If no more reviews or empty array
                    if (!reviews || !reviews.length) {
                        loadMoreBtn.textContent = 'No more reviews';
                        loadMoreBtn.disabled = true;
                        loadMoreBtn.setAttribute('data-has-more', 'false');
                        return;
                    }
                    
                    // Track the new review IDs using the Set
                    reviews.forEach(review => {
                        if (review.id) window.loadedReviewIds.add(review.id);
                    });
                    
                    // Append the reviews to the feed
                    const reviewsContainer = document.querySelector('.space-y-20');
                    
                    reviews.forEach(review => {
                        const reviewElement = createReviewElement(review);
                        reviewsContainer.appendChild(reviewElement);
                    });
                    
                    // Update the button state
                    loadMoreBtn.setAttribute('data-page', currentPage + 1);
                    loadMoreBtn.setAttribute('data-has-more', data.has_more);
                    loadMoreBtn.textContent = 'Load more';
                    loadMoreBtn.disabled = false;
                    
                    // Re-initialize event handlers for new elements
                    initCommentButtons();
                    initLikeButtons();
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadMoreBtn.textContent = 'Try again';
                    loadMoreBtn.disabled = false;
                });
        });
    }
    
    // Function to create a review element from JSON data
    function createReviewElement(review) {
        const template = document.createElement('template');
        
        // Generate comment HTML if there are comments
        let commentsHTML = '';
        if (review.comment_count > 0) {
            commentsHTML = `
                <!-- Comments section - styled to match feed.html -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 mx-4 mt-4 mb-4 overflow-hidden">
                    <div class="px-4 py-2 border-b border-pink-100 flex items-center justify-between bg-pink-50">
                        <div class="text-xs text-pink-700 font-medium">Comments (${review.comment_count})</div>
                        ${review.comment_count > 2 ? '<a href="#" class="text-xs text-pink-600 hover:underline hover:text-pink-700">View all</a>' : ''}
                    </div>
                    
                    <!-- Comments list -->
                    <div class="divide-y divide-gray-50">
                        ${review.comments && review.comments.length > 0 ? review.comments.map(comment => `
                            <div class="px-4 py-3 flex hover:bg-gray-50 transition-colors">
                                <!-- Comment user avatar -->
                                <div class="w-8 h-8 rounded-full bg-gray-100 overflow-hidden flex-shrink-0 mr-3 ring-1 ring-gray-200">
                                    <img src="${comment.soundscore_user?.profile_picture || '/static/images/default_avatar.png'}" 
                                         class="w-full h-full object-cover" alt="">
                                </div>
                                
                                <!-- Comment content -->
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-baseline space-x-1">
                                        <a href="/user/${comment.soundscore_user?.username || ''}" 
                                           class="text-sm font-medium text-gray-900 hover:underline hover:text-pink-600 transition-colors truncate">
                                          @${comment.soundscore_user?.username || ''}
                                        </a>
                                        <span class="text-xs text-gray-400">${formatDate(comment.created_at)}</span>
                                    </div>
                                    <p class="text-xs text-gray-700 mt-0.5">${comment.text}</p>
                                </div>
                            </div>
                        `).join('') : ''}
                    </div>
                </div>
            `;
        }
        
        template.innerHTML = `
            <div class="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden transform transition-all duration-200 hover:shadow-lg" data-review-id="${review.id}">
                <!-- User header -->
                <div class="flex items-center px-6 pt-5 pb-3 border-b border-gray-50">
                    <div class="w-12 h-12 rounded-full bg-gray-200 overflow-hidden mr-4 ring-2 ring-pink-100">
                        <img src="${review.soundscore_user?.profile_picture || '/static/images/default.jpg'}" 
                             class="w-full h-full object-cover" alt="">
                    </div>
                    <div class="flex-1">
                        <a href="/user/${review.soundscore_user?.username || ''}" 
                           class="font-semibold text-gray-900 hover:underline hover:text-pink-600 transition-colors">
                          @${review.soundscore_user?.username || ''}
                        </a>
                        <div class="text-xs text-gray-500">${formatDate(review.created_at)}</div>
                    </div>
                    <div class="flex items-center bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-full px-3 py-1.5 shadow-sm">
                        <div class="flex items-center text-yellow-400">
                            ${generateStarRating(review.rating)}
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
                            <h3 class="font-bold text-gray-800 text-lg mb-1">${review.soundscore_album?.title || ''}</h3>
                            <p class="text-sm text-gray-600 bg-gray-50 px-2 py-1 rounded-full inline-block">${review.soundscore_album?.artist || ''}</p>
                        </div>
                    </div>
                </div>
                
                ${review.text ? `
                <!-- Review text -->
                <div class="px-6 pb-5">
                    <p class="text-gray-700 text-sm italic line-clamp-4 bg-gray-50 p-4 rounded-lg border-l-4 border-pink-200">"${review.text}"</p>
                </div>
                ` : ''}
                
                <!-- COMMENTS SECTION ADDED HERE with UPDATED STYLING -->
                ${commentsHTML}
                
                <!-- Interaction bar -->
                <div class="flex items-center justify-around px-6 py-3.5 border-t border-gray-100 bg-gray-50">
                    <button class="like-button flex items-center text-gray-500 hover:text-pink-600 transition-colors group" 
                            data-review-id="${review.id}" 
                            data-liked="${review.is_liked ? 'true' : 'false'}">
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
                
                <!-- Comment form (hidden by default) -->
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 px-5 py-4 mx-4 mb-4 comment-form-container hidden" data-review-id="${review.id}">
                    <form class="comment-form" data-review-id="${review.id}">
                        <div class="flex items-start gap-2">
                            <textarea name="text" rows="2" placeholder="Write a comment..." class="w-full p-2 border border-gray-200 rounded-lg text-sm focus:border-pink-300 focus:ring focus:ring-pink-200 focus:ring-opacity-50 transition"></textarea>
                            <button type="submit" class="px-3 py-1.5 bg-pink-500 text-white text-sm rounded hover:bg-pink-600 transition-colors shadow-sm">Post</button>
                        </div>
                        <input type="hidden" name="parent_id" value="">
                    </form>
                    <div class="text-xs text-gray-400 mt-2 hidden comment-success">Comment posted!</div>
                </div>
            </div>
        `;
        
        const newElement = template.content.firstElementChild;
        
        // Add the CSRF token to the form for dynamically created reviews
        const form = newElement.querySelector('.comment-form');
        if (form) {
            const csrfToken = getCookie('csrftoken');
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'csrfmiddlewaretoken';
            tokenInput.value = csrfToken;
            form.appendChild(tokenInput);
        }
        
        return newElement;
    }
    
    // Add a helper function to format dates to match your existing format
    function formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric',
            month: 'short', 
            day: 'numeric'
        });
    }
    
    // Star rating generator
    function generateStarRating(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        let stars = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            stars += '<svg class="w-3 h-3 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>';
        }
        
        // Half star
        if (halfStar) {
            stars += '<svg class="w-3 h-3 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M22 9.24l-7.19-.62L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21 12 17.27 18.18 21l-1.63-7.03L22 9.24zM12 15.4V6.1l1.71 4.04 4.38.38-3.32 2.88 1 4.28L12 15.4z"/></svg>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            stars += '<svg class="w-3 h-3 fill-current opacity-30" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>';
        }
        
        return stars;
    }
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
                
                // Focus the textarea when opening
                if (!formContainer.classList.contains('hidden')) {
                    const textarea = formContainer.querySelector('textarea');
                    if (textarea) textarea.focus();
                }
            }
        });
    });
};

window.initLikeButtons = function() {
    console.log('Initializing like buttons');
    document.querySelectorAll('.like-button:not([data-initialized])').forEach(button => {
        button.setAttribute('data-initialized', 'true');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const reviewId = this.getAttribute('data-review-id');
            const wasLiked = this.getAttribute('data-liked') === 'true';
            const heartIcon = this.querySelector('.heart-icon');
            const likeCount = this.querySelector('.like-count');
            
            // Visual feedback first
            if (!wasLiked) {
                heartIcon.classList.add('text-pink-600', 'fill-current');
                heartIcon.setAttribute('fill', 'currentColor');
                this.setAttribute('data-liked', 'true');
                likeCount.textContent = (parseInt(likeCount.textContent || '0') + 1).toString();
            } else {
                heartIcon.classList.remove('text-pink-600', 'fill-current');
                heartIcon.setAttribute('fill', 'none');
                this.setAttribute('data-liked', 'false');
                const currentCount = parseInt(likeCount.textContent || '0');
                if (currentCount > 0) {
                    likeCount.textContent = (currentCount - 1).toString();
                }
            }
            
            // Send request to server
            fetch('/comments/likes/toggle/', {
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
                    // Update UI based on server response
                    likeCount.textContent = data.count;
                }
            })
            .catch(error => {
                console.error('Like error:', error);
                // Revert UI changes if request failed
                if (!wasLiked) {
                    heartIcon.classList.remove('text-pink-600', 'fill-current');
                    heartIcon.setAttribute('fill', 'none');
                    this.setAttribute('data-liked', 'false');
                } else {
                    heartIcon.classList.add('text-pink-600', 'fill-current');
                    heartIcon.setAttribute('fill', 'currentColor');
                    this.setAttribute('data-liked', 'true');
                }
                likeCount.textContent = wasLiked ? 
                    (parseInt(likeCount.textContent || '0') + 1).toString() : 
                    (parseInt(likeCount.textContent || '0') - 1).toString();
            });
        });
    });
};

// Add a function to handle comment form submissions
window.initCommentForms = function() {
    console.log('Initializing comment forms');
    document.querySelectorAll('.comment-form:not([data-initialized])').forEach(form => {
        form.setAttribute('data-initialized', 'true');
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const reviewId = this.getAttribute('data-review-id');
            const commentText = this.querySelector('textarea[name="text"]').value;
            const successMsg = this.closest('.comment-form-container').querySelector('.comment-success');
            
            if (!commentText.trim()) return;
            
            fetch('/comments/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    review_id: reviewId,
                    text: commentText
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Clear the form
                    this.querySelector('textarea[name="text"]').value = '';
                    
                    // Show success message
                    if (successMsg) {
                        successMsg.classList.remove('hidden');
                        setTimeout(() => {
                            successMsg.classList.add('hidden');
                        }, 3000);
                    }
                    
                    // Update comment count
                    const commentButton = document.querySelector(`.comment-button[data-review-id="${reviewId}"]`);
                    const countSpan = commentButton.querySelector('span');
                    if (countSpan) {
                        const currentText = countSpan.textContent;
                        const newCount = data.comment_count || (parseInt(currentText.match(/\d+/) || 0) + 1);
                        countSpan.textContent = `Comment (${newCount})`;
                    }
                }
            })
            .catch(error => {
                console.error('Comment error:', error);
            });
        });
    });
};