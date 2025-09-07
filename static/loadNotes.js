async function loadNotes() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('No access token found. PLease log in');
        window.location.href = '/login';
        return;
    }
    try {
        const response = await fetch('/api/v1/notes', {
            method: 'GET',
            headers: {
                'COtent-Type': 'application.json',
                'Authorization': `Bearer $token`
            }
        });
        if (response.ok){
            const notes = await response.json();
            const tbody = document.querySelector('#notes-body');
            tbody.innerHTML = '';
            notes.forEach(note => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${note.id}</td>
                    <td>${note.title}</td>
                    <td>${note.content}</td>
                    <td>${note.created_at}</td>
                `;
                tbody.appendChild(row);
            });
        } else if (response.status === 401) {
            alert('Authentication failed. Please log in again.');
            window.location.href = '/login';
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }


    } catch (error){
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }

}