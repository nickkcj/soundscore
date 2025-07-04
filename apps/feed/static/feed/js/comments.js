/**
 * Comment System JavaScript
 * Handles comment form toggling, submission, and user interactions
 * Provides real-time feedback and form validation for review comments
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Comments.js loaded - initializing comment functionality');
    
    /**
     * Global click handler to detect comment button clicks
     * Uses event delegation to handle dynamically added content
     */
    document.addEventListener('click', function(event) {
        // Find the closest comment button element (handles clicks on child elements too)
        const commentButton = event.target.closest('.comment-button');
        
        if (commentButton) {
            console.log('Comment button clicked!', commentButton);
            
            // Extract the review ID from the button's data attribute
            const reviewId = commentButton.getAttribute('data-review-id');
            console.log('Review ID:', reviewId);
            
            // Validate that we have a review ID
            if (!reviewId) {
                console.error('Missing review ID on comment button');
                return;
            }
            
            // Build the selector to find the corresponding comment form
            const commentFormSelector = `.comment-form-container[data-review-id="${reviewId}"]`;
            console.log('Looking for form with selector:', commentFormSelector);
            
            // Find the comment form for this specific review
            const commentForm = document.querySelector(commentFormSelector);
            
            if (commentForm) {
                console.log('Found comment form, current display:', getComputedStyle(commentForm).display);
                
                // Check if the form is currently visible
                const isVisible = getComputedStyle(commentForm).display !== 'none';
                
                // Toggle form visibility with direct style manipulation for reliability
                if (isVisible) {
                    // Hide the comment form
                    commentForm.style.display = 'none';
                    console.log('Hiding comment form');
                } else {
                    // Show the comment form
                    commentForm.style.display = 'block';
                    console.log('Showing comment form');
                    
                    // Focus on the textarea for better user experience
                    const textarea = commentForm.querySelector('textarea');
                    if (textarea) {
                        console.log('Focusing on textarea');
                        // Use setTimeout to ensure the form is visible before focusing
                        setTimeout(() => textarea.focus(), 0);
                    }
                }
            } else {
                // Form not found - provide debugging information
                console.error(`Comment form for review ${reviewId} not found`);
                
                // Debug: List all available comment forms on the page
                const allForms = document.querySelectorAll('.comment-form-container');
                console.log(`Found ${allForms.length} total comment forms:`, allForms);
                
                // Debug: List all available review IDs
                const reviewIds = [];
                allForms.forEach(form => {
                    reviewIds.push(form.getAttribute('data-review-id'));
                });
                console.log('Available review IDs:', reviewIds);
            }
        }
    });
    
    /**
     * Form submission handler for comment forms
     * Handles AJAX submission with validation and user feedback
     */
    document.addEventListener('submit', async function(event) {
        // Check if the submitted form is a comment form
        if (event.target.classList.contains('comment-form')) {
            // Prevent default form submission to handle with AJAX
            event.preventDefault();
            const form = event.target;
            
            // Extract form data and required elements
            const reviewId = form.getAttribute('data-review-id');
            const textarea = form.querySelector('textarea[name="text"]');
            const parentIdInput = form.querySelector('input[name="parent_id"]');
            const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
            
            // Validate that all required form elements exist
            if (!textarea || !csrfToken) {
                console.error('Missing required form elements');
                return;
            }
            
            // Get and validate comment text
            const commentText = textarea.value.trim();
            if (!commentText) {
                console.log('Empty comment text, skipping submission');
                return;
            }
            
            // Get parent comment ID for nested replies (if applicable)
            const parentId = parentIdInput ? parentIdInput.value || null : null;

            try {
                // Send comment data to server via AJAX
                const response = await fetch('/feed/comments/post/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken  // CSRF protection
                    },
                    body: JSON.stringify({
                        review_id: reviewId,
                        text: commentText,
                        parent_id: parentId
                    })
                });

                // Parse server response
                const data = await response.json();

                if (response.ok) {
                    // Success: Clear the form and show feedback
                    textarea.value = '';
                    
                    // Display success message to user
                    const successMessage = form.parentNode.querySelector('.comment-success');
                    if (successMessage) {
                        successMessage.classList.remove('hidden');
                        
                        // Auto-hide success message after 3 seconds
                        setTimeout(() => {
                            successMessage.classList.add('hidden');
                        }, 3000);
                    }
                    
                    // Refresh page after 1 second to show new comment
                    // TODO: Consider implementing dynamic comment insertion instead
                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    // Server returned an error
                    alert('Error: ' + (data.error || 'Failed to post comment'));
                }
            } catch (error) {
                // Network or parsing error
                console.error('Error posting comment:', error);
                alert('Something went wrong. Please try again.');
            }
        }
    });
    
    // Initialize: Count and log existing elements for debugging
    const commentButtons = document.querySelectorAll('.comment-button');
    console.log(`Found ${commentButtons.length} comment buttons on initial page load`);
    
    const commentForms = document.querySelectorAll('.comment-form-container');
    console.log(`Found ${commentForms.length} comment form containers on initial page load`);
});