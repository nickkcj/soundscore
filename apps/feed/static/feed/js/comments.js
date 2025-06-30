document.addEventListener('DOMContentLoaded', function() {
    console.log('Comments.js loaded - initializing comment functionality');
    
    // Debug click events on the page to ensure buttons are being detected
    document.addEventListener('click', function(event) {
        // Let's add more specific targeting to catch clicks on any part of the button or its children
        const commentButton = event.target.closest('.comment-button');
        
        if (commentButton) {
            console.log('Comment button clicked!', commentButton);
            const reviewId = commentButton.getAttribute('data-review-id');
            console.log('Review ID:', reviewId);
            
            if (!reviewId) {
                console.error('Missing review ID on comment button');
                return;
            }
            
            const commentFormSelector = `.comment-form-container[data-review-id="${reviewId}"]`;
            console.log('Looking for form with selector:', commentFormSelector);
            
            const commentForm = document.querySelector(commentFormSelector);
            
            if (commentForm) {
                console.log('Found comment form, current display:', getComputedStyle(commentForm).display);
                
                // Check if it's visible
                const isVisible = getComputedStyle(commentForm).display !== 'none';
                
                // Toggle visibility more forcefully
                if (isVisible) {
                    commentForm.style.display = 'none';
                    console.log('Hiding comment form');
                } else {
                    commentForm.style.display = 'block';
                    console.log('Showing comment form');
                    
                    // Focus on the textarea
                    const textarea = commentForm.querySelector('textarea');
                    if (textarea) {
                        console.log('Focusing on textarea');
                        setTimeout(() => textarea.focus(), 0);
                    }
                }
            } else {
                console.error(`Comment form for review ${reviewId} not found`);
                // Debug all available comment forms
                const allForms = document.querySelectorAll('.comment-form-container');
                console.log(`Found ${allForms.length} total comment forms:`, allForms);
                
                // List all reviewIds
                const reviewIds = [];
                allForms.forEach(form => {
                    reviewIds.push(form.getAttribute('data-review-id'));
                });
                console.log('Available review IDs:', reviewIds);
            }
        }
    });
    
    // Rest of your form submission code stays the same
    document.addEventListener('submit', async function(event) {
        if (event.target.classList.contains('comment-form')) {
            event.preventDefault();
            const form = event.target;
            
            const reviewId = form.getAttribute('data-review-id');
            const textarea = form.querySelector('textarea[name="text"]');
            const parentIdInput = form.querySelector('input[name="parent_id"]');
            const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            // Validate inputs
            if (!textarea || !csrfToken) {
                console.error('Missing required form elements');
                return;
            }
            
            const commentText = textarea.value.trim();
            if (!commentText) return;
            
            const parentId = parentIdInput ? parentIdInput.value || null : null;

            try {
                const response = await fetch('/feed/comments/post/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        review_id: reviewId,
                        text: commentText,
                        parent_id: parentId
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Clear the textarea
                    textarea.value = '';
                    
                    // Show success message
                    const successMessage = form.parentNode.querySelector('.comment-success');
                    if (successMessage) {
                        successMessage.classList.remove('hidden');
                        // Hide success message after 3 seconds
                        setTimeout(() => {
                            successMessage.classList.add('hidden');
                        }, 3000);
                    }
                    
                    // Refresh the page after successful comment
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    alert('Error: ' + (data.error || 'Failed to post comment'));
                }
            } catch (error) {
                console.error('Error posting comment:', error);
                alert('Something went wrong. Please try again.');
            }
        }
    });
    
    // Verify we have comment buttons at load time
    const commentButtons = document.querySelectorAll('.comment-button');
    console.log(`Found ${commentButtons.length} comment buttons on initial page load`);
    
    // Verify we have comment forms at load time
    const commentForms = document.querySelectorAll('.comment-form-container');
    console.log(`Found ${commentForms.length} comment form containers on initial page load`);
});