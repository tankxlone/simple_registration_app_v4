/**
 * Main Application JavaScript
 * Handles theme switching, flash messages, and general app functionality
 */

const App = {
    /**
     * Initialize the application
     */
    init: function() {
        this.initTheme();
        this.initFlashMessages();
        this.initAnimations();
        this.initFormEnhancements();
    },

    /**
     * Initialize theme system
     */
    initTheme: function() {
        const themeToggle = document.getElementById('theme-toggle');
        const themeIcon = document.getElementById('theme-icon');
        
        if (!themeToggle || !themeIcon) {
            console.log('Theme toggle elements not found');
            return;
        }

        // Check for saved theme preference or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Theme toggle click handler
        themeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Theme toggle clicked!');
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            console.log('Current theme:', currentTheme);
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            console.log('Switching to theme:', newTheme);
            this.setTheme(newTheme);
        });
    },

    /**
     * Set theme and update UI
     */
    setTheme: function(theme) {
        console.log('Setting theme to:', theme);
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            const newIconClass = theme === 'dark' ? 'bi bi-moon-fill' : 'bi bi-sun-fill';
            console.log('Updating icon to:', newIconClass);
            themeIcon.className = newIconClass;
        } else {
            console.log('Theme icon not found!');
        }

        // Add smooth transition class
        document.body.classList.add('theme-transitioning');
        setTimeout(() => {
            document.body.classList.remove('theme-transitioning');
        }, 300);

        console.log('Theme set successfully to:', theme);
    },

    /**
     * Initialize flash message system
     */
    initFlashMessages: function() {
        // Auto-hide flash messages after 5 seconds
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(message => {
            setTimeout(() => {
                this.fadeOut(message);
            }, 5000);
        });

        // Add close button functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('alert-close')) {
                this.fadeOut(e.target.closest('.alert'));
            }
        });
    },

    /**
     * Initialize smooth animations
     */
    initAnimations: function() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe elements with animation classes
        document.querySelectorAll('.card, .btn, .form-group').forEach(el => {
            observer.observe(el);
        });
    },

    /**
     * Initialize form enhancements
     */
    initFormEnhancements: function() {
        // Add floating label effect
        document.querySelectorAll('.form-control').forEach(input => {
            const label = input.previousElementSibling;
            if (label && label.classList.contains('form-label')) {
                this.initFloatingLabel(input, label);
            }
        });

        // Add form validation feedback
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                this.validateForm(form, e);
            });
        });
    },

    /**
     * Initialize floating label effect
     */
    initFloatingLabel: function(input, label) {
        const checkValue = () => {
            if (input.value) {
                label.classList.add('floating');
            } else {
                label.classList.remove('floating');
            }
        };

        input.addEventListener('focus', checkValue);
        input.addEventListener('blur', checkValue);
        input.addEventListener('input', checkValue);
        
        // Check initial value
        checkValue();
    },

    /**
     * Validate form before submission
     */
    validateForm: function(form, event) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.showFlashMessage('Please fill in all required fields', 'warning');
        }
    },

    /**
     * Show field-specific error
     */
    showFieldError: function(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.color = 'var(--accent-danger)';
        errorDiv.style.fontSize = '0.75rem';
        errorDiv.style.marginTop = '0.25rem';
        
        field.parentNode.appendChild(errorDiv);
        field.style.borderColor = 'var(--accent-danger)';
    },

    /**
     * Clear field-specific error
     */
    clearFieldError: function(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        field.style.borderColor = '';
    },

    /**
     * Show flash message
     */
    showFlashMessage: function(message, type = 'info') {
        const flashContainer = document.getElementById('flash-messages');
        if (!flashContainer) return;

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} fade-in`;
        alertDiv.innerHTML = `
            <i class="bi bi-${this.getAlertIcon(type)}"></i>
            <span>${message}</span>
            <button type="button" class="alert-close ms-auto" aria-label="Close">
                <i class="bi bi-x"></i>
            </button>
        `;

        flashContainer.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.fadeOut(alertDiv);
        }, 5000);
    },

    /**
     * Get appropriate icon for alert type
     */
    getAlertIcon: function(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Fade out element
     */
    fadeOut: function(element) {
        element.style.transition = 'opacity 0.3s ease-out';
        element.style.opacity = '0';
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 300);
    },

    /**
     * Smooth scroll to element
     */
    scrollTo: function(elementId, offset = 0) {
        const element = document.getElementById(elementId);
        if (element) {
            const elementPosition = element.offsetTop - offset;
            window.scrollTo({
                top: elementPosition,
                behavior: 'smooth'
            });
        }
    },

    /**
     * Debounce function for performance
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function for performance
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Show loading indicator
     */
    showLoading: function() {
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.getElementById('loading-overlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div class="mt-2 text-muted">Loading...</div>
                </div>
            `;
            document.body.appendChild(loadingOverlay);
        }
        loadingOverlay.style.display = 'flex';
    },

    /**
     * Hide loading indicator
     */
    hideLoading: function() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    App.init();
});

// Export for use in other modules
window.App = App;
