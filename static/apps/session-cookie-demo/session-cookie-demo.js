document.addEventListener(
    "DOMContentLoaded",
    function () {

        // ------------------------------------------------
        // ELEMENTS
        // ------------------------------------------------

        const status =
            document.getElementById(
                "session-status"
            );


        const protocolValue =
            document.getElementById(
                "protocol-value"
            );


        const secureValue =
            document.getElementById(
                "secure-value"
            );


        const sessionId =
            document.getElementById(
                "session-id"
            );


        const documentCookie =
            document.getElementById(
                "document-cookie"
            );


        const stateOutput =
            document.getElementById(
                "state-output"
            );


        const choiceResult =
            document.getElementById(
                "choice-result"
            );


        const answerResult =
            document.getElementById(
                "answer-result"
            );


        // ------------------------------------------------
        // PROTOCOL
        // ------------------------------------------------

        protocolValue.textContent =
            window.location.protocol;


        // ------------------------------------------------
        // API HELPER
        // ------------------------------------------------

        async function api(
            path,
            options = {}
        ) {

            const response =
                await fetch(
                    "/api/session-demo" + path,
                    {
                        credentials:
                            "same-origin",

                        headers: {
                            "Content-Type":
                                "application/json",

                            ...options.headers
                        },

                        ...options
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail
                    || "Något gick fel."
                );

            }


            return data;

        }


        // ------------------------------------------------
        // JSON SYNTAX HIGHLIGHTING
        // ------------------------------------------------

        function escapeHtml(text) {

            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");

        }


        function highlightJson(json) {

            json = escapeHtml(json);


            return json.replace(
                /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\btrue\b|\bfalse\b|\bnull\b|-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?|[{}[\]])/g,

                function (match) {

                    let cssClass =
                        "json-number";


                    if (/^"/.test(match)) {

                        if (/:$/.test(match)) {

                            cssClass =
                                "json-key";

                        } else {

                            cssClass =
                                "json-string";

                        }

                    } else if (/true|false/.test(match)) {

                        cssClass =
                            "json-boolean";

                    } else if (/null/.test(match)) {

                        cssClass =
                            "json-null";

                    } else if (/^[\{\}\[\]]$/.test(match)) {

                        cssClass =
                            "json-brace";

                    }


                    return (
                        '<span class="'
                        + cssClass
                        + '">'
                        + match
                        + "</span>"
                    );

                }
            );

        }


        function showJson(data) {

            const formattedJson =
                JSON.stringify(
                    data,
                    null,
                    4
                );


            stateOutput.innerHTML =
                highlightJson(
                    formattedJson
                );

        }


        // ------------------------------------------------
        // REFRESH STATE
        // ------------------------------------------------

        async function refreshState() {

            try {

                const data =
                    await api(
                        "/state"
                    );


                documentCookie.textContent =
                    document.cookie
                    || "(sessionscookien syns inte här)";


                // ----------------------------------------
                // NO ACTIVE SESSION
                // ----------------------------------------

                if (!data.active) {

                    status.textContent =
                        "Ingen aktiv session";


                    status.className =
                        "status-badge inactive";


                    secureValue.textContent =
                        "-";


                    sessionId.textContent =
                        "Ingen";


                    showJson(
                        data
                    );


                    return;

                }


                // ----------------------------------------
                // ACTIVE SESSION
                // ----------------------------------------

                status.textContent =
                    "Session aktiv";


                status.className =
                    "status-badge active";


                secureValue.textContent =
                    data.cookie.secure
                        ? "True"
                        : "False";


                sessionId.textContent =
                    data.session_id_preview;


                showJson(
                    data
                );


            } catch (error) {

                stateOutput.textContent =
                    error.message;

            }

        }


        // ------------------------------------------------
        // START SESSION
        // ------------------------------------------------

        async function startSession(
            secure
        ) {

            choiceResult.textContent =
                "";


            answerResult.hidden =
                true;


            try {

                await api(
                    "/start",
                    {
                        method:
                            "POST",

                        body:
                            JSON.stringify(
                                {
                                    secure:
                                        secure
                                }
                            )
                    }
                );


                await refreshState();


                if (
                    secure
                    && status.classList.contains(
                        "inactive"
                    )
                ) {

                    stateOutput.textContent =
                        "Servern försökte sätta cookien med Secure=True, "
                        + "men webbläsaren skickade inte tillbaka den på "
                        + "den lokala HTTP-anslutningen. "
                        + "Detta är det förväntade beteendet vi vill visa.";

                }


            } catch (error) {

                stateOutput.textContent =
                    error.message;

            }

        }


        // ------------------------------------------------
        // LOCAL SESSION
        // ------------------------------------------------

        document
            .getElementById(
                "start-local"
            )
            .addEventListener(
                "click",
                function () {

                    startSession(
                        false
                    );

                }
            );


        // ------------------------------------------------
        // SECURE SESSION
        // ------------------------------------------------

        document
            .getElementById(
                "start-secure"
            )
            .addEventListener(
                "click",
                function () {

                    startSession(
                        true
                    );

                }
            );


        // ------------------------------------------------
        // CHOOSE DOOR
        // ------------------------------------------------

        document
            .querySelectorAll(
                ".door-button"
            )
            .forEach(
                function (button) {

                    button.addEventListener(
                        "click",
                        async function () {

                            try {

                                const data =
                                    await api(
                                        "/choose",
                                        {
                                            method:
                                                "POST",

                                            body:
                                                JSON.stringify(
                                                    {
                                                        choice:
                                                            button.dataset.choice
                                                    }
                                                )
                                        }
                                    );


                                choiceResult.textContent =
                                    data.message;


                                await refreshState();


                            } catch (error) {

                                choiceResult.textContent =
                                    error.message;

                            }

                        }
                    );

                }
            );


        // ------------------------------------------------
        // ANSWER
        // ------------------------------------------------

        document
            .querySelectorAll(
                ".answer-button"
            )
            .forEach(
                function (button) {

                    button.addEventListener(
                        "click",
                        async function () {

                            try {

                                const data =
                                    await api(
                                        "/answer",
                                        {
                                            method:
                                                "POST",

                                            body:
                                                JSON.stringify(
                                                    {
                                                        answer:
                                                            button.dataset.answer
                                                    }
                                                )
                                        }
                                    );


                                answerResult.hidden =
                                    false;


                                answerResult.textContent =
                                    data.message;


                                answerResult.className =
                                    (
                                        "answer-result "
                                        + (
                                            data.correct
                                                ? "correct"
                                                : "incorrect"
                                        )
                                    );


                                await refreshState();


                            } catch (error) {

                                answerResult.hidden =
                                    false;


                                answerResult.textContent =
                                    error.message;


                                answerResult.className =
                                    "answer-result incorrect";

                            }

                        }
                    );

                }
            );


        // ------------------------------------------------
        // REFRESH
        // ------------------------------------------------

        document
            .getElementById(
                "refresh-state"
            )
            .addEventListener(
                "click",
                refreshState
            );


        // ------------------------------------------------
        // RESET
        // ------------------------------------------------

        document
            .getElementById(
                "reset-session"
            )
            .addEventListener(
                "click",
                async function () {

                    await api(
                        "/reset",
                        {
                            method:
                                "POST",

                            body:
                                JSON.stringify(
                                    {}
                                )
                        }
                    );


                    choiceResult.textContent =
                        "";


                    answerResult.hidden =
                        true;


                    await refreshState();

                }
            );


        // ------------------------------------------------
        // INITIAL STATE
        // ------------------------------------------------

        refreshState();

    }
);