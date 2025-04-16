// Main JavaScript file for Tenant Verification System

// Execute when document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize feather icons if available
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Global form validation helpers
    const forms = document.querySelectorAll('.needs-validation');
    if (forms.length > 0) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }
    
    // Age calculator function - can be used throughout the application
    window.calculateAge = function(dobField, ageField) {
        const dob = new Date(dobField.value);
        if (!isNaN(dob.getTime())) {
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const monthDiff = today.getMonth() - dob.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }
            
            if (ageField) {
                ageField.value = age;
            }
            
            return age;
        }
        return null;
    };
    
    // Date of birth input handler
    const dobInputs = document.querySelectorAll('input[type="date"][id*="date_of_birth"]');
    dobInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Find the corresponding age field
            const fieldId = this.id;
            const ageFieldId = fieldId.replace('date_of_birth', 'age');
            const ageField = document.getElementById(ageFieldId);
            
            if (ageField) {
                calculateAge(this, ageField);
            }
        });
    });
    
    // OTP Timer functionality
    let otpTimer;
    window.startOtpTimer = function(durationInSeconds, displayElement) {
        clearInterval(otpTimer);
        let timeLeft = durationInSeconds;
        
        const updateTimer = () => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            displayElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            
            if (--timeLeft < 0) {
                clearInterval(otpTimer);
                displayElement.textContent = 'OTP Expired';
                if (displayElement.dataset.expiryCallback) {
                    window[displayElement.dataset.expiryCallback]();
                }
            }
        };
        
        updateTimer();
        otpTimer = setInterval(updateTimer, 1000);
    };
    
    // Show alert messages
    window.showAlert = function(message, type = 'success', container = '.alert-container', timeout = 5000) {
        const alertContainer = document.querySelector(container);
        if (!alertContainer) return;
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.appendChild(alertDiv);
        
        if (timeout > 0) {
            setTimeout(() => {
                try {
                    const bsAlert = bootstrap.Alert.getOrCreateInstance(alertDiv);
                    bsAlert.close();
                } catch (e) {
                    alertDiv.remove();
                }
            }, timeout);
        }
    };
    
    // Format phone numbers
    const phoneInputs = document.querySelectorAll('input[type="text"][pattern*="[0-9]"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Remove any non-digit character
            this.value = this.value.replace(/\D/g, '');
            
            // Enforce maxlength specified in pattern
            const patternMatch = this.pattern.match(/\d+/g);
            if (patternMatch && patternMatch.length > 0) {
                const maxLength = parseInt(patternMatch[0], 10);
                if (this.value.length > maxLength) {
                    this.value = this.value.slice(0, maxLength);
                }
            }
        });
    });
    
    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const inputId = this.dataset.target;
            const input = document.getElementById(inputId);
            
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.innerHTML = '<i data-feather="eye-off"></i>';
                } else {
                    input.type = 'password';
                    this.innerHTML = '<i data-feather="eye"></i>';
                }
                
                // Re-initialize feather icons
                if (typeof feather !== 'undefined') {
                    feather.replace();
                }
            }
        });
    });
    
    // Prevent form resubmission on page refresh
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
    
    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize any dropdowns
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    if (typeof bootstrap !== 'undefined') {
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
    }
    
    // Handle conditional form elements
    function handleConditionalFormElements() {
        // Profession dropdown
        const professionDropdown = document.getElementById('profession');
        if (professionDropdown) {
            const otherProfessionDiv = document.getElementById('otherProfessionDiv');
            const otherProfessionInput = document.getElementById('other_profession');
            
            professionDropdown.addEventListener('change', function() {
                if (this.value === 'Others') {
                    otherProfessionDiv.style.display = 'block';
                    otherProfessionInput.setAttribute('required', 'true');
                } else {
                    otherProfessionDiv.style.display = 'none';
                    otherProfessionInput.removeAttribute('required');
                }
            });
        }
        
        // Serving Employee Radio Buttons
        const servingRadios = document.querySelectorAll('input[name="serving_employee"]');
        if (servingRadios.length > 0) {
            const servingCertificateDiv = document.getElementById('servingCertificateDiv');
            const servingCertificateInput = document.getElementById('serving_certificate');
            
            servingRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'Yes' && this.checked) {
                        servingCertificateDiv.style.display = 'block';
                        servingCertificateInput.setAttribute('required', 'true');
                    } else {
                        servingCertificateDiv.style.display = 'none';
                        servingCertificateInput.removeAttribute('required');
                    }
                });
            });
        }
        
        // Retired Employee Radio Buttons
        const retiredRadios = document.querySelectorAll('input[name="retired_employee"]');
        if (retiredRadios.length > 0) {
            const retiredCertificateDiv = document.getElementById('retiredCertificateDiv');
            const retiredCertificateInput = document.getElementById('retired_certificate');
            
            retiredRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'Yes' && this.checked) {
                        retiredCertificateDiv.style.display = 'block';
                        retiredCertificateInput.setAttribute('required', 'true');
                    } else {
                        retiredCertificateDiv.style.display = 'none';
                        retiredCertificateInput.removeAttribute('required');
                    }
                });
            });
        }
        
        // Sikkim Certificate Radio Buttons
        const sikkimRadios = document.querySelectorAll('input[name="sikkim_certificate"]');
        if (sikkimRadios.length > 0) {
            const sikkimCertificateDiv = document.getElementById('sikkimCertificateDiv');
            const sikkimCertificateInput = document.getElementById('sikkim_certificate_file');
            
            sikkimRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    if (this.value === 'Yes' && this.checked) {
                        sikkimCertificateDiv.style.display = 'block';
                        sikkimCertificateInput.setAttribute('required', 'true');
                    } else {
                        sikkimCertificateDiv.style.display = 'none';
                        sikkimCertificateInput.removeAttribute('required');
                    }
                });
            });
        }
    }
    
    // Call the function to handle conditional form elements
    handleConditionalFormElements();
});

