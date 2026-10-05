const API_BASE_URL = "http://127.0.0.1:8000";

const organizationInput = document.getElementById("organizationNumber");
const researchButton = document.getElementById("researchButton");
const newResearchButton = document.getElementById("newResearchButton");

const loadingState = document.getElementById("loadingState");
const errorState = document.getElementById("errorState");
const errorMessage = document.getElementById("errorMessage");

const companySection = document.getElementById("companySection");

const companyName = document.getElementById("companyName");
const companyInitial = document.getElementById("companyInitial");
const companyOrgNumber = document.getElementById("companyOrgNumber");
const companyAddress = document.getElementById("companyAddress");

const totalFacts = document.getElementById("totalFacts");
const registryFacts = document.getElementById("registryFacts");
const sourcesChecked = document.getElementById("sourcesChecked");
const researchStatus = document.getElementById("researchStatus");

const factsContainer = document.getElementById("factsContainer");
const sourcesContainer = document.getElementById("sourcesContainer");


function showElement(element) {
    element.classList.remove("hidden");
}


function hideElement(element) {
    element.classList.add("hidden");
}


function setLoading(isLoading) {
    researchButton.disabled = isLoading;

    if (isLoading) {
        researchButton.innerHTML = `
            <span>Researching...</span>
            <span class="button-arrow">↻</span>
        `;

        showElement(loadingState);
    } else {
        researchButton.innerHTML = `
            <span>Research Company</span>
            <span class="button-arrow">→</span>
        `;

        hideElement(loadingState);
    }
}


function showError(message) {
    errorMessage.textContent = message;
    showElement(errorState);
}


function hideError() {
    hideElement(errorState);
}


function resetResults() {
    hideElement(companySection);
    hideError();

    factsContainer.innerHTML = `
        <div class="empty-facts">
            Research a company to see extracted intelligence.
        </div>
    `;

    sourcesContainer.innerHTML = `
        <div class="empty-facts">
            Sources will appear here after research.
        </div>
    `;
}


function normalizeOrganizationNumber(value) {
    return value.replace(/\D/g, "");
}


function isValidOrganizationNumber(value) {
    return /^\d{9}$/.test(value);
}


async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            Accept: "application/json",
            ...(options.headers || {}),
        },
    });

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const message =
            data?.detail ||
            `Request failed with HTTP ${response.status}.`;

        throw new Error(message);
    }

    return data;
}


async function researchCompany(organizationNumber) {
    return requestJson(
        `${API_BASE_URL}/companies/${organizationNumber}/research`,
        {
            method: "POST",
        }
    );
}


async function getCompanyIntelligence(organizationNumber) {
    return requestJson(
        `${API_BASE_URL}/companies/${organizationNumber}/facts`
    );
}


function formatFieldName(fieldName) {
    if (!fieldName) {
        return "Company Fact";
    }

    return fieldName
        .replace(/_/g, " ")
        .replace(/\b\w/g, character => character.toUpperCase());
}


function formatVerificationStatus(status) {
    if (!status) {
        return "Verified";
    }

    return status
        .replace(/_/g, " ")
        .replace(/\b\w/g, character => character.toUpperCase());
}


function formatConfidence(confidence) {
    if (confidence === null || confidence === undefined) {
        return null;
    }

    const percentage = Math.round(Number(confidence) * 100);

    if (Number.isNaN(percentage)) {
        return null;
    }

    return `${percentage}% confidence`;
}


function formatDate(dateValue) {
    if (!dateValue) {
        return null;
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return null;
    }

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
    });
}


function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function normalizeUrl(url) {
    if (!url) {
        return "#";
    }

    if (
        url.startsWith("http://") ||
        url.startsWith("https://")
    ) {
        return url;
    }

    return `https://${url}`;
}


function getStatusClass(status) {
    switch ((status || "").toLowerCase()) {
        case "verified":
            return "verified";

        case "review":
            return "review";

        case "pending":
            return "pending";

        case "rejected":
            return "rejected";

        default:
            return "pending";
    }
}


function getStatusIcon(status) {
    switch ((status || "").toLowerCase()) {
        case "verified":
            return "✓";

        case "review":
            return "◐";

        case "pending":
            return "○";

        case "rejected":
            return "×";

        default:
            return "○";
    }
}


