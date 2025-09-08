async function handleAddNote(event) {
    event.preventDefault();

    const title = document.querySelector('input[name="title"]').value;
    const content = document.querySelector('input[name="content"]').value;
    const userId = localStorage.getItem('user_id');

    if (!title) {
        alert('Title field required');
        return;
    }

    if (!userId) {
        alert('User ID not found. Please log in.');
        window.location.href = '/login';
        return;
    }

    const data = { title, content, user_id: parseInt(userId)};
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch('api/v1/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Note created successfully');
            window.location.href = '/';
        } else {
            const error = await response.text();
            alert(`Error ${response.status}: ${error}`);
        }
    } catch(error) {
        console.error('Fetch error:', error);
        alert('An unexpected error occurred in handleAddNote');
    }

}