// AJAX Request Helper
function ajaxRequest(url, method = 'GET', data = null, successCallback = null, errorCallback = null) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    
    if (method.toUpperCase() === 'POST' && !(data instanceof FormData)) {
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    }
    
    // Include CSRF token for POST requests if it exists
    if (method.toUpperCase() === 'POST') {
        const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfTokenMeta) {
            xhr.setRequestHeader('X-CSRFToken', csrfTokenMeta.content);
        }
    }
    
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            let response;
            try {
                response = JSON.parse(xhr.responseText);
            } catch (e) {
                response = xhr.responseText;
            }
            
            if (successCallback) {
                successCallback(response);
            }
        } else {
            let error;
            try {
                error = JSON.parse(xhr.responseText);
            } catch (e) {
                error = {
                    status: xhr.status,
                    message: xhr.statusText || 'Unknown error occurred'
                };
            }
            
            if (errorCallback) {
                errorCallback(error);
            } else {
                console.error('AJAX Error:', error);
            }
        }
    };
    
    xhr.onerror = function() {
        if (errorCallback) {
            errorCallback({
                status: 0,
                message: 'Network error occurred'
            });
        } else {
            console.error('Network Error');
        }
    };
    
    xhr.send(data);
}

// Utility Functions
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatPhone(phone) {
    if (!phone) return '';
    
    // Format as XXX-XXX-XXXX if 10 digits
    if (/^\d{10}$/.test(phone)) {
        return `${phone.slice(0, 3)}-${phone.slice(3, 6)}-${phone.slice(6)}`;
    }
    
    return phone;
}

function getFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

function serializeForm(form) {
    const formData = new FormData(form);
    const serialized = [];
    
    for (const [key, value] of formData.entries()) {
        serialized.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
    }
    
    return serialized.join('&');
}

// Export utility functions for global use
window.utils = {
    ajaxRequest,
    formatDate,
    formatPhone,
    getFormData,
    serializeForm
};
