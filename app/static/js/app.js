// Interactive features for MediShare Platform

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-hide alerts
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Add loading state
            const submitBtn = form.querySelector('button[type=\"submit\"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class=\"spinner-border spinner-border-sm me-2\"></span>Saving...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Sidebar mobile toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function closeSidebar() {
        sidebar && sidebar.classList.remove('show');
        overlay && overlay.classList.remove('show');
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            const isOpen = sidebar.classList.toggle('show');
            overlay && overlay.classList.toggle('show', isOpen);
        });
    }

    // Close sidebar when overlay is tapped
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Close sidebar when a nav link is tapped on mobile
    if (sidebar) {
        sidebar.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 768) closeSidebar();
            });
        });
    }
    
    // Stats counters animation
    const animateCounters = () => {
        const counters = document.querySelectorAll('.stat-counter');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const increment = target / 100;
            let current = 0;
            
            const updateCounter = () => {
                if (current < target) {
                    current += increment;
                    counter.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };
            updateCounter();
        });
    };
    
    // Observe stats section for animation trigger
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                statsObserver.unobserve(entry.target);
            }
        });
    });
    
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
    
    // Search functionality (generic)
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const table = document.querySelector(input.dataset.target);
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const query = input.value.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });
    
    // Confirm delete/modals
    document.querySelectorAll('.confirm-delete').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure? This action cannot be undone.')) {
                window.location.href = this.href;
            }
        });
    });
    
    // Table responsive enhancement
    const tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(table => {
        table.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });
        table.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});

