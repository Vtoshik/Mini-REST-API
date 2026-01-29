async function loadInfo() {
    const pathParts = window.location.pathname.split('/');
    const pageId = pathParts[pathParts.length - 1];
    if (!pageId) return;
    const status = localStorage.getItem('user_status');
    const { route, alertText } = checkRoute();
    
    try {
        const result = await apiRequest('GET', `/api/v1${route}/${pageId}`, alertText);
        const object = result.objects;
        if (status==='admin'){
            document.getElementById('info-fields').innerHTML = `
                <li>Id: <span>${escapeHtml(object.id)}</span></li>
                <li>Username:
                    <span contenteditable="true" data-field="username">
                    ${escapeHtml(object.username)}</span></li>
                <li>Email:
                    <span contenteditable="true" data-field="email">
                    ${escapeHtml(object.email)}</span></li>
                <li>Status:
                    <span contenteditable="true" data-field="status">
                    ${escapeHtml(object.status || 'N/A')}</span></li>
                <li>Created At: ${escapeHtml(object.created_at)}</li>
            `;
            document.getElementById('button-group').innerHTML = `
                <button type="button" class="update-btn" onclick="handleUpdate(${object.id})">Update</button>
                <button type="button" onclick="window.location.href='/admin/'">Back to Index</button>
            `;
        } else if (status ==='user'){
            document.getElementById('info-fields').innerHTML = `
                <li>Title:
                    <span contenteditable="true" data-field="title">
                    ${escapeHtml(object.title)}</span></li>
                <li>Content:
                    <span contenteditable="true" data-field="content">
                    ${escapeHtml(object.content)}</span></li>
                <li>Created at: ${escapeHtml(object.created_at)}</li>
            `;
            document.getElementById('button-group').innerHTML = `
                <button type="button" class="update-btn" onclick="handleUpdate(${object.id})">Update</button>
                <button type="button" onclick="window.location.href='/'">Back to Index</button>
            `;
        }
    } catch (error) {
        console.error('Error loading info:', error);
        alert(`Failed to load ${alertText} info`);
    }
}

document.addEventListener('DOMContentLoaded', loadInfo);