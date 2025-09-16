async function handleUpdate(pageId) {
    const token = localStorage.getItem('access_token');
    const status = localStorage.getItem('user_status');

    let route = '';
    let alertText = 'Note';
    let method = 'PATCH';

    if (status === 'admin'){
        route = '/admin/users';
        alertText = 'User';
        method = 'PUT';
    } else if (status === 'user') {
        route = '/notes';
    } else {
        alert(`Not existing route ${route}`);
    }

    const cleanText = (text) => text.replace(/\s+/g, ' ').trim();

    const updatedData = status === 'admin' ? {
        username: cleanText(document.querySelector('[data-field="username"]').textContent),
        email: cleanText(document.querySelector('[data-field="email"]').textContent),
        status: cleanText(document.querySelector('[data-field="status"]').textContent)
    } : {
        title: cleanText(document.querySelector('[data-field="title"]').textContent),
        content: cleanText(document.querySelector('[data-field="content"]').textContent)
    };


    try {
        const response = await fetch(`/api/v1${route}/${pageId}`, {
            method: method,
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(updatedData)
        });

        if (response.ok) {
            alert(`${alertText} updated successfully`);
            loadInfo();
        } else {
            const error = await response.json();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Update error:', error);
        alert(`An unexpected error occurred while updating ${alertText}`);
    }
}