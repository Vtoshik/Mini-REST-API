async function addData(event) {
   event.preventDefault();

   const token = localStorage.getItem('access_token');
   const { route, alertText, data, backroute } = checkRoute('add');
   
   try {
      const response = await fetch(`/api/v1${route}`, {
         method: 'POST',
         headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` 
         },
         body: JSON.stringify(data)
      });

      if (response.ok) {
         alert(`${alertText} created successfully`);
         window.location.href = `${backroute}`;
      } else {
         const error = await response.json();
            alert(`Error ${response.status}: ${error}`);
      }
   } catch (error) {
      console.error('Fetch error:', error);
      alert('An unexpected error occurred');
   }
}