// Validation for password match and strength
document.querySelector('form').addEventListener('submit', function(event) {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        event.preventDefault();  // Prevent form submission
    }

    // Additional password validation can go here (e.g., length, special characters)
});
