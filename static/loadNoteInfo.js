async function loadNoteInfo() {
    const pathParts = window.location.pathname.split('/');
    const noteId = pathParts[pathParts.length - 1];
    if (!noteId) return;

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`/api/v1/notes/${noteId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const note = await response.json();
            document.getElementById('note-info').innerHTML = `
                <li>Id: ${note.id}</li>
                <li>Title: ${note.title}</li>
                <li>Content: ${note.content}</li>
                <li>Created at: ${note.created_at}</li>
            `
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Error loading note info:', error);
        alert('Failed to load note info');
    }
}

document.addEventListener('DOMContentLoaded', loadNoteInfo);