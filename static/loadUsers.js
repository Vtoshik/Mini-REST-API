async function loadUsers() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('No access token found. Please log in.');
        window.location.href = '/login';
        return;
    }
    try {
        const response = await fetch('/api/v1/users', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const profiles = await response.json();
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = '';
            profiles.forEach(profile => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${profile.username}</td>
                    <td><a href="/user/${profile.id}" class="info-user">Info</a></td>
                    <td><a href="/delete/${profile.id}" class="delete-user">Delete</a></td>
                `;
                tbody.appendChild(row);
            });
            document.querySelectorAll('.delete-user').forEach(link => {
                link.addEventListener('click', handleDelete);
            });
        } else if (response.status === 401) {
            alert('Authentication failed. Please log in again.');
            window.location.href = '/login';
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

document.addEventListener('DOMContentLoaded', loadUsers);