async function handleDelete(event) {
    event.preventDefault();
    const userId = event.target.closest('a').getAttribute('href').split('/').pop();

    try {
        const response = await fetch(`/api/v1/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            alert('User deleted successfully');
            loadUsers();
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('An unexpected error occurred');
    }
}

document.querySelectorAll('.delete-user').forEach(link => {
    link.addEventListener('click', handleDelete);
});