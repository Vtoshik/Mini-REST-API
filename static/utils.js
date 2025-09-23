function checkRoute(action = null) {
    const path = window.location.pathname;
    const status = localStorage.getItem('user_status');
    let route, alertText, backroute, data, method, updatedData;

    if (path.startsWith('/admin')) {
        route = '/admin/users';
        alertText = 'User';
        backroute = '/admin/';
        if (action === 'add') {
            const username = document.querySelector('input[name="username"]')?.value;
            const email = document.querySelector('input[name="email"]')?.value;
            const password = document.querySelector('input[name="password"]')?.value;
            const confirmPassword = document.querySelector('input[name="confirm-password"]')?.value;
            data = { username, email, password, confirmPassword };
        } else if (action === 'update') {
            const username = document.querySelector('span[data-field="username"]')?.textContent.trim();
            const email = document.querySelector('span[data-field="email"]')?.textContent.trim();
            const statusField = document.querySelector('span[data-field="status"]')?.textContent.trim();
            updatedData = { username, email, status: statusField };
            method = 'PUT';
        }
    } else {
        route = '/notes';
        alertText = 'Note';
        backroute = '/';
        if (action === 'add') {
            const title = document.querySelector('input[name="title"]')?.value;
            const content = document.querySelector('textarea[name="content"]')?.value || null;
            data = { title, content };
        } else if (action === 'update') {
            const title = document.querySelector('span[data-field="title"]')?.textContent.trim();
            const content = document.querySelector('span[data-field="content"]')?.textContent.trim();
            updatedData = { title, content };
            method = 'PATCH';
        }
    }

    return { route, alertText, backroute, data, method, updatedData };
}

async function apiRequest(method, route, alertText, body = null, authRequired = true, csrfToken = null){
    const options = {
        method: method,
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    //if (authRequired) {
    //    const token = localStorage.getItem('access_token');
    //    if (!token) {
     //       const errorMessage = 'No access token found. Please log in';
      //      alert(errorMessage);
        //    window.location.href = '/login';
         //   throw new Error(errorMessage);
        //}
        //options.headers['Authorization'] = `Bearer ${token}`;
    //}

    if (csrfToken) {
        options.headers['X-CSRF-Token'] = csrfToken;
    }
    
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${route}`, options);
        if (response.ok){
            if (response.status === 204) {
                return { data: null };
            }
            const data = await response.json();
            return { objects: data };
        } else {
            const error = await response.json();
            let message = error.message || JSON.stringify(error);
            if (error.errors) {
                message = Object.values(error.errors).flat().join(", ");
            }
            if (response.status === 401 && authRequired) {
                alert('Authentication failed. Please log in again.');
                window.location.href = '/login';
                throw new Error('Authentication failed');
            }
            throw new Error(message);
        }
    } catch (error) {
        console.error('API request error:', error);
        throw error; // Let caller handle the error
    }
}