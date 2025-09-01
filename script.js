// Smooth scrolling for navigation links
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

// Download tracking
function downloadFile(platform) {
    // Track download analytics
    console.log(`Download initiated for ${platform}`);
    
    // Show download started message
    showNotification(`Download started for ${platform}`, 'success');
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : '#3498db'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(44, 62, 80, 0.95)';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.background = '#2c3e50';
        navbar.style.backdropFilter = 'none';
    }
});

// Feature cards animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.addEventListener('DOMContentLoaded', () => {
    const featureCards = document.querySelectorAll('.feature-card');
    const downloadCards = document.querySelectorAll('.download-card');
    
    [...featureCards, ...downloadCards].forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Copy to clipboard functionality for shortcuts
document.querySelectorAll('.shortcut-item').forEach(item => {
    item.addEventListener('click', () => {
        const shortcut = item.querySelector('kbd').textContent;
        navigator.clipboard.writeText(shortcut).then(() => {
            showNotification(`Copied "${shortcut}" to clipboard`, 'success');
        });
    });
});

// Mobile menu toggle (if needed)
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Download button click handlers
document.addEventListener('DOMContentLoaded', () => {
    // Windows download
    const windowsBtn = document.querySelector('a[href="git-bridge-windows.zip"]');
    if (windowsBtn) {
        windowsBtn.addEventListener('click', () => downloadFile('Windows'));
    }
    
    // macOS download
    const macosBtn = document.querySelector('a[href="git-bridge-macos.dmg"]');
    if (macosBtn) {
        macosBtn.addEventListener('click', () => downloadFile('macOS'));
    }
    
    // Linux download
    const linuxBtn = document.querySelector('a[href="git-bridge-linux.AppImage"]');
    if (linuxBtn) {
        linuxBtn.addEventListener('click', () => downloadFile('Linux'));
    }
    
    // Source download
    const sourceBtn = document.querySelector('a[href="../git-bridge-source.zip"]');
    if (sourceBtn) {
        sourceBtn.addEventListener('click', () => downloadFile('Source Code'));
    }
});

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    // Press 'D' to go to download section
    if (e.key.toLowerCase() === 'd' && !e.ctrlKey && !e.altKey) {
        const downloadSection = document.querySelector('#download');
        if (downloadSection) {
            downloadSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Press 'F' to go to features section
    if (e.key.toLowerCase() === 'f' && !e.ctrlKey && !e.altKey) {
        const featuresSection = document.querySelector('#features');
        if (featuresSection) {
            featuresSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// Add loading animation for download buttons
function addLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing Download...';
    button.style.pointerEvents = 'none';
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.style.pointerEvents = 'auto';
    }, 2000);
}