document.addEventListener('DOMContentLoaded', function() {
    console.log("Filter by script loaded");
    const sortToggleBtn = document.getElementById('sort-toggle');
    
    if (sortToggleBtn) {
        sortToggleBtn.addEventListener('click', function() {
            console.log("Sort toggle clicked");
            
            // Toggle sort order
            const currentOrder = sortToggleBtn.getAttribute('data-sort-order') || 'desc';
            const newOrder = currentOrder === 'desc' ? 'asc' : 'desc';
            
            // Update button state
            sortToggleBtn.setAttribute('data-sort-order', newOrder);
            
            // Update UI
            const sortLabel = document.getElementById('sort-label');
            const sortIcon = document.getElementById('sort-icon');
            
            if (sortLabel) {
                sortLabel.textContent = newOrder === 'desc' ? 'Latest first' : 'Oldest first';
            }
            
            if (sortIcon) {
                sortIcon.style.transform = newOrder === 'asc' ? 'rotate(180deg)' : '';
            }
            
            // Find reviews container
            const reviewsContainer = document.querySelector('.space-y-10');
            if (!reviewsContainer) {
                console.error("Reviews container not found!");
                return;
            }
            
            // Show loading state
            reviewsContainer.classList.add('opacity-50');
            
            // Reset load more button
            const loadMoreBtn = document.getElementById('load-more-btn');
            if (loadMoreBtn) {
                loadMoreBtn.setAttribute('data-page', '1');
            }
            
            // Fetch reviews with new sort order
            fetch(`/comments/feed/load-more/?page=0&page_size=5&exclude_ids=&sort_order=${newOrder}&comments_per_review=10`)
                .then(response => response.json())
                .then(data => {
                    console.log(`Received ${data.reviews.length} reviews with sort order: ${newOrder}`);
                    
                    // Clear existing reviews
                    reviewsContainer.innerHTML = '';
                    
                    if (data.reviews && data.reviews.length > 0) {
                        // Create new review elements
                        data.reviews.forEach(review => {
                            const reviewEl = document.createElement('div');
                            reviewEl.className = "bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden transform transition-all duration-200 hover:shadow-lg";
                            reviewEl.setAttribute('data-review-id', review.id);
                            
                            // Generate HTML for the review
                            reviewEl.innerHTML = generateReviewHTML(review);
                            
                            // Append to container
                            reviewsContainer.appendChild(reviewEl);
                        });
                        
                        // Re-initialize interactive elements
                        initializeReviews();
                    } else {
                        // No reviews found
                        reviewsContainer.innerHTML = `
                            <div class="flex flex-col items-center justify-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 text-pink-200 mb-4">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z" />
                                </svg>
                                <p class="text-gray-500 font-medium">No reviews found.</p>
                            </div>
                        `;
                    }
                    
                    // Update load more button
                    if (loadMoreBtn) {
                        loadMoreBtn.disabled = !data.has_more;
                        loadMoreBtn.classList.toggle('opacity-50', !data.has_more);
                    }
                    
                    // Remove loading state
                    reviewsContainer.classList.remove('opacity-50');
                })
                .catch(error => {
                    console.error("Error fetching sorted reviews:", error);
                    reviewsContainer.classList.remove('opacity-50');
                });
        });
    } else {
        console.error("Sort toggle button not found!");
    }
    
    // Helper function to generate review HTML
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
    
    // Re-initialize interactive elements on dynamically added reviews
    function initializeReviews() {
        // Initialize like buttons
        document.querySelectorAll('.like-button').forEach(button => {
            button.addEventListener('click', function() {
                // Like button handling logic
            });
        });
        
        // Initialize comment buttons
        document.querySelectorAll('.comment-button').forEach(button => {
            button.addEventListener('click', function() {
                // Comment button handling logic
            });
        });
    }
});