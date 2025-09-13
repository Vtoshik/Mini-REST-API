async function addData(event) {
   event.preventDefault();

   let data = {};
   const token = localStorage.getItem('access_token');
   const status = localStorage.getItem('user_status');

   let route = '';
   let alertText = 'Note';
   let backroute = '';

   if (status === 'admin'){
      const username = document.querySelector('input[name="username"]').value;
      const email = document.querySelector('input[name="email"]').value;
      const password = document.querySelector('input[name="password"]').value;

      if (!username || !email || !password) {
         alert('All fields are required');
         return;
      }

      route = '/register';
      alertText = 'User';
      backroute = '/admin/';
      data = { username, email, password };
   } else if (status === 'user') {
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

      route = '/notes';
      backroute = '/';
      data = { title, content, user_id: parseInt(userId)};
   } else {
      alert(`Not existing route ${route}`);
   }
   
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
         const error = await response.text();
            alert(`Error ${response.status}: ${error}`);
      }
   } catch (error) {
      console.error('Fetch error:', error);
      alert('An unexpected error occurred');
   }
}