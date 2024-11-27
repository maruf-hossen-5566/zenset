document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarContent = document.getElementById('sidebar-content');
    const main = document.querySelector('main');
    
    // Initial position calculations
    let lastScrollTop = 0;
    let ticking = false;
    
    // Function to update sidebar position
    function updateSidebar() {
        const mainRect = main.getBoundingClientRect();
        const sidebarRect = sidebarContent.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Reset styles first
        sidebarContent.style.position = '';
        sidebarContent.style.top = '';
        sidebarContent.style.bottom = '';
        
        // If sidebar is shorter than viewport, just make it sticky
        if (sidebarRect.height <= windowHeight) {
            sidebarContent.style.position = 'sticky';
            sidebarContent.style.top = '20px'; // Add some top margin
            return;
        }
        
        // If sidebar is taller than viewport, handle scroll direction
        const scrollDirection = scrollTop > lastScrollTop ? 'down' : 'up';
        lastScrollTop = scrollTop;
        
        if (scrollDirection === 'down') {
            // Scrolling down: Show bottom of sidebar
            if (mainRect.bottom > windowHeight) {
                sidebarContent.style.position = 'sticky';
                sidebarContent.style.top = `-${sidebarRect.height - windowHeight + 20}px`;
            }
        } else {
            // Scrolling up: Show top of sidebar
            if (mainRect.top < 0) {
                sidebarContent.style.position = 'sticky';
                sidebarContent.style.top = '20px';
            }
        }
    }
    
    // Throttled scroll handler
    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateSidebar();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    // Add scroll event listener
    window.addEventListener('scroll', onScroll, { passive: true });
    
    // Update on resize
    window.addEventListener('resize', () => {
        updateSidebar();
    }, { passive: true });
    
    // Initial update
    updateSidebar();
});