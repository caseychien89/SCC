document.addEventListener('DOMContentLoaded', () => {
    const tabContainer = document.querySelector('.tab-container');
    if (!tabContainer) {
        // console.warn('Tab container (.tab-container) not found.');
        return;
    }
    const tabs = tabContainer.querySelectorAll('.tab-item');

    if (!tabs.length) {
        // console.warn('No tab items (.tab-item) found.');
        return;
    }

    function setActiveTab(selectedTab) {
        tabs.forEach(tab => {
            const isActive = tab === selectedTab;
            tab.classList.toggle('active', isActive);
            tab.setAttribute('aria-selected', isActive.toString());
            tab.setAttribute('tabindex', isActive ? '0' : '-1');
        });

        // Scroll the active tab into view if container is scrollable
        if (tabContainer.scrollWidth > tabContainer.clientWidth) {
            // A small delay can help if the click/focus transition interferes
            setTimeout(() => {
                selectedTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }, 50);
        }
        // console.log(`Tab changed to: ${selectedTab.dataset.tab}`);
    }

    // Tab click functionality
    tabContainer.addEventListener('click', (event) => {
        const clickedTab = event.target.closest('.tab-item');
        if (!clickedTab || clickedTab.classList.contains('active')) {
            // Click was not on a tab item or it's already active
            return;
        }
        setActiveTab(clickedTab);
    });

    // Keyboard navigation (ArrowLeft, ArrowRight, Home, End)
    tabContainer.addEventListener('keydown', (event) => {
        const currentFocusedTab = document.activeElement;
        // Ensure the event originated from within the tab container and on a tab item
        if (!currentFocusedTab || !currentFocusedTab.matches('.tab-item') || !tabContainer.contains(currentFocusedTab)) {
            return;
        }

        let newTabToFocus;
        const currentIndex = Array.from(tabs).indexOf(currentFocusedTab);

        if (event.key === 'ArrowRight') {
            event.preventDefault(); // Prevent page scroll
            newTabToFocus = tabs[(currentIndex + 1) % tabs.length];
        } else if (event.key === 'ArrowLeft') {
            event.preventDefault(); // Prevent page scroll
            newTabToFocus = tabs[(currentIndex - 1 + tabs.length) % tabs.length];
        } else if (event.key === 'Home') {
            event.preventDefault();
            newTabToFocus = tabs[0];
        } else if (event.key === 'End') {
            event.preventDefault();
            newTabToFocus = tabs[tabs.length - 1];
        }

        if (newTabToFocus) {
            newTabToFocus.focus();
            setActiveTab(newTabToFocus); // Also activate the tab
        }
    });

    // Initial setup for the pre-selected active tab's tabindex
    const initiallyActiveTab = tabContainer.querySelector('.tab-item.active');
    if (initiallyActiveTab) {
        setActiveTab(initiallyActiveTab); // This will set its tabindex to 0 and others to -1
    }
});