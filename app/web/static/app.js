/* ============================================
   PostgreSQL Assistant — Main Page Logic
   ============================================ */

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const form = $("#ask-form");
const questionEl = $("#question");
const versionEl = $("#pg-version");
const modeEl = $("#mode");
const extendedEl = $("#extended-mode");
const extendedLabel = $("#extended-label");
const extendedGroup = $("#extended-group");
const extendedHint = $("#extended-hint");
const submitBtn = $("#submit-btn");
const errorBox = $("#error-box");

const loadingPanel = $("#loading-panel");
const clarificationPanel = $("#clarification-panel");
const clarificationQuestion = $("#clarification-question");
const clarificationInput = $("#clarification-input");
const clarificationBtn = $("#clarification-btn");

const resultPanel = $("#result-panel");
const resultBadge = $("#result-badge");
const resultVersion = $("#result-version");
const resultExtended = $("#result-extended");
const answerBlock = $("#answer-block");
const answerText = $("#answer-text");
const tutorialBlock = $("#tutorial-block");
const tutorialSummary = $("#tutorial-summary");
const tutorialPrereq = $("#tutorial-prereq");
const tutorialSteps = $("#tutorial-steps");
const tutorialVerification = $("#tutorial-verification");
const tutorialTroubleshooting = $("#tutorial-troubleshooting");
const tutorialNotes = $("#tutorial-notes");
const tutorialNextSteps = $("#tutorial-next-steps");
const sourcesSection = $("#sources-section");
const sourcesEl = $("#sources");

// State
let pendingRequest = null;

// ---- Helpers ----

function setError(msg) {
  if (!msg) {
    errorBox.hidden = true;
    errorBox.textContent = "";
    return;
  }
  errorBox.hidden = false;
  errorBox.textContent = msg;
}

function setLoading(on) {
  submitBtn.disabled = on;
  if (on) {
    submitBtn.classList.add("is-loading");
  } else {
    submitBtn.classList.remove("is-loading");
  }
  loadingPanel.hidden = !on;
  if (on) {
    resultPanel.hidden = true;
    clarificationPanel.hidden = true;
  }
}

function updateExtendedState() {
  const isTutorial = modeEl.value === "tutorial";
  extendedEl.disabled = !isTutorial;
  extendedEl.setAttribute("aria-disabled", String(!isTutorial));
  if (!isTutorial) {
    extendedEl.checked = false;
    extendedLabel.classList.add("disabled");
    extendedGroup.classList.add("is-disabled");
    extendedHint.hidden = false;
  } else {
    extendedLabel.classList.remove("disabled");
    extendedGroup.classList.remove("is-disabled");
    extendedHint.hidden = true;
  }
}

function renderList(target, items) {
  target.innerHTML = "";
  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    target.appendChild(li);
  });
}

function showSection(sectionId, items) {
  const section = $(sectionId);
  if (!section) return;
  if (items && items.length > 0) {
    section.hidden = false;
  } else {
    section.hidden = true;
  }
}

// ---- Mode labels for user ----

const MODE_LABELS = {
  answer: "Краткий ответ",
  tutorial: "Обучающий режим",
};

// ---- Render Sources ----

function renderSources(sources) {
  sourcesEl.innerHTML = "";
  if (!sources || sources.length === 0) {
    sourcesSection.hidden = true;
    return;
  }
  sourcesSection.hidden = false;

  sources.forEach((src) => {
    const item = document.createElement("div");
    item.className = "source-item";

    const title = document.createElement("div");
    title.className = "source-item-title";
    title.textContent = src.title;

    const meta = document.createElement("div");
    meta.className = "source-item-meta";
    const corpusLabel = src.corpus_type === "official" ? "official" : "supplementary";
    const roleLabel = src.source_role === "base" ? "base" : "supplementary";
    meta.textContent = `Тип корпуса: ${corpusLabel} · Роль: ${roleLabel}`;

    const path = document.createElement("div");
    path.className = "source-item-path";
    path.textContent = src.section_path;

    item.appendChild(title);
    item.appendChild(meta);
    item.appendChild(path);

    if (src.url && src.url.startsWith("http")) {
      const link = document.createElement("a");
      link.className = "source-item-link";
      link.href = src.url;
      link.textContent = "Открыть источник";
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      item.appendChild(link);
    }

    sourcesEl.appendChild(item);
  });
}

