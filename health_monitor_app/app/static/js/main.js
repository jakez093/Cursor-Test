/**
 * Health Monitor App - Main JavaScript
 * Enhances UI and visualization elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 1rem 1.5rem rgba(18, 38, 63, .175)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 .25rem .5rem rgba(18, 38, 63, .15)';
        });
    });
    
    // Activate tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Highlight rows in tables when hovered
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(44, 123, 229, 0.05)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
    
    // Enhance form fields focus effects
    const formFields = document.querySelectorAll('.form-control, .form-select');
    formFields.forEach(field => {
        field.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        field.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
    
    // Add smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && document.querySelector(targetId)) {
                e.preventDefault();
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add animation to graph images when they load
    const graphImages = document.querySelectorAll('.graph-container img');
    graphImages.forEach(img => {
        img.addEventListener('load', function() {
            this.classList.add('fade-in');
        });
    });
    
    // Enhance parameter pills navigation
    const parameterPills = document.querySelectorAll('.parameter-pill');
    parameterPills.forEach(pill => {
        pill.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        pill.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Keep current time period when switching parameters
        pill.addEventListener('click', function(e) {
            // This is now handled by template URL generation
        });
    });
    
    // Add active class to current nav item based on URL
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentPath.includes(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });
    
    // Add visual feedback for time period buttons
    const timeButtons = document.querySelectorAll('.btn-group .btn');
    timeButtons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 0.25rem 0.5rem rgba(44, 123, 229, 0.15)';
            }
        });
        
        btn.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = '';
                this.style.boxShadow = '';
            }
        });
    });
    
    // Enhanced navigation arrows for graph views
    const navArrows = document.querySelectorAll('.nav-arrow');
    if (navArrows.length) {
        // Add hover and pulse effect
        navArrows.forEach(arrow => {
            // Pulse effect on page load
            arrow.classList.add('pulse-animation');
            setTimeout(() => {
                arrow.classList.remove('pulse-animation');
            }, 2000);
            
            // Add click transition effect
            arrow.addEventListener('click', function(e) {
                const graphContainer = document.querySelector('.graph-container');
                if (graphContainer) {
                    // Apply fade-out transition
                    graphContainer.style.opacity = '0.5';
                    graphContainer.style.transition = 'opacity 0.3s ease';
                }
                
                // Show loading indicator
                const graphCard = document.querySelector('.graph-card');
                if (graphCard) {
                    const loadingIndicator = document.createElement('div');
                    loadingIndicator.className = 'position-absolute top-50 start-50 translate-middle';
                    loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
                    loadingIndicator.style.zIndex = '20';
                    graphCard.appendChild(loadingIndicator);
                    
                    // Remove the loading indicator after navigation timeout
                    setTimeout(() => {
                        if (document.contains(loadingIndicator)) {
                            loadingIndicator.remove();
                        }
                    }, 3000);
                }
            });
        });
        
        // Add keyboard navigation support (moved to graph.html page for direct access)
    }
    
    // Responsive behavior for tables
    function handleResponsiveTables() {
        const tables = document.querySelectorAll('.table');
        const windowWidth = window.innerWidth;
        
        tables.forEach(table => {
            if (windowWidth < 768) {
                table.classList.add('table-responsive');
            } else {
                table.classList.remove('table-responsive');
            }
        });
    }
    
    // Initialize responsive tables
    handleResponsiveTables();
    
    // Update on window resize
    window.addEventListener('resize', handleResponsiveTables);
    
    // Add loading indicator for form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                
                // Reset after timeout in case of network issues
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 5000);
            }
        });
    });
    
    // Add back-to-top button functionality
    if (document.getElementById('back-to-top')) {
        window.onscroll = function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                document.getElementById('back-to-top').style.display = 'block';
            } else {
                document.getElementById('back-to-top').style.display = 'none';
            }
        };
        
        document.getElementById('back-to-top').addEventListener('click', function() {
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        });
    }
    
    // Add CSS animations for graph navigation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .pulse-animation {
            animation: pulse 1s infinite;
        }
        
        .graph-container {
            transition: opacity 0.3s ease;
        }
        
        .graph-container img {
            transition: opacity 0.5s ease;
        }
    `;
    document.head.appendChild(style);
}); 