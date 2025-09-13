async function loadObjects() {
    const token = localStorage.getItem('access_token');
    const status = localStorage.getItem('user_status');

    let route = '';
    let alertText = 'Note';

    if (status === 'admin'){
        route = '/admin/users';
        alertText = 'User';
    } else if (status === 'user') {
        route = '/notes';
    } else {
        alert(`Not existing route ${route}`);
    }

    if (!token) {
        alert('No access token found. PLease log in');
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch(`/api/v1${route}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok){
            const object = await response.json();
            const tbody = document.querySelector('.list-body');
            tbody.innerHTML = '';
            object.forEach(object => {
                const row = document.createElement('tr');
                if (status === 'user') {
                    row.innerHTML = `
                        <td>${object.id}</td>
                        <td>${object.title}</td>
                        <td><a href="/note/${object.id}" class="info-note">
                            Content</a></td>
                        <td><a href="/note/delete/${object.id}" class="delete-object">
                            Delete</a></td>
                    `;
                } else if (status === 'admin') {
                    row.innerHTML = `
                        <td>${object.username}</td>
                        <td><a href="/admin/user/${object.id}" class="info-user">Info</a></td>
                        <td><a href="/admin/delete/${object.id}" class="delete-object">Delete</a></td>
                    `;
                }
                tbody.appendChild(row);
            });
            document.querySelectorAll('.delete-object').forEach(link => {
               link.addEventListener('click', handleDelete)
            });
        } else if (response.status === 401) {
            alert('Authentication failed. Please log in again.');
            window.location.href = '/login';
        } else {
            const error = await response.text();
            alert(`Error ${response.status}: ${error}`);
        }
    } catch (error){
        console.error('Error loading:', error);
        alert(`Failed to load ${alertText}`);
    }

}

document.addEventListener('DOMContentLoaded', loadObjects);