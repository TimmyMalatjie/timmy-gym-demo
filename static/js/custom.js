// static/js/custom.js
// Timmy's Gym - Custom JavaScript (Game Logic)

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Timmy\'s Gym System Loaded!');
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading animation for buttons
    document.querySelectorAll('.cta-button').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!this.classList.contains('disabled')) {
                this.innerHTML += ' <span class="spinner-border spinner-border-sm ms-2"></span>';
                this.classList.add('disabled');
                
                // Remove spinner after 2 seconds (for demo purposes)
                setTimeout(() => {
                    this.innerHTML = this.innerHTML.replace(/ <span class="spinner-border.*<\/span>/, '');
                    this.classList.remove('disabled');
                }, 2000);
            }
        });
    });
});

// Utility functions for future features
const TimmyGym = {
    // Show notification messages
    showNotification: function(message, type = 'success') {
        console.log(`${type.toUpperCase()}: ${message}`);
        // We'll enhance this later with actual UI notifications
    },
    
    // Format currency for South African Rand
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-ZA', {
            style: 'currency',
            currency: 'ZAR'
        }).format(amount);
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Find logout links
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Optional: Add confirmation dialog
            // Uncomment the next 3 lines if you want logout confirmation
            // if (!confirm('Are you sure you want to logout?')) {
            //     e.preventDefault();
            // }
        });
    });
    
    // Show logout success message animation
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto-hide success messages after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }, 5000);
        }
    });
});