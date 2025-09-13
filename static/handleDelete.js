async function handleDelete(pageId) {

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
            method: 'DELETE',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            alert(`${alertText} deleted successfully`);
            loadObjects();
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert(`An unexpected error occurred while deleting ${alertText}`);
    }
}

document.querySelectorAll('.delete-user').forEach(link => {
    link.addEventListener('click', handleDelete);
});