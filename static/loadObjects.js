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
            const objects = await response.json();
            const tbody = document.querySelector('.list-body');
            tbody.innerHTML = '';
            objects.forEach(obj => {
                const row = document.createElement('tr');
                if (status === 'user') {
                    row.innerHTML = `
                        <td>${obj.id}</td>
                        <td>${obj.title}</td>
                        <td>
                            <button class="info-note" onclick="window.location.href='/note/${obj.id}'">Content</button>
                        </td>
                        <td>
                            <button class="delete-object" onclick="handleDelete(${obj.id})">Delete</button>
                        </td>
                    `;
                } else if (status === 'admin') {
                    row.innerHTML = `
                        <td>${obj.username}</td>
                        <td>
                            <button class="info-user" onclick="window.location.href='/admin/user/${obj.id}'">Info</button>
                        </td>
                        <td>
                            <button class="delete-object" onclick="handleDelete(${obj.id})">Delete</button>
                        </td>
                    `;
                }
                tbody.appendChild(row);
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