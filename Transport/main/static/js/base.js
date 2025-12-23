// Navbar slide-down + Dropdown menu functionality

document.addEventListener("DOMContentLoaded", function() {
    // Navbar slide-down
    var navbar = document.querySelector('.navbar');
    if (navbar) {
        setTimeout(function() {
            navbar.classList.add('navbar-visible');
        }, 10);
    }

    // Page fade-in animation
   window.addEventListener('load', () => {
    document.body.classList.add('page-loaded');
   });


    // Dropdown menu functionality
    function setupDropdown(dropdownId, toggleId) {
        var dropdown = document.getElementById(dropdownId);
        var toggle = document.getElementById(toggleId);
        var menu = dropdown ? dropdown.querySelector('.dropdown-menu') : null;
        if (dropdown && toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                dropdown.classList.toggle('show-dropdown');
            });
            menu.addEventListener('click', function(e) {
                e.stopPropagation();
            });
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    dropdown.classList.remove('show-dropdown');
                }
            });
        }
    }
    setupDropdown('profile-dropdown', 'profile-dropdown-toggle');
    setupDropdown('login-dropdown', 'login-dropdown-toggle');

    // Hamburger menu toggle for responsive navbar
    var navToggle = document.getElementById('navbar-toggle');
    var navList = document.getElementById('nav-list');
    if (navToggle && navList) {
        navToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navList.classList.toggle('open');
        });
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navList.contains(e.target) && !navToggle.contains(e.target)) {
                navList.classList.remove('open');
            }
        });
    }
});



