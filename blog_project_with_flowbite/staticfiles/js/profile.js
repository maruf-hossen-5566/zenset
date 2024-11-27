document.addEventListener("DOMContentLoaded", function () {
    let submitButton = document.querySelector("button[type='submit']");
    let form = document.querySelector("form");

    // Initial state
    submitButton.disabled = true;

    // Listen to all input changes
    form.addEventListener("input", function () {
        submitButton.disabled = false;
    });

    // Submit form
    submitButton.addEventListener("click", function (event) {
        event.preventDefault();
        submitButton.disabled = true;
        form.submit();
    });
});
