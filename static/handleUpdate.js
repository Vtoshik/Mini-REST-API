async function handleUpdate(pageId) {
    const token = localStorage.getItem('access_token');
    const { route, alertText, method, updatedData} = checkRoute('update');

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