document.addEventListener('DOMContentLoaded', () => {
    function logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_status');
        window.location.href = '/login';
    }

    const logoutLink = document.querySelector('button[onclick="window.location.href=\'/logout\'"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(event) {
            event.preventDefault();
            logout();
        });
    } else {
        console.warn('Logout link not found in the document');
    }
});