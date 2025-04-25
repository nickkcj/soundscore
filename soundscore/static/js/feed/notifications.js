document.addEventListener('DOMContentLoaded', function() {
    const notificationButton = document.getElementById('notification-button');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const notificationCount = document.querySelector('.notification-count');
    const markAllReadButton = document.getElementById('mark-all-read');
    
    let isDropdownOpen = false;
    
    // Toggle dropdown
    notificationButton.addEventListener('click', function() {
      if (isDropdownOpen) {
        closeDropdown();
      } else {
        openDropdown();
        loadNotifications();
        // Immediately hide the notification count when dropdown is opened
        notificationCount.classList.add('hidden');
        // Automatically mark all as read when opening the dropdown
        markAllAsRead();
      }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
      if (isDropdownOpen && !event.target.closest('#notification-bell')) {
        closeDropdown();
      }
    });
    
    // Mark all as read - now a function that can be called programmatically
    markAllReadButton.addEventListener('click', function(event) {
      event.preventDefault();
      markAllAsRead();
    });
    
    function markAllAsRead() {
      fetch('/notifications/mark-all-as-read/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update UI
          document.querySelectorAll('.notification-item').forEach(item => {
            item.classList.remove('bg-pink-50');
            item.classList.add('bg-white');
            const unreadIndicator = item.querySelector('span.bg-pink-500');
            if (unreadIndicator) unreadIndicator.remove();
          });
          
          // Update count
          notificationCount.textContent = '0';
          notificationCount.classList.add('hidden');
        }
      })
      .catch(error => console.error('Error marking all as read:', error));
    }
    
    // Load notification count on page load
    loadNotificationCount();
    
    // Periodically check for new notifications (every 60 seconds)
    setInterval(loadNotificationCount, 60000);
    
    function openDropdown() {
      notificationDropdown.classList.remove('hidden');
      isDropdownOpen = true;
    }
    
    function closeDropdown() {
      notificationDropdown.classList.add('hidden');
      isDropdownOpen = false;
    }
    
    function loadNotifications() {
      // Show loading state
      notificationList.querySelector('.notifications-loading')?.classList.remove('hidden');
      notificationList.querySelector('.no-notifications')?.classList.add('hidden');
      
      // Remove any existing notifications
      document.querySelectorAll('.notification-item').forEach(item => item.remove());
      
      fetch('/notifications/?limit=5')
        .then(response => response.json())
        .then(data => {
          // Hide loading
          notificationList.querySelector('.notifications-loading')?.classList.add('hidden');
          
          if (!data.notifications || data.notifications.length === 0) {
            notificationList.querySelector('.no-notifications')?.classList.remove('hidden');
            return;
          }
          
          // Create notification elements
          data.notifications.forEach(notification => {
            const notificationElement = createNotificationElement(notification);
            notificationList.appendChild(notificationElement);
          });
        })
        .catch(error => {
          console.error('Error loading notifications:', error);
          notificationList.querySelector('.notifications-loading')?.classList.add('hidden');
          notificationList.querySelector('.no-notifications')?.classList.remove('hidden');
        });
    }
    
    function loadNotificationCount() {
      fetch('/notifications/unread-count/')
        .then(response => response.json())
        .then(data => {
          updateNotificationCount(data.unread_count || data.count || 0);
        })
        .catch(error => console.error('Error loading notification count:', error));
    }
    
    function updateNotificationCount(count) {
      if (count > 0) {
        notificationCount.textContent = count > 9 ? '9+' : count;
        notificationCount.classList.remove('hidden');
      } else {
        notificationCount.classList.add('hidden');
      }
    }
    
    function createNotificationElement(notification) {
      const div = document.createElement('div');
      div.className = `notification-item p-3 border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${!notification.is_read ? 'bg-pink-50' : 'bg-white'}`;
      div.dataset.id = notification.id;
      
      // Format the date
      const date = new Date(notification.created_at);
      const timeAgo = formatTimeAgo(date);
      
      // Create the HTML content based on notification type
      let iconHtml = '';
      
      if (notification.notification_type === 'like') {
        iconHtml = `
          <div class="w-8 h-8 rounded-full bg-pink-100 text-pink-500 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
            </svg>
          </div>
        `;
      } else if (notification.notification_type === 'comment') {
        iconHtml = `
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-500 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
            </svg>
          </div>
        `;
      } else {
        iconHtml = `
          <div class="w-8 h-8 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
        `;
      }
      
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
      
      // Navigate when clicked
      div.addEventListener('click', function() {
        // Navigate to the appropriate page based on notification type
        if (notification.review_id) {
          window.location.href = `/review/${notification.review_id}`;
        }
      });
      
      return div;
    }
    
    function formatTimeAgo(date) {
      const now = new Date();
      const diffInSeconds = Math.floor((now - date) / 1000);
      
      if (diffInSeconds < 60) return 'Just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hr ago`;
      if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
      
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
    
    function getCookie(name) {
      let value = '; ' + document.cookie;
      let parts = value.split('; ' + name + '=');
      if (parts.length === 2) return parts.pop().split(';').shift();
    }
  });