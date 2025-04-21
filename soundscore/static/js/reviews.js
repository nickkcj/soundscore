document.addEventListener('DOMContentLoaded', function () {
    // DOM elements
    const createReviewModal = document.getElementById('createReviewModal');
    const modalContent = document.getElementById('modalContent');
    const openModalBtn = document.getElementById('openCreateReviewModal');
    console.log("Selected Button:", openModalBtn); // <-- ADD THIS LINE
    const openModalEmptyBtn = document.getElementById('openCreateReviewModalEmpty');
    const closeModalBtn = document.getElementById('closeCreateReviewModal');
    const artistInput = document.getElementById('artist_name');
    const searchResults = document.getElementById('searchResults');
    const searchSpinner = document.getElementById('searchSpinner');
    const searchStep = document.getElementById('searchStep');
    const reviewStep = document.getElementById('reviewStep');
    const successStep = document.getElementById('successStep');
    const backToSearchBtn = document.getElementById('backToSearch');
    const reviewForm = document.getElementById('reviewForm');
    const doneButton = document.getElementById('doneButton');
    const ratingStars = document.querySelectorAll('.rating-star');
    const ratingInput = document.getElementById('rating');
    const ratingDisplay = document.getElementById('ratingDisplay');
    const ratingContainer = document.getElementById('ratingContainer');
    
    // Selected album elements
    const selectedAlbumDisplay = document.getElementById('selectedAlbumDisplay');
    const selectedAlbumCover = document.getElementById('selectedAlbumCover');
    const selectedAlbumTitle = document.getElementById('selectedAlbumTitle');
    const selectedAlbumArtist = document.getElementById('selectedAlbumArtist');
    const albumIdInput = document.getElementById('album_id');
    const albumTitleInput = document.getElementById('album_title');
    const albumArtistInput = document.getElementById('album_artist');
    const albumCoverInput = document.getElementById('album_cover');
    
    let searchTimeout;
    
    // Open modal
    function openModal() {
        createReviewModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Prevent scrolling behind modal
        setTimeout(() => {
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('scale-100', 'opacity-100');
        }, 10);
        artistInput.focus();
    }
    
    // Event listeners for opening modal
    openModalBtn.addEventListener('click', function (e) {
        e.preventDefault();
        openModal();
    });
    
    if (openModalEmptyBtn) {
        openModalEmptyBtn.addEventListener('click', function (e) {
            e.preventDefault();
            openModal();
        });
    }
    
    // Close modal
    closeModalBtn.addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    createReviewModal.addEventListener('click', function (e) {
        if (e.target === createReviewModal) {
            closeModal();
        }
    });
    
    // Done button
    doneButton.addEventListener('click', function() {
        window.location.reload(); // Reload page to see the new review
    });
    
    // Search for albums with debounce
    artistInput.addEventListener('input', function () {
        if (searchTimeout) clearTimeout(searchTimeout);
        
        const query = this.value.trim();
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            searchAlbums(query);
        }, 500);
    });
    
    // Back button
    backToSearchBtn.addEventListener('click', function() {
        reviewStep.classList.add('hidden');
        searchStep.classList.remove('hidden');
    });
    
    // Rating stars
    ratingStars.forEach(star => {
        star.addEventListener('click', function() {
            const ratingValue = this.getAttribute('data-rating');
            setRating(ratingValue);
            
            // Add a subtle animation to the rating container
            ratingContainer.classList.add('bg-pink-50');
            setTimeout(() => {
                ratingContainer.classList.remove('bg-pink-50');
            }, 300);
        });
    });
    
    // Submit review
    reviewForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitReview();
    });
    
    // Functions
    
    function closeModal() {
        modalContent.classList.add('scale-95', 'opacity-0');
        modalContent.classList.remove('scale-100', 'opacity-100');
        
        setTimeout(() => {
            createReviewModal.classList.add('hidden');
            document.body.style.overflow = ''; // Re-enable scrolling
            resetModal();
        }, 200);
    }
    
    function resetModal() {
        artistInput.value = '';
        searchResults.innerHTML = '';
        reviewForm.reset();
        searchStep.classList.remove('hidden');
        reviewStep.classList.add('hidden');
        successStep.classList.add('hidden');
        setRating(0);
    }
    
    function searchAlbums(query) {
        searchSpinner.classList.remove('hidden');
        searchResults.innerHTML = '<p class="text-gray-500 text-center py-3">Searching...</p>';
        
        fetch(`/api/search-albums/?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) throw new Error('Search failed');
                return response.json();
            })
            .then(data => {
                displaySearchResults(data.albums || []);
            })
            .catch(error => {
                console.error('Search error:', error);
                searchResults.innerHTML = '<p class="text-red-500 text-center py-3">Error searching for albums. Please try again.</p>';
            })
            .finally(() => {
                searchSpinner.classList.add('hidden');
            });
    }
    
    function displaySearchResults(albums) {
        searchResults.innerHTML = '';
        
        if (albums.length === 0) {
            searchResults.innerHTML = '<p class="text-gray-500 text-center py-3">No albums found. Try another search term.</p>';
            return;
        }
        
        albums.forEach(album => {
            const resultItem = document.createElement('div');
            resultItem.className = 'flex items-center gap-3 p-3 hover:bg-pink-50 cursor-pointer border border-gray-200 rounded-xl mb-2 transition-colors duration-200';
            
            const releaseYear = album.release_date ? album.release_date.substring(0, 4) : '';
            
            resultItem.innerHTML = `
                <img src="${album.cover_url || '/static/images/default_album.png'}" 
                    alt="${album.title}" class="w-16 h-16 object-cover rounded-lg shadow-sm">
                <div>
                    <h3 class="font-medium text-gray-800">${album.title}</h3>
                    <p class="text-sm text-gray-500">${album.artist}</p>
                    <p class="text-xs text-gray-400">${releaseYear}</p>
                </div>
            `;
            
            resultItem.addEventListener('click', () => {
                selectAlbum(album);
            });
            
            searchResults.appendChild(resultItem);
        });
    }
    
    function selectAlbum(album) {
        // Set hidden inputs
        albumIdInput.value = album.id;
        albumTitleInput.value = album.title;
        albumArtistInput.value = album.artist;
        albumCoverInput.value = album.cover_url;
        
        // Update display
        selectedAlbumCover.src = album.cover_url || '/static/images/default_album.png';
        selectedAlbumTitle.textContent = album.title;
        selectedAlbumArtist.textContent = album.artist;
        
        // Switch to review step with animation
        searchStep.classList.add('hidden');
        reviewStep.classList.remove('hidden');
    }
    
    function setRating(value) {
        ratingInput.value = value;
        
        // Update stars
        ratingStars.forEach((star, index) => {
            if (index < value) {
                star.classList.remove('text-gray-300');
                star.classList.add('text-yellow-400');
            } else {
                star.classList.add('text-gray-300');
                star.classList.remove('text-yellow-400');
            }
        });
        
        // Update text
        if (value > 0) {
            ratingDisplay.textContent = `${value} star${value !== 1 ? 's' : ''}`;
            ratingDisplay.classList.add('text-yellow-600');
            ratingDisplay.classList.remove('text-gray-500');
        } else {
            ratingDisplay.textContent = 'Select a rating';
            ratingDisplay.classList.remove('text-yellow-600');
            ratingDisplay.classList.add('text-gray-500');
        }
    }
    
    function submitReview() {
        const formData = {
            album_id: albumIdInput.value,
            album_title: albumTitleInput.value,
            album_artist: albumArtistInput.value,
            album_cover: albumCoverInput.value,
            rating: ratingInput.value,
            review_text: document.getElementById('review_text').value,
            is_favorite: document.getElementById('is_favorite').checked
        };
        
        if (!formData.album_id || !formData.rating) {
            alert('Please select an album and provide a rating');
            return;
        }
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/api/create-review/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to submit review');
            return response.json();
        })
        .then(data => {
            // Show success message
            reviewStep.classList.add('hidden');
            successStep.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error submitting review:', error);
            alert('Error submitting review. Please try again.');
        });
    }
    
    // Review text "See more/less" functionality
    function initializeReviewExpandButtons() {
        console.log("[Reviews] Initializing review expand buttons...");
        const reviewContainers = document.querySelectorAll('.review-container');
        console.log(`[Reviews] Found ${reviewContainers.length} review containers.`);

        reviewContainers.forEach((container, index) => {
            const collapsedText = container.querySelector('.review-text-collapsed');

            if (!collapsedText || container.classList.contains('review-processed')) {
                return;
            }
            if (container.querySelector('.see-more-btn')) {
                 container.classList.add('review-processed');
                 return;
            }

            // Create expanded version - **Add break-words**
            const expandedText = document.createElement('p');
            expandedText.className = 'block w-full text-sm text-gray-600 italic mb-2 review-text-expanded hidden whitespace-normal break-words'; // <-- ADDED break-words
            expandedText.innerHTML = collapsedText.innerHTML;

            // Create buttons
            const seeMoreBtn = document.createElement('button');
            seeMoreBtn.type = 'button';
            seeMoreBtn.className = 'see-more-btn text-xs font-medium text-pink-500 hover:text-pink-600 transition-colors duration-200 ml-1';
            seeMoreBtn.textContent = 'See more';
            seeMoreBtn.classList.add('hidden'); // Start hidden

            const seeLessBtn = document.createElement('button');
            seeLessBtn.type = 'button';
            seeLessBtn.className = 'see-less-btn text-xs font-medium text-pink-500 hover:text-pink-600 transition-colors duration-200 ml-1 hidden';
            seeLessBtn.textContent = 'See less';

            // Append elements
            container.appendChild(expandedText);
            collapsedText.insertAdjacentElement('afterend', seeMoreBtn);
            expandedText.insertAdjacentElement('afterend', seeLessBtn);

            const textContent = collapsedText.textContent || "";
            const textLength = textContent.trim().length;
            // *** ADJUST THIS THRESHOLD AS NEEDED ***
            // If text is longer than this, it *might* be clamped visually.
            const MIN_LENGTH_FOR_POTENTIAL_CLAMP = 80;

            console.log(`[Reviews] Container ${index + 1}: Text length = ${textLength}.`);

            // *** Simplified Logic: Show button based on length only ***
            if (textLength > MIN_LENGTH_FOR_POTENTIAL_CLAMP) {
                // Assume long text *might* be clamped, so show the button.
                // The user can click it if needed.
                seeMoreBtn.classList.remove('hidden');
                console.log(`[Reviews] Container ${index + 1}: Text long enough, showing "See more" button.`);

                seeMoreBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    console.log(`[Reviews] Container ${index + 1}: "See more" clicked.`);
                    collapsedText.classList.add('hidden');
                    seeMoreBtn.classList.add('hidden');
                    expandedText.classList.remove('hidden');
                    seeLessBtn.classList.remove('hidden');
                });

                seeLessBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    console.log(`[Reviews] Container ${index + 1}: "See less" clicked.`);
                    expandedText.classList.add('hidden');
                    seeLessBtn.classList.add('hidden');
                    collapsedText.classList.remove('hidden');
                    seeMoreBtn.classList.remove('hidden');
                });
            } else {
                 console.log(`[Reviews] Container ${index + 1}: Text too short, removing buttons.`);
                 // Remove buttons if text is definitely too short
                 seeMoreBtn.remove();
                 seeLessBtn.remove();
                 expandedText.remove();
            }
            container.classList.add('review-processed');
        });
         console.log("[Reviews] Finished initializing review expand buttons.");
    }
    
    // Initialize on page load
    initializeReviewExpandButtons();
    
    // Also initialize after ajax content loads (if you load reviews dynamically)
    document.addEventListener('reviews-loaded', initializeReviewExpandButtons);
});