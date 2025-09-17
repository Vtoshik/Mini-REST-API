async function handleDelete(pageId) {
    const { route, alertText } = checkRoute();

    try {
        await apiRequest('DELETE', `/api/v1${route}/${pageId}`, alertText);
        alert(`${alertText} deleted successfully`);
        loadObjects();
    } catch (error) {
        console.error('Delete error:', error);
        alert(`An unexpected error occurred while deleting ${alertText}`);
    }
}

document.querySelectorAll('.delete-user').forEach(link => {
    link.addEventListener('click', handleDelete);
});