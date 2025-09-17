async function handleUpdate(pageId) {
    const { route, alertText, method, updatedData} = checkRoute('update');

    try {
        await apiRequest(method, `/api/v1${route}/${pageId}`, alertText, updatedData);
        alert(`${alertText} updated successfully`);
        loadInfo();
    } catch (error) {
        console.error('Update error:', error);
        alert(`Failed to update ${alertText}: ${error.message}`);
    }

}