
// Automatically remove notification messages after 5 seconds

document.addEventListener("DOMContentLoaded", function () {

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {
            alert.style.opacity = "0";

            setTimeout(function () {
                alert.remove();
            }, 500);

        }, 5000);

    });

});


document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("profileForm");
    const button = document.getElementById("saveProfileBtn");
    const buttonText = document.getElementById("saveButtonText");
    const status = document.getElementById("saveStatus");

    if (!form || !button) return;

    let submitting = false;

    form.addEventListener("submit", function (event) {
        if (submitting) {
            event.preventDefault();
            return;
        }

        if (!form.checkValidity()) {
            form.reportValidity();
            event.preventDefault();
            return;
        }

        submitting = true;
        button.disabled = true;
        buttonText.textContent = "Saving...";
        status.textContent = "Saving your profile...";
    });
});




document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(
        'form[data-auth-form], form[action*="signin"], form[action*="signup"], form[action*="login"]'
    );

    forms.forEach(function (form) {
        let submitting = false;

        form.addEventListener("submit", function (event) {
            if (submitting) {
                event.preventDefault();
                return;
            }

            if (!form.checkValidity()) {
                form.reportValidity();
                event.preventDefault();
                return;
            }

            submitting = true;

            const button = form.querySelector(
                'button[type="submit"], input[type="submit"]'
            );

            if (button) {
                button.disabled = true;

                if (button.tagName === "BUTTON") {
                    button.dataset.originalText = button.innerText;
                    button.innerText = "Please wait...";
                } else {
                    button.dataset.originalText = button.value;
                    button.value = "Please wait...";
                }
            }
        });
    });
});
