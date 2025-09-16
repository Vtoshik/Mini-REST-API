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
                    <li>Id: <span>${object.id}</span></li>
                    <li>Username: 
                        <span contenteditable="true" data-field="username">
                        ${object.username}</span></li>
                    <li>Email: 
                        <span contenteditable="true" data-field="email">
                        ${object.email}</span></li>
                    <li>Status: 
                        <span contenteditable="true" data-field="status">
                        ${object.status || 'N/A'}</span></li>
                    <li>Created At: ${object.created_at}</li>
                    <button class="delete-object" onclick="handleUpdate(${object.id})">Update</button>
                `;
            } else if (status ==='user'){
                document.getElementById('note-info').innerHTML = `
                    <li>Id: ${object.id}</li>
                    <li>Title: 
                        <span contenteditable="true" data-field="title">
                        ${object.title}</span></li>
                    <li>Content: 
                        <span contenteditable="true" data-field="content">
                        ${object.content}</span></li>
                    <li>Created at: ${object.created_at}</li>
                    <button class="delete-object" onclick="handleUpdate(${object.id})">Update</button>
                `
            }
        } else {
            const error = await response.json();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Error loading info:', error);
        alert(`Failed to load ${alertText} info`);
    }
}

document.addEventListener('DOMContentLoaded', loadInfo);