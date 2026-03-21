const API_BASE = "http://localhost:8000";

// ─── DOM refs ────────────────────────────────────────────────
const fileInput         = document.getElementById("fileInput");
const uploadZone        = document.getElementById("uploadZone");
const fileSelected      = document.getElementById("fileSelected");
const fileName          = document.getElementById("fileName");
const fileSize          = document.getElementById("fileSize");
const fileRemove        = document.getElementById("fileRemove");
const analyzeBtn        = document.getElementById("analyzeBtn");
const loadingOverlay    = document.getElementById("loadingOverlay");
const resultsSection    = document.getElementById("resultsSection");
const uploadSection     = document.querySelector(".upload-section");
const heroSection       = document.querySelector(".hero");
const newAnalysisBtn    = document.getElementById("newAnalysisBtn");
const errorToast        = document.getElementById("errorToast");
const errorMessage      = document.getElementById("errorMessage");
const errorClose        = document.getElementById("errorClose");

let selectedFile = null;
let stepInterval = null;

// ─── Drag & Drop ─────────────────────────────────────────────
uploadZone.addEventListener("dragover", e => {
  e.preventDefault();
  uploadZone.classList.add("dragover");
});

uploadZone.addEventListener("dragleave", () => {
  uploadZone.classList.remove("dragover");
});

uploadZone.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelect(file);
});

uploadZone.addEventListener("click", (e) => {
  if (e.target === uploadZone || e.target.closest(".upload-icon-wrap") || e.target.closest(".upload-text") || e.target.closest(".upload-formats")) {
    if (!e.target.classList.contains("upload-link")) {
      fileInput.click();
    }
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
});

fileRemove.addEventListener("click", resetUpload);
newAnalysisBtn.addEventListener("click", resetAll);
errorClose.addEventListener("click", hideError);

analyzeBtn.addEventListener("click", runAnalysis);

// ─── File handling ────────────────────────────────────────────
function handleFileSelect(file) {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showError("Please upload a file in PDF format.");
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    showError("File is too large. Maximum size is 20 MB.");
    return;
  }

  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);

  uploadZone.classList.add("hidden");
  fileSelected.classList.remove("hidden");
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

function resetUpload() {
  selectedFile = null;
  fileInput.value = "";
  uploadZone.classList.remove("hidden");
  fileSelected.classList.add("hidden");
}

function resetAll() {
  resetUpload();
  resultsSection.classList.add("hidden");
  document.querySelector(".upload-section").classList.remove("hidden");
  heroSection.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ─── Analysis ─────────────────────────────────────────────────
async function runAnalysis() {
  if (!selectedFile) return;

  showLoading();

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      body: formData,
    });

    const json = await response.json();

    if (!response.ok) {
      throw new Error(json.detail || `Server error: ${response.status}`);
    }

    if (!json.success || !json.data) {
      throw new Error("Invalid response from server");
    }

    hideLoading();
    renderResults(json.data, json.filename);

  } catch (err) {
    hideLoading();
    let msg = err.message || "Unknown error";
    if (msg.includes("fetch") || msg.includes("NetworkError") || msg.includes("Failed to fetch")) {
      msg = "Could not connect to the server. Make sure the backend is running on port 8000.";
    }
    showError(msg);
  }
}

// ─── Loading Steps Animation ───────────────────────────────────
function showLoading() {
  loadingOverlay.classList.remove("hidden");
  document.querySelector(".upload-section").classList.add("hidden");
  heroSection.classList.add("hidden");

  const steps = [
    document.getElementById("step1"),
    document.getElementById("step2"),
    document.getElementById("step3"),
  ];

  steps.forEach(s => { s.classList.remove("active", "done"); });
  steps[0].classList.add("active");

  let current = 0;
  stepInterval = setInterval(() => {
    if (current < steps.length - 1) {
      steps[current].classList.remove("active");
      steps[current].classList.add("done");
      current++;
      steps[current].classList.add("active");
    }
  }, 4000);
}

function hideLoading() {
  clearInterval(stepInterval);
  loadingOverlay.classList.add("hidden");
}

