document.addEventListener(
    "DOMContentLoaded",
    function () {

        // ------------------------------------------------
        // ELEMENTS
        // ------------------------------------------------

        const body =
            document.body;


        const adminToggle =
            document.getElementById(
                "admin-toggle"
            );


        const newCardButton =
            document.getElementById(
                "new-card-button"
            );


        const modal =
            document.getElementById(
                "card-modal"
            );


        const modalTitle =
            document.getElementById(
                "modal-title"
            );


        const modalClose =
            document.getElementById(
                "modal-close"
            );


        const modalCancel =
            document.getElementById(
                "modal-cancel"
            );


        const form =
            document.getElementById(
                "card-form"
            );


        const appId =
            document.getElementById(
                "app-id"
            );


        const title =
            document.getElementById(
                "card-title"
            );


        const slug =
            document.getElementById(
                "card-slug"
            );


        const description =
            document.getElementById(
                "card-description"
            );


        const url =
            document.getElementById(
                "card-url"
            );


        const urlHelp =
            document.getElementById(
                "url-help"
            );


        const badge =
            document.getElementById(
                "card-badge"
            );


        const thumbnailLabel =
            document.getElementById(
                "thumbnail-label"
            );


        const tags =
            document.getElementById(
                "card-tags"
            );


        const theme =
            document.getElementById(
                "card-theme"
            );


        const order =
            document.getElementById(
                "card-order"
            );


        const image =
            document.getElementById(
                "card-image"
            );


        const imageAlt =
            document.getElementById(
                "image-alt"
            );


        const imagePreviewWrapper =
            document.getElementById(
                "image-preview-wrapper"
            );


        const imagePreview =
            document.getElementById(
                "image-preview"
            );


        const removeImageWrapper =
            document.getElementById(
                "remove-image-wrapper"
            );


        const removeImage =
            document.getElementById(
                "remove-image"
            );


        const appsData =
            document.getElementById(
                "apps-data"
            );


        // ------------------------------------------------
        // APP DATA
        // ------------------------------------------------

        const apps =
            JSON.parse(
                appsData.textContent
            );


        const appsById =
            new Map(
                apps.map(
                    function (app) {

                        return [
                            app.id,
                            app
                        ];

                    }
                )
            );


        let existingImage = null;

        let previewUrl = null;

        let editingExistingApp = false;


        // ------------------------------------------------
        // SLUGIFY
        // ------------------------------------------------

        function slugify(value) {

            return value
                .normalize("NFD")
                .replace(
                    /[\u0300-\u036f]/g,
                    ""
                )
                .toLowerCase()
                .replace(
                    /[^a-z0-9]+/g,
                    "-"
                )
                .replace(
                    /^-+|-+$/g,
                    ""
                );

        }


        // ------------------------------------------------
        // ADMIN MODE
        // ------------------------------------------------

        function setAdminMode(enabled) {

            body.classList.toggle(
                "admin-mode",
                enabled
            );


            adminToggle.textContent =
                enabled
                    ? "✓ Klar"
                    : "✎ Redigera";


            sessionStorage.setItem(
                "portal-admin-mode",
                enabled
                    ? "true"
                    : "false"
            );

        }


        const savedAdminMode =
            sessionStorage.getItem(
                "portal-admin-mode"
            ) === "true";


        setAdminMode(
            savedAdminMode
        );


        adminToggle.addEventListener(
            "click",
            function () {

                const enabled =
                    !body.classList.contains(
                        "admin-mode"
                    );


                setAdminMode(
                    enabled
                );

            }
        );


        // ------------------------------------------------
        // STOP APP NAVIGATION IN ADMIN MODE
        // ------------------------------------------------

        document
            .querySelectorAll(
                ".app-card"
            )
            .forEach(
                function (card) {

                    card.addEventListener(
                        "click",
                        function (event) {

                            if (
                                body.classList.contains(
                                    "admin-mode"
                                )
                            ) {

                                event.preventDefault();

                            }

                        }
                    );

                }
            );


        // ------------------------------------------------
        // IMAGE PREVIEW
        // ------------------------------------------------

        function clearPreview() {

            if (previewUrl) {

                URL.revokeObjectURL(
                    previewUrl
                );

                previewUrl = null;

            }


            imagePreview.removeAttribute(
                "src"
            );


            imagePreviewWrapper.hidden =
                true;

        }


        function showExistingImage(
            imageUrl
        ) {

            clearPreview();


            if (!imageUrl) {
                return;
            }


            imagePreview.src =
                imageUrl;


            imagePreviewWrapper.hidden =
                false;

        }


        // ------------------------------------------------
        // OPEN MODAL
        // ------------------------------------------------

        function openModal(
            app = null
        ) {

            form.reset();

            clearPreview();


            existingImage = null;

            editingExistingApp =
                app !== null;


            // --------------------------------------------
            // EDIT EXISTING APP
            // --------------------------------------------

            if (app) {

                modalTitle.textContent =
                    "Redigera kort";


                appId.value =
                    app.id || "";


                title.value =
                    app.title || "";


                slug.value =
                    app.id || "";


                slug.disabled =
                    true;


                description.value =
                    app.description || "";


                url.value =
                    app.url || "";


                badge.value =
                    app.badge || "";


                thumbnailLabel.value =
                    app.thumbnail_label || "";


                tags.value =
                    (
                        app.tags || []
                    ).join(", ");


                theme.value =
                    app.theme || "generic";


                order.value =
                    app.order || "";


                imageAlt.value =
                    app.image_alt || "";


                existingImage =
                    app.image || null;


                removeImage.checked =
                    false;


                if (
                    app.generated
                ) {

                    url.readOnly =
                        true;


                    urlHelp.textContent =
                        "Den här appens länk skapas automatiskt från dess slug.";

                } else {

                    url.readOnly =
                        false;


                    urlHelp.textContent =
                        "Den här specialappen använder en egen FastAPI-route.";

                }


                if (existingImage) {

                    showExistingImage(
                        existingImage
                    );


                    removeImageWrapper.hidden =
                        false;

                } else {

                    removeImageWrapper.hidden =
                        true;

                }

            }


            // --------------------------------------------
            // NEW APP
            // --------------------------------------------

            else {

                modalTitle.textContent =
                    "Skapa ny app";


                appId.value =
                    "";


                title.value =
                    "";


                slug.value =
                    "";


                slug.disabled =
                    false;


                description.value =
                    "";


                url.value =
                    "";


                url.readOnly =
                    true;


                urlHelp.textContent =
                    "Länken skapas automatiskt från appens slug.";


                badge.value =
                    "";


                thumbnailLabel.value =
                    "";


                tags.value =
                    "";


                theme.value =
                    "generic";


                order.value =
                    apps.length + 1;


                imageAlt.value =
                    "";


                removeImage.checked =
                    false;


                removeImageWrapper.hidden =
                    true;

            }


            modal.hidden =
                false;


            body.classList.add(
                "modal-open"
            );


            window.setTimeout(
                function () {

                    title.focus();

                },
                0
            );

        }


        // ------------------------------------------------
        // CLOSE MODAL
        // ------------------------------------------------

        function closeModal() {

            modal.hidden =
                true;


            body.classList.remove(
                "modal-open"
            );


            clearPreview();

        }


        // ------------------------------------------------
        // AUTO SLUG + URL FOR NEW APP
        // ------------------------------------------------

        function updateGeneratedUrlPreview() {

            if (editingExistingApp) {
                return;
            }


            let currentSlug =
                slug.value.trim();


            if (!currentSlug) {

                currentSlug =
                    slugify(
                        title.value
                    );

            }


            if (currentSlug) {

                url.value =
                    "/apps/"
                    + slugify(
                        currentSlug
                    );

            } else {

                url.value =
                    "";

            }

        }


        title.addEventListener(
            "input",
            function () {

                if (
                    !editingExistingApp
                    && !slug.value.trim()
                ) {

                    updateGeneratedUrlPreview();

                }

            }
        );


        slug.addEventListener(
            "input",
            function () {

                updateGeneratedUrlPreview();

            }
        );


        // ------------------------------------------------
        // EDIT BUTTONS
        // ------------------------------------------------

        document
            .querySelectorAll(
                ".card-edit-button"
            )
            .forEach(
                function (button) {

                    button.addEventListener(
                        "click",
                        function () {

                            const app =
                                appsById.get(
                                    button.dataset.appId
                                );


                            if (app) {

                                openModal(
                                    app
                                );

                            }

                        }
                    );

                }
            );


        // ------------------------------------------------
        // NEW APP BUTTON
        // ------------------------------------------------

        newCardButton.addEventListener(
            "click",
            function () {

                openModal();

            }
        );


        // ------------------------------------------------
        // CLOSE BUTTONS
        // ------------------------------------------------

        modalClose.addEventListener(
            "click",
            closeModal
        );


        modalCancel.addEventListener(
            "click",
            closeModal
        );


        // ------------------------------------------------
        // CLICK OUTSIDE MODAL
        // ------------------------------------------------

        modal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === modal
                ) {

                    closeModal();

                }

            }
        );


        // ------------------------------------------------
        // ESC
        // ------------------------------------------------

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                    && !modal.hidden
                ) {

                    closeModal();

                }

            }
        );


        // ------------------------------------------------
        // NEW IMAGE PREVIEW
        // ------------------------------------------------

        image.addEventListener(
            "change",
            function () {

                const file =
                    image.files[0];


                if (!file) {

                    showExistingImage(
                        existingImage
                    );

                    return;

                }


                clearPreview();


                previewUrl =
                    URL.createObjectURL(
                        file
                    );


                imagePreview.src =
                    previewUrl;


                imagePreviewWrapper.hidden =
                    false;


                removeImage.checked =
                    false;

            }
        );


        // ------------------------------------------------
        // REMOVE IMAGE
        // ------------------------------------------------

        removeImage.addEventListener(
            "change",
            function () {

                if (
                    removeImage.checked
                ) {

                    clearPreview();

                } else {

                    showExistingImage(
                        existingImage
                    );

                }

            }
        );

    }
);