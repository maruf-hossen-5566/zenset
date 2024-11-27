document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.querySelector("button[type='submit']");
    const form = document.querySelector("form");

    // Function to check if all inputs are filled
    const checkFormValidity = () => {
        const formInputs = document.querySelectorAll("form input");
        return Array.from(formInputs).every(input => input.value.trim() !== "");
    };

    // Initial check
    submitButton.disabled = !checkFormValidity();

    // Listen to all input changes
    form.addEventListener("input", () => {
        submitButton.disabled = !checkFormValidity();
    });

    // Submit form
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        submitButton.disabled = true;
        form.submit();
    });
});
