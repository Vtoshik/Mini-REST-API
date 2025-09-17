async function addData(event) {
   event.preventDefault();
   const { route, alertText, data, backroute } = checkRoute('add');
   
   try {
      await apiRequest('POST', `/api/v1${route}`, alertText, data);
      alert(`${alertText} created successfully`);
      window.location.href = `${backroute}`;
   } catch (error) {
      console.error('Fetch error:', error);
      alert('An unexpected error occurred');
   }
}