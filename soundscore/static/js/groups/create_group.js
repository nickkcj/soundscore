document.addEventListener('DOMContentLoaded', function() {
    const modalToggles = document.querySelectorAll('[data-modal-toggle]');
    modalToggles.forEach(toggle => {
      toggle.addEventListener('click', function() {
        const targetId = this.getAttribute('data-modal-target');
        const modal = document.getElementById(targetId);
        if (modal) {
          modal.classList.toggle('hidden');
        }
      });
    });
    
    const modalHides = document.querySelectorAll('[data-modal-hide]');
    modalHides.forEach(hide => {
      hide.addEventListener('click', function() {
        const targetId = this.getAttribute('data-modal-hide');
        const modal = document.getElementById(targetId);
        if (modal) {
          modal.classList.add('hidden');
        }
      });
    });
  });