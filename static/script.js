
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



document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("scholarshipSearch");
    const categoryButtons = document.querySelectorAll(".category-pill");
    const deadlineFilter = document.getElementById("deadlineFilter");
    const includeExpired = document.getElementById("includeExpired");
    const cards = document.querySelectorAll(".scholarship-card");
    const resultsCount = document.getElementById("resultsCount");
    const searchEmpty = document.getElementById("searchEmpty");

    let selectedCategory = "all";

    function filterScholarships() {

        const searchTerm = searchInput.value.toLowerCase().trim();
        const selectedStatus = deadlineFilter.value;
        const showExpired = includeExpired.checked;

        let visibleCount = 0;

        cards.forEach(function (card) {

            const searchableText = (
                card.dataset.search || ""
            ).toLowerCase();

            const category = (
                card.dataset.category || ""
            ).toLowerCase();

            const status = (
                card.dataset.status || ""
            ).toLowerCase();

            const matchesSearch =
                searchableText.includes(searchTerm);

            const matchesCategory =
                selectedCategory === "all" ||
                category.includes(selectedCategory) ||
                searchableText.includes(selectedCategory);

            const matchesStatus =
                selectedStatus === "all" ||
                status.includes(selectedStatus);

            const matchesExpired =
                showExpired ||
                !status.includes("closed");

            const visible =
                matchesSearch &&
                matchesCategory &&
                matchesStatus &&
                matchesExpired;

            card.style.display = visible ? "" : "none";

            if (visible) {
                visibleCount++;
            }

        });

        resultsCount.textContent = "(" + visibleCount + ")";

        if (searchEmpty) {

            searchEmpty.style.display =
                cards.length > 0 && visibleCount === 0
                ? "block"
                : "none";

        }

    }

    // SEARCH
    searchInput.addEventListener("input", filterScholarships);

    // STATUS FILTER
    deadlineFilter.addEventListener("change", filterScholarships);

    // EXPIRED SCHOLARSHIPS
    includeExpired.addEventListener("change", filterScholarships);

    // CATEGORY FILTERS
    categoryButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            categoryButtons.forEach(function (pill) {
                pill.classList.remove("active");
            });

            button.classList.add("active");

            selectedCategory = button.dataset.category;

            filterScholarships();

        });

    });

    // INITIAL FILTER
    filterScholarships();

});


