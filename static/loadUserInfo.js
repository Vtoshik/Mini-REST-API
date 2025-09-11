async function loadUserInfo() {
    const pathParts = window.location.pathname.split('/');
    const userId = pathParts[pathParts.length - 1];
    if (!userId) return;

    const token = localStorage.getItem('access_token');
    try {
        const response = await fetch(`/api/v1/users/${userId}`, {
            method: 'GET',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const user = await response.json();
            document.getElementById('user-info').innerHTML = `
                <li>Id: ${user.id}</li>
                <li>Username: ${user.username}</li>
                <li>Email: ${user.email}</li>
                <li>Status: ${user.status || 'N/A'}</li>
                <li>Created At: ${user.created_at}</li>
            `;
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Error loading user info:', error);
        alert('Failed to load user info');
    }
}

document.addEventListener('DOMContentLoaded', loadUserInfo);