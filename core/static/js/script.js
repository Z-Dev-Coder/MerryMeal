/* -------------------------------------------------------------
 * MERRYMEAL UNIFIED PORTAL - ACCESSIBILITY & LAYOUT SCRIPTS
 * Handles Text Scaler & High-Contrast Mode Persistence
 * ------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
    // A11y DOM Elements
    const btnToggleContrast = document.getElementById('btn-toggle-contrast');
    const btnScaleText = document.getElementById('btn-scale-text');
    const body = document.body;

    // 1. Core High-Contrast Toggler with LocalStorage Cache
    const initContrastTheme = () => {
        const isHighContrast = localStorage.getItem('a11y-high-contrast') === 'true';
        if (isHighContrast) {
            body.classList.add('high-contrast-mode');
        } else {
            body.classList.remove('high-contrast-mode');
        }
    };

    if (btnToggleContrast) {
        btnToggleContrast.addEventListener('click', () => {
            const hasContrast = body.classList.toggle('high-contrast-mode');
            localStorage.setItem('a11y-high-contrast', hasContrast);
            
            // Trigger visual announcement for screen readers
            announceToScreenReader(hasContrast ? "High contrast mode activated." : "High contrast mode deactivated.");
        });
    }

    // 2. Dynamic Text Size Scaler (Supports 3 increments: 100%, 120%, 140%)
    const fontTiers = ['100%', '118%', '136%'];
    let activeFontTier = parseInt(localStorage.getItem('a11y-font-tier')) || 0;

    const applyFontScaling = () => {
        const percentageScale = fontTiers[activeFontTier];
        document.documentElement.style.fontSize = percentageScale;
        localStorage.setItem('a11y-font-tier', activeFontTier);
        
        // Update helper screen text if present
        const label = btnScaleText ? btnScaleText.querySelector('.a11y-label') : null;
        if (label) {
            label.innerHTML = `Size: ${activeFontTier + 1}`;
        }
    };

    if (btnScaleText) {
        btnScaleText.addEventListener('click', () => {
            activeFontTier = (activeFontTier + 1) % fontTiers.length;
            applyFontScaling();
            
            // Screen reader notification
            announceToScreenReader(`Font size adjusted to scale level ${activeFontTier + 1}.`);
        });
    }

    // 3. Screen Reader ARIA Live Zone Logger
    const announceToScreenReader = (message) => {
        let liveZone = document.getElementById('a11y-live-announcer');
        if (!liveZone) {
            liveZone = document.createElement('div');
            liveZone.id = 'a11y-live-announcer';
            liveZone.setAttribute('aria-live', 'polite');
            liveZone.setAttribute('aria-atomic', 'true');
            liveZone.style.position = 'absolute';
            liveZone.style.width = '1px';
            liveZone.style.height = '1px';
            liveZone.style.margin = '-1px';
            liveZone.style.overflow = 'hidden';
            liveZone.style.clip = 'rect(0,0,0,0)';
            document.body.appendChild(liveZone);
        }
        liveZone.textContent = '';
        setTimeout(() => {
            liveZone.textContent = message;
        }, 50);
    };

    // 4. Scroll Reveal Intersection Observer Script
    const revealElements = document.querySelectorAll('.scroll-reveal');
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target); // Unobserve to keep active state static once loaded
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => {
        revealObserver.observe(el);
    });

    // Run Initializations
    initContrastTheme();
    applyFontScaling();
});
