document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');

    if (!form) {
        console.error("Error: 'login-form' not found. Ensure the form exists before executing the script.");
        return;
    }

    form.addEventListener('submit', function (event) {
        if (form.dataset.submitted === "true") {
            return;
        }

        let isValid = true;
        let usernameOrEmailInput = document.getElementById('id_username');
        let passwordInput = document.getElementById('id_password');

        if (!usernameOrEmailInput || !passwordInput) {
            console.error("Error: Input fields not found.");
            return;
        }

        let usernameError = document.getElementById('username-error');
        let passwordError = document.getElementById('password-error');

        let usernameOrEmail = usernameOrEmailInput.value.trim();
        let password = passwordInput.value.trim();

        // Reset error messages and hide the error divs initially
        usernameError.textContent = '';
        passwordError.textContent = '';
        usernameError.style.display = 'none';
        passwordError.style.display = 'none';

        // Basic validation
        if (!usernameOrEmail || (!/\S+@\S+\.\S+/.test(usernameOrEmail) && !/\w+/.test(usernameOrEmail))) {
            usernameError.textContent = 'Please enter a valid email address or username.';
            usernameError.style.display = 'block'; // Show the error
            isValid = false;
        }

        if (!password) {
            passwordError.textContent = 'Password cannot be empty.';
            passwordError.style.display = 'block'; // Show the error
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();  // Prevent form submission if there are errors
            return;
        }

        event.preventDefault(); // Stop form submission while checking credentials

        // Check if user exists and validate the password
        checkUserExistsAndPassword(usernameOrEmail, password)
            .then(response => {
                if (response.valid) {
                    form.dataset.submitted = "true";  // Prevent double submission
                    form.submit();  // Proceed with form submission if valid
                } else {
                    // Display appropriate error messages
                    if (response.error_type === "user_not_found") {
                        usernameError.textContent = 'This email or username is not registered.';
                        usernameError.style.display = 'block'; // Show the error
                    } else if (response.error_type === "invalid_password") {
                        passwordError.textContent = 'Incorrect password.';
                        passwordError.style.display = 'block'; // Show the error
                    } else {
                        usernameError.textContent = 'Invalid username or email.';
                        passwordError.textContent = 'Invalid password.';
                        usernameError.style.display = 'block';
                        passwordError.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                usernameError.textContent = 'An error occurred. Please try again later.';
                usernameError.style.display = 'block'; // Show the error
            });
    });

    // Function to check if user exists and validate password
    function checkUserExistsAndPassword(usernameOrEmail, password) {
        const url = `/check_user_exists_password/?username_or_email=${encodeURIComponent(usernameOrEmail)}&password=${encodeURIComponent(password)}`;

        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Server response:", data);
                return data;
            })
            .catch(error => {
                console.error('Error fetching:', error);
                return { valid: false, error_type: "server_error" }; // Handle server errors
            });
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const forgotPasswordLink = document.querySelector('a[href="{% url "password_reset" %}"]');
    const forgotPasswordForm = document.getElementById('forgot-password-form');

    // Show the reset password form when the link is clicked
    forgotPasswordLink.addEventListener('click', function (e) {
        e.preventDefault();  // Prevent the default link action
        forgotPasswordForm.style.display = 'block';  // Show the form
    });

    // You can also handle the reset form submission with JavaScript if needed
    const resetPasswordForm = document.getElementById('reset-password-form');
    resetPasswordForm.addEventListener('submit', function (e) {
        e.preventDefault();

        // Get the email address
        const email = document.getElementById('reset-email').value;

        // Send the email to the backend to generate a reset link
        fetch('{% url "password_reset" %}', {
            method: 'POST',
            body: JSON.stringify({ email: email }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Get CSRF token from cookies
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('reset-message').innerText = 'A reset link has been sent to your email address.';
            } else {
                document.getElementById('reset-message').innerText = 'There was an error sending the reset link. Please try again.';
            }
        })
        .catch(error => {
            document.getElementById('reset-message').innerText = 'Error: ' + error;
        });
    });
});

// Utility function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
