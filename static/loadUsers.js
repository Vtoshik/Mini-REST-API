async function loadUsers() {
    try {
        const response = await fetch('/api/v1/users', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            const profiles = await response.json();
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = '';
            profiles.forEach(profile => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${profile.username}</td>
                    <td><a href="/user/${profile.id}">Info</a></td>
                    <td><a href="/delete/${profile.id}" class="delete-user">Delete</a></td>
                `;
                tbody.appendChild(row);
            });
            document.querySelectorAll('.delete-user').forEach(link => {
                link.addEventListener('click', handleDelete);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

document.addEventListener('DOMContentLoaded', loadUsers);