function getStatusText(status) {
    switch ((status || "").toLowerCase()) {
        case "verified":
            return "Verified";

        case "review":
            return "Needs Review";

        case "pending":
            return "Pending";

        case "rejected":
            return "Rejected";

        default:
            return formatVerificationStatus(status);
    }
}


function renderCompanyHeader(company) {
    const name = company.legal_name || "Unknown Company";

    companyName.textContent = name;

    companyInitial.textContent =
        name.charAt(0).toUpperCase();

    companyOrgNumber.textContent =
        `Org No. ${company.organization_number || "—"}`;

    companyAddress.textContent =
        company.address || "Address unavailable";
}


function renderMetrics(intelligence) {
    const summary = intelligence.summary || {};
    const sources = intelligence.sources || [];

    totalFacts.textContent =
        summary.total_facts ?? 0;

    registryFacts.textContent =
        summary.registry_facts ?? 0;

    sourcesChecked.textContent =
        sources.length;

    const verifiedFacts =
        summary.verified_facts || 0;

    const reviewFacts =
        summary.review_facts || 0;

    const pendingFacts =
        summary.pending_facts || 0;

    if (summary.total_facts === 0) {
        researchStatus.textContent = "No Data";
    } else if (reviewFacts > 0 || pendingFacts > 0) {
        researchStatus.textContent = "Review";
    } else if (verifiedFacts > 0) {
        researchStatus.textContent = "Verified";
    } else {
        researchStatus.textContent = "Complete";
    }
}


function createFactCard(fact) {
    const card = document.createElement("div");

    card.className = "fact-card";

    const fieldName =
        formatFieldName(fact.field_name);

    const value =
        fact.value || "Unavailable";

    const evidence =
        fact.evidence_text ||
        "No evidence text available.";

    const status =
        fact.verification_status || "pending";

    const confidence =
        formatConfidence(fact.confidence);

    const sourceUrl =
        fact.source?.url || null;

    const retrievedAt =
        formatDate(fact.source?.retrieved_at);

    const statusClass =
        getStatusClass(status);

    const statusIcon =
        getStatusIcon(status);

    const statusText =
        getStatusText(status);

    const sourceHtml = sourceUrl
        ? `
            <a
                class="fact-source"
                href="${escapeHtml(normalizeUrl(sourceUrl))}"
                target="_blank"
                rel="noopener noreferrer"
            >
                View source ↗
            </a>
        `
        : "";

    const metadata = [];

    if (confidence) {
        metadata.push(confidence);
    }

    if (retrievedAt) {
        metadata.push(`Retrieved ${retrievedAt}`);
    }

    card.innerHTML = `
        <div class="fact-field">
            ${escapeHtml(fieldName)}
        </div>

        <div class="fact-value">
            ${escapeHtml(value)}
        </div>

        <div class="fact-evidence">
            ${escapeHtml(evidence)}
        </div>

        <div class="fact-bottom">
            <div class="fact-status ${statusClass}">
                <span>${statusIcon}</span>
                ${escapeHtml(statusText)}
            </div>

            <div class="fact-metadata">
                ${metadata
                    .map(item => escapeHtml(item))
                    .join(" · ")}
            </div>
        </div>

        ${sourceHtml}
    `;

    return card;
}


function deduplicateFacts(facts) {
    const factMap = new Map();

    for (const fact of facts) {
        const key = [
            fact.field_name,
            fact.value,
            fact.source?.url || "",
        ]
            .join("|")
            .toLowerCase();

        const existing = factMap.get(key);

        if (!existing) {
            factMap.set(key, fact);
            continue;
        }

        const existingConfidence =
            Number(existing.confidence || 0);

        const currentConfidence =
            Number(fact.confidence || 0);

        if (currentConfidence > existingConfidence) {
            factMap.set(key, fact);
        }
    }

    return Array.from(factMap.values());
}


