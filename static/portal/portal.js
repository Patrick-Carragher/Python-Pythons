document.addEventListener("DOMContentLoaded", function () {

    const body = document.body;

    const adminToggle =
        document.getElementById("admin-toggle");

    const newCardButton =
        document.getElementById("new-card-button");

    const modal =
        document.getElementById("card-modal");

    const modalTitle =
        document.getElementById("modal-title");

    const modalClose =
        document.getElementById("modal-close");

    const modalCancel =
        document.getElementById("modal-cancel");

    const form =
        document.getElementById("card-form");

    const appId =
        document.getElementById("app-id");

    const title =
        document.getElementById("card-title");

    const description =
        document.getElementById("card-description");

    const url =
        document.getElementById("card-url");

    const badge =
        document.getElementById("card-badge");

    const thumbnailLabel =
        document.getElementById("thumbnail-label");

    const tags =
        document.getElementById("card-tags");

    const theme =
        document.getElementById("card-theme");

    const order =
        document.getElementById("card-order");

    const image =
        document.getElementById("card-image");

    const imageAlt =
        document.getElementById("image-alt");

    const imagePreviewWrapper =
        document.getElementById("image-preview-wrapper");

    const imagePreview =
        document.getElementById("image-preview");

    const removeImageWrapper =
        document.getElementById("remove-image-wrapper");

    const removeImage =
        document.getElementById("remove-image");

    const appsData =
        document.getElementById("apps-data");


    const apps =
        JSON.parse(appsData.textContent);


    const appsById =
        new Map(
            apps.map(function (app) {
                return [app.id, app];
            })
        );


    let existingImage = null;
    let previewUrl = null;


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
            enabled ? "true" : "false"
        );

    }


    const savedAdminMode =
        sessionStorage.getItem(
            "portal-admin-mode"
        ) === "true";


    setAdminMode(savedAdminMode);


    adminToggle.addEventListener(
        "click",
        function () {

            setAdminMode(
                !body.classList.contains(
                    "admin-mode"
                )
            );

        }
    );


    function clearPreview() {

        if (previewUrl) {

            URL.revokeObjectURL(
                previewUrl
            );

            previewUrl = null;

        }

        imagePreview.removeAttribute("src");

        imagePreviewWrapper.hidden = true;

    }


    function showImage(imageUrl) {

        clearPreview();

        if (!imageUrl) {
            return;
        }

        imagePreview.src = imageUrl;

        imagePreviewWrapper.hidden = false;

    }


    function openModal(app = null) {

        form.reset();

        clearPreview();

        existingImage = null;


        if (app) {

            modalTitle.textContent =
                "Redigera kort";

            appId.value =
                app.id || "";

            title.value =
                app.title || "";

            description.value =
                app.description || "";

            url.value =
                app.url || "";

            badge.value =
                app.badge || "";

            thumbnailLabel.value =
                app.thumbnail_label || "";

            tags.value =
                (app.tags || []).join(", ");

            theme.value =
                app.theme || "generic";

            order.value =
                app.order || "";

            imageAlt.value =
                app.image_alt || "";

            existingImage =
                app.image || null;


            if (existingImage) {

                showImage(
                    existingImage
                );

                removeImageWrapper.hidden =
                    false;

            } else {

                removeImageWrapper.hidden =
                    true;

            }

        } else {

            modalTitle.textContent =
                "Skapa nytt kort";

            appId.value = "";

            theme.value = "generic";

            removeImageWrapper.hidden = true;

        }


        modal.hidden = false;

        body.classList.add(
            "modal-open"
        );

        title.focus();

    }


    function closeModal() {

        modal.hidden = true;

        body.classList.remove(
            "modal-open"
        );

        clearPreview();

    }


    document
        .querySelectorAll(
            ".card-edit-button"
        )
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const app =
                        appsById.get(
                            button.dataset.appId
                        );

                    if (app) {
                        openModal(app);
                    }

                }
            );

        });


    newCardButton.addEventListener(
        "click",
        function () {
            openModal();
        }
    );


    modalClose.addEventListener(
        "click",
        closeModal
    );


    modalCancel.addEventListener(
        "click",
        closeModal
    );


    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {
                closeModal();
            }

        }
    );


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


    image.addEventListener(
        "change",
        function () {

            const file =
                image.files[0];

            if (!file) {

                showImage(
                    existingImage
                );

                return;

            }


            clearPreview();


            previewUrl =
                URL.createObjectURL(file);


            imagePreview.src =
                previewUrl;

            imagePreviewWrapper.hidden =
                false;

            removeImage.checked =
                false;

        }
    );


    removeImage.addEventListener(
        "change",
        function () {

            if (removeImage.checked) {

                clearPreview();

            } else {

                showImage(
                    existingImage
                );

            }

        }
    );

});