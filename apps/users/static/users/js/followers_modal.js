document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('followersModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const closeModalBtn = document.getElementById('closeModal');
    
    let currentType = '';
    let currentUsername = '';
    let currentPage = 1;
    let hasMore = false;
    
    // Open modal triggers
    document.querySelectorAll('.followers-btn, .following-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            currentType = this.getAttribute('data-type');
            currentUsername = this.getAttribute('data-username');
            currentPage = 1;
            
            // Set modal title
            modalTitle.textContent = currentType === 'followers' ? 'Followers' : 'Following';
            
            // Clear previous content
            modalContent.innerHTML = '';
            emptyState.classList.add('hidden');
            loadMoreContainer.classList.add('hidden');
            
            // Show modal and load data
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            loadData();
        });
    });
    
    // Close modal
    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
    
    closeModalBtn.addEventListener('click', closeModal);
    
    // Close on backdrop click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            closeModal();
        }
    });
    
    // Load more button
    loadMoreBtn.addEventListener('click', function() {
        currentPage++;
        loadData(true);
    });
    
    async function loadData(append = false) {
        // Show loading state
        if (!append) {
            loadingState.classList.remove('hidden');
        } else {
            loadMoreBtn.textContent = 'Loading...';
            loadMoreBtn.disabled = true;
        }
        
        try {
            const endpoint = currentType === 'followers' ? 'followers-modal' : 'following-modal';
            const response = await fetch(`/users/profile/${currentUsername}/${endpoint}/?page=${currentPage}`);
            const data = await response.json();
            
            if (data.success) {
                if (!append) {
                    modalContent.innerHTML = data.html;
                } else {
                    modalContent.innerHTML += data.html;
                }
                
                hasMore = data.has_more;
                
                // Show/hide load more button
                if (hasMore) {
                    loadMoreContainer.classList.remove('hidden');
                } else {
                    loadMoreContainer.classList.add('hidden');
                }
                
                // Show empty state if no content
                if (data.html.trim() === '' && !append) {
                    emptyState.classList.remove('hidden');
                    document.getElementById('emptyTitle').textContent = 
                        currentType === 'followers' ? 'No followers yet' : 'Not following anyone yet';
                    document.getElementById('emptyMessage').textContent = 
                        currentType === 'followers' 
                            ? 'This user doesn\'t have any followers yet.' 
                            : 'This user isn\'t following anyone yet.';
                }
                
                // Attach follow button listeners
                attachFollowListeners();
                
            } else {
                console.error('Error loading data:', data.message);
            }
        } catch (error) {
            console.error('Network error:', error);
        } finally {
            loadingState.classList.add('hidden');
            loadMoreBtn.textContent = 'Load more';
            loadMoreBtn.disabled = false;
        }
    }
    
    function attachFollowListeners() {
        document.querySelectorAll('.follow-btn-modal').forEach(btn => {
            btn.addEventListener('click', async function() {
                const username = this.getAttribute('data-username');
                const isFollowing = this.getAttribute('data-following') === 'true';
                const endpoint = isFollowing ? 'unfollow' : 'follow';
                
                // Disable button
                this.disabled = true;
                this.classList.add('opacity-50');
                
                try {
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
                    
                    const response = await fetch(`/users/profile/${username}/${endpoint}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({})
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        if (data.success) {
                            // Update button state
                            this.setAttribute('data-following', data.following ? 'true' : 'false');
                            
                            if (data.following) {
                                this.textContent = 'Following';
                                this.className = 'follow-btn-modal px-3 py-1 bg-gray-500 text-white rounded-lg text-xs font-medium hover:bg-gray-600 transition-colors';
                            } else {
                                this.textContent = 'Follow';
                                this.className = 'follow-btn-modal px-3 py-1 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-lg text-xs font-medium hover:from-pink-600 hover:to-pink-700 transition-colors';
                            }
                        }
                    }
                } catch (error) {
                    console.error('Follow error:', error);
                } finally {
                    this.disabled = false;
                    this.classList.remove('opacity-50');
                }
            });
        });
    }
});