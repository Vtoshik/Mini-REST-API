async function loadInfo() {
    const pathParts = window.location.pathname.split('/');
    const pageId = pathParts[pathParts.length - 1];
    if (!pageId) return;

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

    try {
        const response = await fetch(`/api/v1${route}/${pageId}`, {
            method: 'GET',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const object = await response.json();
            if (status==='admin'){
                document.getElementById('user-info').innerHTML = `
                    <li>Id: ${object.id}</li>
                    <li>Username: ${object.username}</li>
                    <li>Email: ${object.email}</li>
                    <li>Status: ${object.status || 'N/A'}</li>
                    <li>Created At: ${object.created_at}</li>
                `;
            } else if (status ==='user'){
                document.getElementById('note-info').innerHTML = `
                    <li>Id: ${object.id}</li>
                    <li>Title: ${object.title}</li>
                    <li>Content: ${object.content}</li>
                    <li>Created at: ${object.created_at}</li>
                `
            }
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Error loading info:', error);
        alert(`Failed to load ${alertText} info`);
    }
}

document.addEventListener('DOMContentLoaded', loadInfo);