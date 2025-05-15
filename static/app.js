// Function to refresh the page if translation is in progress
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the result page
    const progressBar = document.querySelector('.progress-bar');
    
    if (progressBar) {
        // Get progress value
        const progress = parseInt(progressBar.style.width) || 0;
        
        // If job is not completed (progress < 100), set auto-refresh
        if (progress < 100) {
            // Check status every 5 seconds
            setTimeout(function() {
                window.location.reload();
            }, 5000);
        }
    }
});
