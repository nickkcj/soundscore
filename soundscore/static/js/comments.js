document.addEventListener('DOMContentLoaded', function() {
    // Handle comment button clicks to toggle the comment form
    const commentButtons = document.querySelectorAll('.comment-button');
    commentButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const commentForm = document.querySelector(`.comment-form-container[data-review-id="${reviewId}"]`);
            
            // Toggle visibility of the comment form
            commentForm.classList.toggle('hidden');
            
            // Focus on the textarea when showing the form
            if (!commentForm.classList.contains('hidden')) {
                commentForm.querySelector('textarea').focus();
            }
        });
    });
    
    // Handle comment form submissions
    const commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            const reviewId = form.getAttribute('data-review-id');
            const textarea = form.querySelector('textarea[name="text"]');
            const parentId = form.querySelector('input[name="parent_id"]').value || null;
            const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;

            const commentText = textarea.value.trim();
            if (!commentText) return;

            try {
                const response = await fetch('/comments/post/', {
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
                    textarea.value = '';
                    const successMessage = form.parentNode.querySelector('.comment-success');
                    successMessage.classList.remove('hidden');
                    
                    // Refresh the page after successful comment (or implement dynamic comment addition)
                    setTimeout(() => {
                        location.reload();
                        // Alternatively, add the new comment dynamically to the UI without reloading
                    }, 1000);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error posting comment:', error);
                alert('Something went wrong. Please try again.');
            }
        });
    });
});