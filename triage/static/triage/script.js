// Live AI risk preview: as the user types their request, we debounce and
// call the Django JSON API (/api/classify-preview/) which runs the same
// ML model used on final submission, so the user gets instant feedback.

(function () {
    const textArea = document.getElementById("id_request_text");
    const resultBox = document.getElementById("preview-result");
    if (!textArea || !resultBox) return;

    let debounceTimer = null;

    const badgeClass = {
        low: "badge-low",
        medium: "badge-medium",
        high: "badge-high",
    };

    function renderResult(data) {
        const risk = data.risk_level;
        const confidencePct = Math.round(data.confidence * 100);
        const sourceText = data.source === "rule_override"
            ? `Flagged by security rule (matched: "${data.matched_keyword}")`
            : "Assessed by ML model";

        resultBox.innerHTML = `
            <span class="badge ${badgeClass[risk] || ''}">${risk.toUpperCase()} RISK</span>
            <p class="muted" style="margin-top:10px;">Confidence: ${confidencePct}%</p>
            <p class="muted">${sourceText}</p>
            <p class="muted">Recommended approver: ${data.recommended_approver}</p>
        `;
    }

    function renderWaiting(message) {
        resultBox.innerHTML = `<span class="muted">${message}</span>`;
    }

    textArea.addEventListener("input", function () {
        const text = textArea.value.trim();
        clearTimeout(debounceTimer);

        if (text.length < 8) {
            renderWaiting("Keep typing… (need at least a short sentence)");
            return;
        }

        renderWaiting("Thinking…");

        debounceTimer = setTimeout(function () {
            fetch("/api/classify-preview/?text=" + encodeURIComponent(text))
                .then((res) => {
                    if (!res.ok) throw new Error("bad response");
                    return res.json();
                })
                .then(renderResult)
                .catch(() => renderWaiting("Couldn't reach the AI model. Try again."));
        }, 500);
    });
})();
