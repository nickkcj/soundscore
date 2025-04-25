console.log('-------- feed.js loaded --------');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded fired');
    
    // Add this at the start - keep track of which review IDs we've already seen
    const loadedReviewIds = [];
    
    // Find all initial reviews and store their IDs
    document.querySelectorAll('[data-review-id]').forEach(review => {
        const id = review.getAttribute('data-review-id');
        if (id) loadedReviewIds.push(parseInt(id));
    });
    
    console.log('Initial loaded review IDs:', loadedReviewIds);
    
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
            
            // Make AJAX request with the loaded IDs
            fetch(`/comments/feed/load-more/?page=${currentPage}&page_size=5&exclude_ids=${loadedReviewIds.join(',')}`)
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
                    
                    // Track the new review IDs
                    reviews.forEach(review => {
                        if (review.id) loadedReviewIds.push(review.id);
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
        
        template.innerHTML = `
            <div class="bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden transform transition-all duration-200 hover:shadow-lg">
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
                        <div class="text-xs text-gray-500">${review.created_at ? review.created_at.slice(0, 10) : ''}</div>
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
                        <span class="ml-2 text-xs font-medium">Comment</span>
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
        
        return template.content.firstElementChild;
    }
    
    // Helper function to generate star rating HTML
    function generateStarRating(rating) {
        let stars = '';
        for(let i = 1; i <= 5; i++) {
            stars += `<svg class="w-3.5 h-3.5 ${i <= rating ? 'fill-current' : 'text-gray-300'}" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09L5.5 12.5 1 8.91l6.122-.89L10 2.5l2.878 5.52 6.122.89-4.5 3.59 1.378 5.59z"/>
                      </svg>`;
        }
        return stars;
    }
    
    // Functions to re-initialize event handlers for dynamically added elements
    function initCommentButtons() {
        document.querySelectorAll('.comment-button').forEach(button => {
            if (!button.hasAttribute('data-initialized')) {
                button.setAttribute('data-initialized', 'true');
                button.addEventListener('click', function() {
                    const reviewId = this.getAttribute('data-review-id');
                    const formContainer = document.querySelector(`.comment-form-container[data-review-id="${reviewId}"]`);
                    if (formContainer) {
                        formContainer.classList.toggle('hidden');
                    }
                });
            }
        });
    }
    
    function initLikeButtons() {
        document.querySelectorAll('.like-button').forEach(button => {
            if (!button.hasAttribute('data-initialized')) {
                button.setAttribute('data-initialized', 'true');
                button.addEventListener('click', function() {
                    const reviewId = this.getAttribute('data-review-id');
                    const heartIcon = this.querySelector('.heart-icon');
                    const likeCount = this.querySelector('.like-count');
                    
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
                            if (data.liked) {
                                heartIcon.classList.add('text-pink-600', 'fill-current');
                                heartIcon.setAttribute('fill', 'currentColor');
                                this.setAttribute('data-liked', 'true');
                            } else {
                                heartIcon.classList.remove('text-pink-600', 'fill-current');
                                heartIcon.setAttribute('fill', 'none');
                                this.setAttribute('data-liked', 'false');
                            }
                            likeCount.textContent = data.count;
                        }
                    });
                });
            }
        });
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});