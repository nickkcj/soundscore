document.addEventListener('DOMContentLoaded', function() {
  const sortToggle = document.getElementById('sort-toggle');
  if (!sortToggle) return;

  // Initialize from localStorage or default to "desc" (newest first)
  const savedOrder = localStorage.getItem('reviewSortOrder') || 'desc';
  updateSortUI(savedOrder);
  
  // Add click handler
  sortToggle.addEventListener('click', function() {
    const currentOrder = sortToggle.getAttribute('data-sort-order');
    const newOrder = currentOrder === 'desc' ? 'asc' : 'desc';
    
    updateSortUI(newOrder);
    localStorage.setItem('reviewSortOrder', newOrder);
    
    // Reset and reload feed
    const reviewsContainer = document.querySelector('.space-y-20');
    const loadMoreBtn = document.getElementById('load-more-btn');
    
    if (reviewsContainer) reviewsContainer.innerHTML = '';
    if (loadMoreBtn) {
      loadMoreBtn.setAttribute('data-page', '0');
      loadMoreBtn.setAttribute('data-has-more', 'true');
      loadMoreBtn.disabled = false;
      loadMoreBtn.textContent = 'Load more';
      
      // Clear the global Set instead of reassigning
      window.loadedReviewIds.clear();
      
      loadMoreBtn.click(); // Reload with new sort
    }
  });
  
  // Helper function to update UI
  function updateSortUI(order) {
    const label = document.getElementById('sort-label');
    const icon = document.getElementById('sort-icon');
    
    sortToggle.setAttribute('data-sort-order', order);
    if (label) label.textContent = order === 'desc' ? 'Latest first' : 'Latest last';
    if (icon) icon.style.transform = order === 'asc' ? 'rotate(180deg)' : '';
  }
});