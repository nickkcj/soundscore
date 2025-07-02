console.log("Follow user script loaded");

document.addEventListener('DOMContentLoaded', function() {
    const followBtn = document.getElementById('follow-btn');
    
    if (followBtn) {
        // Set initial button state
        updateButtonState(followBtn);
        
        followBtn.addEventListener('click', async function() {
            const username = this.getAttribute('data-username');
            const isFollowing = this.getAttribute('data-following') === 'true';
            
            // Disable button during request
            this.disabled = true;
            this.classList.add('opacity-50');
            
            try {
                const endpoint = isFollowing ? 'unfollow' : 'follow';
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                                 document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
                
                if (!csrfToken) {
                    console.error('CSRF token not found');
                    return;
                }
                
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
                        updateButtonState(this);
                        
                        // Show success message (optional)
                        showNotification(data.message, 'success');
                    } else {
                        showNotification(data.message, 'error');
                    }
                } else {
                    showNotification('Something went wrong. Please try again.', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Network error. Please try again.', 'error');
            } finally {
                // Re-enable button
                this.disabled = false;
                this.classList.remove('opacity-50');
            }
        });
    }
    
    function updateButtonState(button) {
        const isFollowing = button.getAttribute('data-following') === 'true';
        const followText = button.querySelector('.follow-text');
        const followIcon = button.querySelector('.follow-icon path');
        
        if (isFollowing) {
            // Unfollow state - User with checkmark
            button.className = 'w-full inline-flex items-center justify-center px-5 py-2.5 bg-gray-500 text-white rounded-lg text-sm font-medium shadow-sm transition-all duration-200 hover:bg-gray-600 follow-button';
            followText.textContent = 'Following';
            followIcon.setAttribute('d', 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z M22 4L12 14l-5-5'); // User with check
        } else {
            // Follow state - User with plus
            button.className = 'w-full inline-flex items-center justify-center px-5 py-2.5 bg-pink-500 text-white rounded-lg text-sm font-medium shadow-sm transition-all duration-200 hover:bg-pink-600 follow-button';
            followText.textContent = 'Follow';
            followIcon.setAttribute('d', 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z M19 8v6m3-3h-6'); // User with plus
        }
    }
    
    function showNotification(message, type) {
        // Remove any existing notifications first
        const existingNotification = document.querySelector('.follow-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'follow-notification fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-full shadow-lg text-white text-sm font-medium transition-all duration-500 ease-out opacity-0 translate-y-4';
        
        // Set colors and icons based on type
        if (type === 'success') {
            if (message.includes('following')) {
                // Following message
                notification.className += ' bg-gradient-to-r from-pink-500 to-pink-600';
                notification.innerHTML = `
                    <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                        </svg>
                        <span>${message}</span>
                    </div>
                `;
            } else {
                // Unfollowing message
                notification.className += ' bg-gradient-to-r from-gray-500 to-gray-600';
                notification.innerHTML = `
                    <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                        </svg>
                        <span>${message}</span>
                    </div>
                `;
            }
        } else {
            // Error message
            notification.className += ' bg-gradient-to-r from-red-500 to-red-600';
            notification.innerHTML = `
                <div class="flex items-center space-x-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                    <span>${message}</span>
                </div>
            `;
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.remove('opacity-0', 'translate-y-4');
            notification.classList.add('opacity-100', 'translate-y-0');
        });
        
        // Remove after 3 seconds with animation
        setTimeout(() => {
            notification.classList.remove('opacity-100', 'translate-y-0');
            notification.classList.add('opacity-0', 'translate-y-4');
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 500);
        }, 3000);
    }
});