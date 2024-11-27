document.addEventListener("DOMContentLoaded", function () {
    let buttons = document.querySelectorAll(".freeze-button");

    buttons.forEach(button => {
        button.addEventListener("click", function () {
            button.style.pointerEvents = "none";
        });
    });

});
