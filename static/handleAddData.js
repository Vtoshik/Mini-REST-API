async function handleAddData(event) {
   event.preventDefault();

   const username = document.querySelector('input[name="username"]').value;
   const email = document.querySelector('input[name="email"]').value;
   const password = document.querySelector('input[name="password"]').value;

   if (!username || !email || !password) {
      alert('All fields are required');
      return;
   }

   const data = { username, email, password };

   try {
      const response = await fetch('/api/v1/register', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(data)
      });

      if (response.ok) {
         window.location.href = '/';
      } else {
         const error = await response.text();
         alert(`Error: ${error}`);
      }
   } catch (error) {
      console.error('Fetch error:', error);
      alert('An unexpected error occurred');
   }
}