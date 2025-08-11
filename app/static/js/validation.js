/**
 * Client-side validation utilities
 */
const Validation = {
    /**
     * Validate entire form
     */
    validateForm: function(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    },
    
    /**
     * Validate individual field
     */
    validateField: function(field) {
        const fieldType = field.type;
        const fieldName = field.name;
        
        switch (fieldType) {
            case 'email':
                return this.validateEmail(field);
            case 'password':
                return this.validatePassword(field);
            case 'text':
                if (fieldName === 'name') {
                    return this.validateName(field);
                }
                return this.validateText(field);
            default:
                return this.validateRequired(field);
        }
    },
    
    /**
     * Validate required field
     */
    validateRequired: function(field) {
        const value = field.value.trim();
        const isValid = value.length > 0;
        
        this.setFieldValidation(field, isValid, 'This field is required');
        return isValid;
    },
    
    /**
     * Validate email format
     */
    validateEmail: function(field) {
        const value = field.value.trim();
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        const isValid = emailRegex.test(value);
        
        this.setFieldValidation(field, isValid, 'Please enter a valid email address');
        return isValid;
    },
    
    /**
     * Validate password strength
     */
    validatePassword: function(field) {
        const value = field.value;
        const errors = [];
        
        if (value.length < 8) {
            errors.push('Password must be at least 8 characters long');
        }
        
        if (!/[A-Z]/.test(value)) {
            errors.push('Password must contain at least one uppercase letter');
        }
        
        if (!/[a-z]/.test(value)) {
            errors.push('Password must contain at least one lowercase letter');
        }
        
        if (!/\d/.test(value)) {
            errors.push('Password must contain at least one number');
        }
        
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(value)) {
            errors.push('Password must contain at least one special character');
        }
        
        const isValid = errors.length === 0;
        this.setFieldValidation(field, isValid, errors.join(', '));
        return isValid;
    },
    
    /**
     * Validate name format
     */
    validateName: function(field) {
        const value = field.value.trim();
        const nameRegex = /^[a-zA-Z\s]+$/;
        let isValid = true;
        let errorMessage = '';
        
        if (value.length < 2) {
            isValid = false;
            errorMessage = 'Name must be at least 2 characters long';
        } else if (value.length > 50) {
            isValid = false;
            errorMessage = 'Name must be no more than 50 characters long';
        } else if (!nameRegex.test(value)) {
            isValid = false;
            errorMessage = 'Name can only contain letters and spaces';
        }
        
        this.setFieldValidation(field, isValid, errorMessage);
        return isValid;
    },
    
    /**
     * Validate text length
     */
    validateText: function(field) {
        const value = field.value.trim();
        const minLength = field.getAttribute('minlength') || 0;
        const maxLength = field.getAttribute('maxlength') || 1000;
        
        let isValid = true;
        let errorMessage = '';
        
        if (value.length < minLength) {
            isValid = false;
            errorMessage = `Text must be at least ${minLength} characters long`;
        } else if (value.length > maxLength) {
            isValid = false;
            errorMessage = `Text must be no more than ${maxLength} characters long`;
        }
        
        this.setFieldValidation(field, isValid, errorMessage);
        return isValid;
    },
    
    /**
     * Validate password confirmation
     */
    validatePasswordMatch: function(passwordField, confirmField) {
        const password = passwordField.value;
        const confirmPassword = confirmField.value;
        const isValid = password === confirmPassword;
        
        this.setFieldValidation(confirmField, isValid, 'Passwords do not match');
        return isValid;
    },
    
    /**
     * Validate rating value
     */
    validateRating: function(field) {
        const value = parseInt(field.value);
        const isValid = !isNaN(value) && value >= 1 && value <= 5;
        
        this.setFieldValidation(field, isValid, 'Rating must be a number between 1 and 5');
        return isValid;
    },
    
    /**
     * Set field validation state
     */
    setFieldValidation: function(field, isValid, errorMessage) {
        const errorElement = document.getElementById(field.id + '-error');
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            if (errorElement) {
                errorElement.textContent = '';
            }
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            if (errorElement) {
                errorElement.textContent = errorMessage;
            }
        }
    },
    
    /**
     * Clear field validation
     */
    clearFieldValidation: function(field) {
        field.classList.remove('is-valid', 'is-invalid');
        const errorElement = document.getElementById(field.id + '-error');
        if (errorElement) {
            errorElement.textContent = '';
        }
    },
    
    /**
     * Clear all form validation
     */
    clearFormValidation: function(form) {
        const fields = form.querySelectorAll('.form-control');
        fields.forEach(field => {
            this.clearFieldValidation(field);
        });
    }
};