function sortFacts(facts) {
    const priority = {
        verified: 0,
        review: 1,
        pending: 2,
        rejected: 3,
    };

    return [...facts].sort((a, b) => {
        const statusA =
            priority[(a.verification_status || "").toLowerCase()] ?? 4;

        const statusB =
            priority[(b.verification_status || "").toLowerCase()] ?? 4;

        if (statusA !== statusB) {
            return statusA - statusB;
        }

        return String(a.field_name || "")
            .localeCompare(String(b.field_name || ""));
    });
}


function renderFacts(intelligence) {
    factsContainer.innerHTML = "";

    const facts =
        deduplicateFacts(intelligence.facts || []);

    const sortedFacts =
        sortFacts(facts);

    if (!sortedFacts.length) {
        factsContainer.innerHTML = `
            <div class="empty-facts">
                No extracted facts are available yet.
            </div>
        `;

        return;
    }

    sortedFacts.forEach(fact => {
        factsContainer.appendChild(
            createFactCard(fact)
        );
    });
}


function createSourceCard(source) {
    const card = document.createElement("div");

    card.className = "source-card";

    const factCount =
        source.fact_count || 0;

    const sourceType =
        formatFieldName(source.source_type);

    const retrievedAt =
        formatDate(source.retrieved_at);

    const sourceUrl =
        normalizeUrl(source.url);

    card.innerHTML = `
        <div class="source-top">
            <div class="source-type">
                ${escapeHtml(sourceType)}
            </div>

            <div class="source-status success">
                AVAILABLE
            </div>
        </div>

        <a
            class="source-url"
            href="${escapeHtml(sourceUrl)}"
            target="_blank"
            rel="noopener noreferrer"
        >
            ${escapeHtml(source.url)}
        </a>

        <div class="source-facts">
            ${factCount}
            ${factCount === 1 ? "fact" : "facts"} linked
            ${retrievedAt ? ` · Retrieved ${escapeHtml(retrievedAt)}` : ""}
        </div>
    `;

    return card;
}


function renderSources(intelligence) {
    sourcesContainer.innerHTML = "";

    const sources =
        intelligence.sources || [];

    if (!sources.length) {
        sourcesContainer.innerHTML = `
            <div class="empty-facts">
                No public sources were discovered.
            </div>
        `;

        return;
    }

    sources.forEach(source => {
        sourcesContainer.appendChild(
            createSourceCard(source)
        );
    });
}


function renderResearchResult(intelligence) {
    const company =
        intelligence.company || {};

    renderCompanyHeader(company);
    renderMetrics(intelligence);
    renderFacts(intelligence);
    renderSources(intelligence);

    showElement(companySection);

    companySection.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}


async function handleResearch() {
    hideError();

    const organizationNumber =
        normalizeOrganizationNumber(
            organizationInput.value
        );

    organizationInput.value =
        organizationNumber;

    if (!isValidOrganizationNumber(organizationNumber)) {
        showError(
            "Please enter a valid 9-digit Norwegian organization number."
        );

        return;
    }

    resetResults();

    setLoading(true);

    try {
        /*
         * First run the research pipeline.
         * This updates the company profile and gathers
         * the latest available evidence.
         */
        await researchCompany(
            organizationNumber
        );

        /*
         * Then fetch the actual stored intelligence.
         * This gives the frontend access to:
         * - facts
         * - evidence
         * - confidence
         * - verification status
         * - source metadata
         */
        const intelligence =
            await getCompanyIntelligence(
                organizationNumber
            );

        renderResearchResult(
            intelligence
        );
    } catch (error) {
        console.error(
            "Signalpost research error:",
            error
        );

        showError(
            error.message ||
            "Unable to research this company."
        );
    } finally {
        setLoading(false);
    }
}


function handleNewResearch() {
    organizationInput.value = "";

    resetResults();

    organizationInput.focus();

    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });
}


researchButton.addEventListener(
    "click",
    handleResearch
);


newResearchButton.addEventListener(
    "click",
    handleNewResearch
);


organizationInput.addEventListener(
    "keydown",
    event => {
        if (event.key === "Enter") {
            handleResearch();
        }
    }
);


organizationInput.addEventListener(
    "input",
    () => {
        organizationInput.value =
            organizationInput.value
                .replace(/\D/g, "")
                .slice(0, 9);
    }
);