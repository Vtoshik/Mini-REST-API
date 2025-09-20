function checkRoute(func_type=NaN){
    const status = localStorage.getItem('user_status');
    let route = '';
    let alertText = 'Note';
    let method = 'PATCH';
    let backroute = '';

    if (status === 'admin'){
        route = func_type === 'add' ? '/register' : '/admin/users';
        alertText = 'User';
        method = 'PUT';
        backroute = '/admin/';
    } else if (status === 'user') {
        route = '/notes';
        backroute = '/';
    } else {
        alert(`Not existing route ${route}`);
        throw new Error(`Invalid user status: ${status}`);
    }


    if (func_type === 'update'){
        const cleanText = (text) => text.replace(/\s+/g, ' ').trim();

        const updatedData = status === 'admin' ? {
            username: cleanText(document.querySelector('[data-field="username"]').textContent),
            email: cleanText(document.querySelector('[data-field="email"]').textContent),
            status: cleanText(document.querySelector('[data-field="status"]').textContent)
        } : {
            title: cleanText(document.querySelector('[data-field="title"]').textContent),
            content: cleanText(document.querySelector('[data-field="content"]').textContent)
        };

        if (status === 'admin') {
            if (updatedData.status !== 'user' && updatedData.status !== 'admin') {
                alert('Status can be only user or admin');
                throw new Error('Status can be only user or admin');
            }
        }

        return {
            route: route,
            alertText: alertText,
            method: method,
            updatedData: updatedData
        };
    } else if (func_type === 'add') {
        let data = {};
        if (status === 'admin'){
            const username = document.querySelector('input[name="username"]').value;
            const email = document.querySelector('input[name="email"]').value;
            const password = document.querySelector('input[name="password"]').value;

        if (!username || !email || !password) {
            alert('All fields are required');
            return;
        }
        if (username.length < 3 || username.length > 20) {
            alert('Username must be 3-20 characters');
            return;
        }
        if (password.length < 8) {
            alert('Password must be at least 8 characters');
            return;
        }

        data = { username, email, password };
        } else if (status === 'user') {
            const title = document.querySelector('input[name="title"]').value;
            const content = document.querySelector('input[name="content"]').value;
            const userId = localStorage.getItem('user_id');

            if (!title) {
                alert('Title field required');
                return;
            }
            if (title.length > 20) {
                alert('Title must be 20 characters or less');
                return;
            }
            if (!userId) {
                alert('User ID not found. Please log in.');
                window.location.href = '/login';
                return;
            }

            data = { title, content};
        } 

        return {
            route: route,
            alertText: alertText,
            data: data,
            backroute: backroute
        }
    }

    return {
        route: route,
        alertText: alertText
    };
}

async function apiRequest(method, route, alertText, body = null, authRequired = true){
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (authRequired) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('No access token found. PLease log in');
            window.location.href = '/login';
            throw new Error('No access token found');
        }
        options.headers['Authorization'] = `Bearer ${token}`;
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
        } else if (response.status === 401 && authRequired) {
            alert('Authentication failed. Please log in again.');
            window.location.href = '/login';
            throw new Error('Authentication failed');
        } else {
            const error = await response.json();
            alert(`Error ${response.status}: ${error.message || JSON.stringify(error)}`);
            throw new Error(`Server error: ${error.message || JSON.stringify(error)}`);
        }
    } catch (error) {
        console.error('API request error', error);
        alert(`Failed to load ${alertText}`);
        throw error;
    }

}