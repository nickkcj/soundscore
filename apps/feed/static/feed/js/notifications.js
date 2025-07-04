/**
 * Notification System JavaScript
 * Handles notification dropdown, real-time updates, and user interactions
 * Manages notification badge counts and mark-as-read functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get notification system DOM elements
    const notificationButton = document.getElementById('notification-button');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const notificationCount = document.querySelector('.notification-count');
    const markAllReadButton = document.getElementById('mark-all-read');
    
    // Track dropdown state to manage interactions
    let isDropdownOpen = false;
    
    /**
     * Toggle notification dropdown visibility
     * Loads notifications when opened and manages read status
     */
    notificationButton.addEventListener('click', function() {
        if (isDropdownOpen) {
            closeDropdown();
        } else {
            openDropdown();
            loadNotifications();
            
            // Hide notification badge immediately when user opens dropdown
            notificationCount.classList.add('hidden');
            
            // Auto-mark all notifications as read when dropdown is opened
            // This improves UX by clearing the badge when user views notifications
            markAllAsRead();
        }
    });
    
    /**
     * Close dropdown when clicking outside the notification area
     * Improves UX by allowing users to dismiss notifications naturally
     */
    document.addEventListener('click', function(event) {
        if (isDropdownOpen && !event.target.closest('#notification-bell')) {
            closeDropdown();
        }
    });
    
    /**
     * Manual "Mark all as read" button handler
     * Allows users to explicitly clear all notifications
     */
    markAllReadButton.addEventListener('click', function(event) {
        event.preventDefault();
        markAllAsRead();
    });
    
    /**
     * Mark all notifications as read via API call
     * Updates both server state and UI immediately
     */
    function markAllAsRead() {
        fetch('/feed/notifications/mark-all-as-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // CSRF protection
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI to reflect read status
                document.querySelectorAll('.notification-item').forEach(item => {
                    // Remove unread highlighting
                    item.classList.remove('bg-pink-50');
                    item.classList.add('bg-white');
                    
                    // Remove unread indicator dots
                    const unreadIndicator = item.querySelector('span.bg-pink-500');
                    if (unreadIndicator) unreadIndicator.remove();
                });
                
                // Clear notification badge
                notificationCount.textContent = '0';
                notificationCount.classList.add('hidden');
            }
        })
        .catch(error => console.error('Error marking all as read:', error));
    }
    
    // Load notification count when page first loads
    loadNotificationCount();
    
    // Set up periodic refresh to check for new notifications every minute
    setInterval(loadNotificationCount, 60000);
    
    /**
     * Show the notification dropdown
     */
    function openDropdown() {
        notificationDropdown.classList.remove('hidden');
        isDropdownOpen = true;
    }
    
    /**
     * Hide the notification dropdown
     */
    function closeDropdown() {
        notificationDropdown.classList.add('hidden');
        isDropdownOpen = false;
    }
    
    /**
     * Load and display recent notifications from server
     * Fetches latest 5 notifications and updates the dropdown content
     */
    function loadNotifications() {
        // Show loading state while fetching data
        notificationList.querySelector('.notifications-loading')?.classList.remove('hidden');
        notificationList.querySelector('.no-notifications')?.classList.add('hidden');
        
        // Clear existing notification items to prevent duplicates
        document.querySelectorAll('.notification-item').forEach(item => item.remove());
        
        // Fetch notifications from server
        fetch('/feed/notifications/?limit=5')
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                notificationList.querySelector('.notifications-loading')?.classList.add('hidden');
                
                // Check if we have notifications to display
                if (!data.notifications || data.notifications.length === 0) {
                    // Show "no notifications" message
                    notificationList.querySelector('.no-notifications')?.classList.remove('hidden');
                    return;
                }
                
                // Create and append notification elements
                data.notifications.forEach(notification => {
                    const notificationElement = createNotificationElement(notification);
                    notificationList.appendChild(notificationElement);
                });
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                // Hide loading and show empty state on error
                notificationList.querySelector('.notifications-loading')?.classList.add('hidden');
                notificationList.querySelector('.no-notifications')?.classList.remove('hidden');
            });
    }
    
    /**
     * Load unread notification count for the badge
     * Updates the notification badge number in the header
     */
    function loadNotificationCount() {
        fetch('/feed/notifications/unread-count/')
            .then(response => response.json())
            .then(data => {
                // Handle different response formats from server
                updateNotificationCount(data.unread_count || data.count || 0);
            })
            .catch(error => console.error('Error loading notification count:', error));
    }
    
    /**
     * Update the notification badge display
     * @param {number} count - Number of unread notifications
     */
    function updateNotificationCount(count) {
        if (count > 0) {
            // Show badge with count (max 9+)
            notificationCount.textContent = count > 9 ? '9+' : count;
            notificationCount.classList.remove('hidden');
        } else {
            // Hide badge when no unread notifications
            notificationCount.classList.add('hidden');
        }
    }
    
    /**
     * Create a notification DOM element with proper styling and interactions
     * @param {Object} notification - Notification data from server
     * @returns {HTMLElement} - Styled notification element
     */
    function createNotificationElement(notification) {
        const div = document.createElement('div');
        
        // Apply styling based on read status
        div.className = `notification-item p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${!notification.is_read ? 'bg-pink-50' : 'bg-white'}`;
        div.dataset.id = notification.id;
        
        // Format timestamp for display
        const date = new Date(notification.created_at);
        const timeAgo = formatTimeAgo(date);
        
        // Generate appropriate icon based on notification type
        let iconHtml = '';
        
        if (notification.notification_type === 'like') {
            // Heart icon for likes
            iconHtml = `
                <div class="w-8 h-8 rounded-full bg-pink-100 text-pink-500 flex items-center justify-center flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                    </svg>
                </div>
            `;
        } else if (notification.notification_type === 'comment') {
            // Comment bubble icon for comments
            iconHtml = `
                <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-500 flex items-center justify-center flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                    </svg>
                </div>
            `;
        } else {
            // Generic info icon for other notification types
            iconHtml = `
                <div class="w-8 h-8 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                    </svg>
                </div>
            `;
        }
        
        // Build the notification HTML structure
        div.innerHTML = `
            <div class="flex items-start space-x-3">
                ${iconHtml}
                <div class="flex-1 min-w-0">
                    <p class="text-sm text-gray-800">${notification.message}</p>
                    <p class="text-xs text-gray-500 mt-1">${timeAgo}</p>
                </div>
                ${!notification.is_read ? '<span class="w-2 h-2 bg-pink-500 rounded-full"></span>' : ''}
            </div>
        `;
        
        // Add click handler for navigation
        div.addEventListener('click', function() {
            // Navigate to the related content when notification is clicked
            if (notification.review_id) {
                window.location.href = `/review/${notification.review_id}`;
            }
        });
        
        return div;
    }
    
    /**
     * Format a date into a human-readable "time ago" string
     * @param {Date} date - Date to format
     * @returns {string} - Formatted time string
     */
    function formatTimeAgo(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        // Return appropriate time format based on elapsed time
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hr ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        
        // For older notifications, show actual date
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
    
    /**
     * Get CSRF token from cookies for secure API requests
     * @param {string} name - Cookie name
     * @returns {string} - Cookie value
     */
    function getCookie(name) {
        let value = '; ' + document.cookie;
        let parts = value.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});