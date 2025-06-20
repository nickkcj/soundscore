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
    
    // A function to initialize all event listeners
    function initializeEventListeners() {
        // Check if elements exist before adding listeners
        if (openModalBtn) {
            openModalBtn.addEventListener('click', function (e) {
                e.preventDefault();
                openModal();
            });
        }
    
        if (openModalEmptyBtn) {
            openModalEmptyBtn.addEventListener('click', function (e) {
                e.preventDefault();
                openModal();
            });
        }
    
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', closeModal);
        }
    
        if (createReviewModal) {
            createReviewModal.addEventListener('click', function (e) {
                if (e.target === createReviewModal) {
                    closeModal();
                }
            });
        }

        if (doneButton) {
            doneButton.addEventListener('click', function() {
                window.location.reload();
            });
        }

        if (artistInput) {
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
        }

        if (backToSearchBtn) {
            backToSearchBtn.addEventListener('click', function() {
                reviewStep.classList.add('hidden');
                searchStep.classList.remove('hidden');
            });
        }
        
        if (ratingStars) {
            ratingStars.forEach(star => {
                star.addEventListener('click', function() {
                    const ratingValue = this.getAttribute('data-rating');
                    setRating(ratingValue);
                    
                    ratingContainer.classList.add('bg-pink-50');
                    setTimeout(() => {
                        ratingContainer.classList.remove('bg-pink-50');
                    }, 300);
                });
            });
        }

        if (reviewForm) {
            reviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitReview();
            });
        }

        initializeReviewExpandButtons();
    }
    
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
    
    // Event listeners for opening modal - MOVED to initializeEventListeners
    
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
        
        fetch(`/reviews/api/search-albums/?q=${encodeURIComponent(query)}`)
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
        
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        
        fetch('/reviews/api/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Failed to submit review') });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                reviewStep.classList.add('hidden');
                successStep.classList.remove('hidden');
            } else {
                throw new Error(data.error || 'An unknown error occurred');
            }
        })
        .catch(error => {
            console.error('Submit error:', error);
            alert(`Error: ${error.message}`);
        });
    }
    
    // Review text "See more/less" functionality
    function initializeReviewExpandButtons() {
        const reviewContainers = document.querySelectorAll('.review-container');
        reviewContainers.forEach(container => {
            const textElement = container.querySelector('.review-text-collapsed');
            // Check if text is actually clamped
            if (textElement && textElement.scrollHeight > textElement.clientHeight) {
                const expandButton = document.createElement('button');
                expandButton.textContent = 'See more';
                expandButton.className = 'text-pink-600 hover:underline text-xs mt-1';
                container.appendChild(expandButton);

                expandButton.addEventListener('click', () => {
                    if (textElement.classList.contains('line-clamp-2')) {
                        textElement.classList.remove('line-clamp-2');
                        expandButton.textContent = 'See less';
                    } else {
                        textElement.classList.add('line-clamp-2');
                        expandButton.textContent = 'See more';
                    }
                });
            }
        });
    }
    
    // Initialize everything
    initializeEventListeners();
});