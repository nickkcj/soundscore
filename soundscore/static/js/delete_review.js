document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const deleteModal = document.getElementById('deleteConfirmModal');
    const deleteModalContent = document.getElementById('deleteModalContent');
    const albumToDelete = document.getElementById('albumToDelete');
    const reviewToDeleteId = document.getElementById('reviewToDeleteId');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    
    // Add event listeners to all delete buttons
    const deleteButtons = document.querySelectorAll('.delete-review-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const albumTitle = this.getAttribute('data-album-title');
            
            // Set values in the modal
            albumToDelete.textContent = albumTitle;
            reviewToDeleteId.value = reviewId;
            
            // Show the modal with animation
            deleteModal.classList.remove('hidden');
            setTimeout(() => {
                deleteModalContent.classList.remove('scale-95', 'opacity-0');
                deleteModalContent.classList.add('scale-100', 'opacity-100');
            }, 10);
        });
    });
    
    // Handle cancel button
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    
    // Handle click outside modal to close
    deleteModal.addEventListener('click', function(e) {
        if (e.target === deleteModal) {
            closeDeleteModal();
        }
    });
    
    // Handle confirm delete
    confirmDeleteBtn.addEventListener('click', function() {
        const reviewId = reviewToDeleteId.value;
        if (!reviewId) return;
        
        // Show loading state
        confirmDeleteBtn.disabled = true;
        confirmDeleteBtn.innerHTML = '<svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Send AJAX request to delete
        fetch(`/delete-review/${reviewId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (response.ok) {
                // Remove the review card from the DOM
                const reviewCard = document.querySelector(`[data-review-id="${reviewId}"]`).closest('.flex.bg-white.rounded-lg');
                reviewCard.classList.add('scale-95', 'opacity-0');
                setTimeout(() => {
                    reviewCard.remove();
                    
                    // If no reviews left, show the "No Reviews Yet" message
                    const reviewsContainer = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.gap-6');
                    if (reviewsContainer && reviewsContainer.children.length === 0) {
                        location.reload(); // Reload to show empty state
                    }
                }, 300);
                
                closeDeleteModal();
            } else {
                throw new Error('Failed to delete review');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to delete review. Please try again.');
            confirmDeleteBtn.disabled = false;
            confirmDeleteBtn.textContent = 'Delete';
        });
    });
    
    function closeDeleteModal() {
        // Hide with animation
        deleteModalContent.classList.add('scale-95', 'opacity-0');
        deleteModalContent.classList.remove('scale-100', 'opacity-100');
        
        setTimeout(() => {
            deleteModal.classList.add('hidden');
            // Reset button state if needed
            confirmDeleteBtn.disabled = false;
            confirmDeleteBtn.textContent = 'Delete';
        }, 300);
    }
});