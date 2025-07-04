/**
 * Handles modal toggling for group creation UI.
 * Allows opening and closing modals for creating a group.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Find all elements that toggle modals
    const modalToggles = document.querySelectorAll('[data-modal-toggle]');
    modalToggles.forEach(toggle => {
      toggle.addEventListener('click', function() {
        // Get the target modal by ID and toggle its visibility
        const targetId = this.getAttribute('data-modal-target');
        const modal = document.getElementById(targetId);
        if (modal) {
          modal.classList.toggle('hidden');
        }
      });
    });
    
    // Find all elements that hide modals
    const modalHides = document.querySelectorAll('[data-modal-hide]');
    modalHides.forEach(hide => {
      hide.addEventListener('click', function() {
        // Get the target modal by ID and hide it
        const targetId = this.getAttribute('data-modal-hide');
        const modal = document.getElementById(targetId);
        if (modal) {
          modal.classList.add('hidden');
        }
      });
    });
});