// ─── Render Results ────────────────────────────────────────────
function renderResults(data, filename) {
  // Header
  const riskLevel = (data.risk_level || "medium").toLowerCase();
  const riskBadge = document.getElementById("resultBadge");
  const riskLabels = {
    low:      "Low Risk",
    medium:   "Medium Risk",
    high:     "High Risk",
    critical: "Critical Risk",
  };
  riskBadge.className = `result-badge risk-${riskLevel}`;
  document.getElementById("riskText").textContent = riskLabels[riskLevel] || "Medium Risk";
  document.getElementById("docType").textContent = data.document_type || "Financial Document";
  document.getElementById("resultFilename").textContent = filename || "document";

  // Summary
  setText("documentSummary", data.document_summary);

  // Risk explanation
  const riskCard = document.getElementById("riskExplanationCard");
  if (data.risk_explanation) {
    riskCard.className = `risk-explanation-card risk-${riskLevel}`;
    setText("riskExplanation", data.risk_explanation);
    riskCard.classList.remove("hidden");
  } else {
    riskCard.classList.add("hidden");
  }

  // Key conditions
  renderKeyConditions(data.key_conditions || []);

  // Hidden fees
  renderItems("hiddenFeesList", "feesCount", data.hidden_fees || [], true);

  // Penalties
  renderItems("penaltiesList", "penaltiesCount", data.penalties || [], true);

  // Dangerous clauses
  renderItems("dangerousClausesList", "clausesCount", data.dangerous_clauses || [], false, true);

  // Red flags
  renderRedFlags(data.red_flags || []);

  // Recommendations
  renderRecommendations(data.recommendations || []);

  // Verdict
  setText("overallVerdict", data.overall_verdict);

  // Show section
  resultsSection.classList.remove("hidden");
  setTimeout(() => resultsSection.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text || "—";
}

function renderKeyConditions(conditions) {
  const grid = document.getElementById("keyConditionsGrid");
  const block = document.getElementById("keyConditionsBlock");
  grid.innerHTML = "";

  if (!conditions.length) {
    block.classList.add("hidden");
    return;
  }

  block.classList.remove("hidden");
  conditions.forEach(c => {
    const div = document.createElement("div");
    div.className = "condition-item";
    div.innerHTML = `
      <div class="condition-label">${escHtml(c.label || "")}</div>
      <div class="condition-value">${escHtml(c.value || "—")}</div>
    `;
    grid.appendChild(div);
  });
}

function renderItems(listId, countId, items, showAmount = false, showRec = false) {
  const list = document.getElementById(listId);
  const countEl = document.getElementById(countId);
  list.innerHTML = "";

  if (countEl) countEl.textContent = items.length;

  if (!items.length) {
    list.innerHTML = '<div class="empty-state">None detected</div>';
    return;
  }

  items.forEach(item => {
    const sev = (item.severity || "medium").toLowerCase();
    const sevLabels = { low: "Low", medium: "Medium", high: "High", critical: "Critical" };

    const card = document.createElement("div");
    card.className = `item-card sev-${sev}`;

    let amountHtml = "";
    if (showAmount && item.amount) {
      amountHtml = `<span class="item-amount">${escHtml(item.amount)}</span>`;
    }

    let recHtml = "";
    if (showRec && item.recommendation) {
      recHtml = `<div class="item-recommendation">${escHtml(item.recommendation)}</div>`;
    }

    card.innerHTML = `
      <div class="item-header">
        <span class="item-title">${escHtml(item.title || "")}</span>
        ${amountHtml}
        <span class="severity-badge">${sevLabels[sev] || "Medium"}</span>
      </div>
      <p class="item-desc">${escHtml(item.description || "")}</p>
      ${recHtml}
    `;
    list.appendChild(card);
  });
}

function renderRedFlags(flags) {
  const list = document.getElementById("redFlagsList");
  const block = document.getElementById("redFlagsBlock");
  list.innerHTML = "";

  if (!flags.length) {
    block.classList.add("hidden");
    return;
  }

  block.classList.remove("hidden");
  flags.forEach(flag => {
    const div = document.createElement("div");
    div.className = "red-flag-item";
    div.innerHTML = `
      <span class="red-flag-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </span>
      ${escHtml(flag)}
    `;
    list.appendChild(div);
  });
}

function renderRecommendations(recs) {
  const list = document.getElementById("recommendationsList");
  const block = document.getElementById("recommendationsBlock");
  list.innerHTML = "";

  if (!recs.length) {
    block.classList.add("hidden");
    return;
  }

  block.classList.remove("hidden");
  recs.forEach((rec, i) => {
    const div = document.createElement("div");
    div.className = "recommendation-item";
    div.innerHTML = `
      <span class="rec-number">${i + 1}</span>
      ${escHtml(rec)}
    `;
    list.appendChild(div);
  });
}

// ─── Error handling ────────────────────────────────────────────
function showError(msg) {
  errorMessage.textContent = msg;
  errorToast.classList.remove("hidden");
  setTimeout(hideError, 7000);
}

function hideError() {
  errorToast.classList.add("hidden");
}

// ─── Utils ────────────────────────────────────────────────────
function escHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(String(str)));
  return div.innerHTML;
}