// ---- Render Response ----

function renderResponse(data) {
  resultPanel.hidden = false;
  answerBlock.hidden = data.mode !== "answer";
  tutorialBlock.hidden = data.mode !== "tutorial";

  resultBadge.textContent = MODE_LABELS[data.mode] || data.mode;
  resultVersion.textContent = "PostgreSQL " + data.pg_version;
  if (data.mode === "tutorial") {
    const isExtended = Boolean(data.extended_mode);
    resultExtended.hidden = false;
    resultExtended.textContent = isExtended
      ? "Расширенный учебный режим: включён"
      : "Расширенный учебный режим: выключен";
  } else {
    resultExtended.hidden = true;
    resultExtended.textContent = "";
  }

  if (data.mode === "answer") {
    answerText.textContent = data.answer || "";
  } else if (data.tutorial) {
    const t = data.tutorial;

    tutorialSummary.textContent = t.short_explanation || "";

    renderList(tutorialPrereq, t.prerequisites || []);
    showSection("#prereq-section", t.prerequisites);

    renderList(tutorialSteps, t.steps || []);
    showSection("#steps-section", t.steps);

    renderList(tutorialVerification, t.verification || []);
    showSection("#verification-section", t.verification);

    renderList(tutorialTroubleshooting, t.troubleshooting || []);
    showSection("#troubleshooting-section", t.troubleshooting);

    renderList(tutorialNotes, t.notes || []);
    showSection("#notes-section", t.notes);

    renderList(tutorialNextSteps, t.next_steps || []);
    showSection("#next-steps-section", t.next_steps);
  }

  renderSources(data.sources || []);
}

// ---- Render Clarification ----

function renderClarification(data) {
  clarificationPanel.hidden = false;
  clarificationQuestion.textContent = data.clarification.question;
  clarificationInput.value = "";
  clarificationInput.focus();

  // Save request context for follow-up
  pendingRequest = {
    question: questionEl.value,
    pg_version: versionEl.value,
    mode: modeEl.value,
    extended_mode: Boolean(extendedEl.checked),
  };
}

// ---- API Call ----

async function sendAsk(payload) {
  setError("");
  setLoading(true);

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      setError(data.detail || "Ошибка обработки запроса");
      return;
    }

    // Clarification response
    if (data.clarification && !data.tutorial && !data.answer) {
      renderClarification(data);
      return;
    }

    // Normal response
    renderResponse(data);
  } catch (err) {
    setError(err.message || "Ошибка сети. Проверьте подключение.");
  } finally {
    setLoading(false);
  }
}

// ---- Load versions ----

async function loadVersions() {
  const response = await fetch("/api/versions");
  if (!response.ok) {
    throw new Error("Не удалось загрузить версии PostgreSQL");
  }
  const payload = await response.json();
  versionEl.innerHTML = "";
  payload.versions.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.major_version;
    option.textContent = item.major_version;
    versionEl.appendChild(option);
  });
}

// ---- Events ----

modeEl.addEventListener("change", updateExtendedState);

form.addEventListener("submit", (e) => {
  e.preventDefault();
  pendingRequest = null;
  clarificationPanel.hidden = true;

  sendAsk({
    question: questionEl.value,
    pg_version: versionEl.value,
    mode: modeEl.value,
    extended_mode: Boolean(extendedEl.checked),
  });
});

clarificationBtn.addEventListener("click", () => {
  const answer = clarificationInput.value.trim();
  if (!answer) {
    clarificationInput.focus();
    return;
  }
  if (!pendingRequest) return;

  clarificationPanel.hidden = true;

  sendAsk({
    ...pendingRequest,
    clarification_answer: answer,
  });

  pendingRequest = null;
});

clarificationInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    clarificationBtn.click();
  }
});

// ---- Init ----

(async () => {
  try {
    await loadVersions();
    updateExtendedState();
  } catch (err) {
    setError(err.message || "Ошибка инициализации");
  }
})();
