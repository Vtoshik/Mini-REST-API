async function loadObjects() {
    const status = localStorage.getItem('user_status');
    const { route, alertText } = checkRoute();

    try {
        const result =  await apiRequest('GET', `/api/v1${route}`, alertText);
        const objects = result.objects;
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
    } catch (error) {
        console.error('Error loading objects:', error);
        alert(`Failed to load ${alertText}: ${error.message}`);
    }
}

document.addEventListener('DOMContentLoaded', loadObjects);