/* ============================================
   PostgreSQL Assistant — Main Page Logic
   ============================================ */

const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const questionError = document.getElementById("question-error");
const versionSelect = document.getElementById("pg-version");
const modeSelect = document.getElementById("mode");
const additionalSettings = document.getElementById("additional-settings");
const extendedCheckbox = document.getElementById("extended-mode");
const extendedGroup = document.getElementById("extended-group");
const extendedLabel = document.getElementById("extended-label");
const submitBtn = document.getElementById("submit-btn");
const submitBtnText = submitBtn.querySelector(".btn-text");

const errorBox = document.getElementById("error-box");
const loadingPanel = document.getElementById("loading-panel");
const resultPanel = document.getElementById("result-panel");

const clarificationPanel = document.getElementById("clarification-panel");
const clarificationQuestion = document.getElementById("clarification-question");
const clarificationInput = document.getElementById("clarification-input");
const clarificationBtn = document.getElementById("clarification-btn");

const resultBadge = document.getElementById("result-badge");
const resultVersion = document.getElementById("result-version");
const resultExtended = document.getElementById("result-extended");

const answerBlock = document.getElementById("answer-block");
const tutorialBlock = document.getElementById("tutorial-block");
const answerText = document.getElementById("answer-text");

const tutorialSummary = document.getElementById("tutorial-summary");
const tutorialPrereq = document.getElementById("tutorial-prereq");
const tutorialSteps = document.getElementById("tutorial-steps");
const tutorialNotes = document.getElementById("tutorial-notes");

const sourcesSection = document.getElementById("sources-section");
const sourcesList = document.getElementById("sources");

const MODE_LABELS = {
  answer: "Краткий ответ",
  tutorial: "Обучающий режим",
};

const state = {
  currentResult: null,
  pendingClarificationPayload: null,
  isLoading: false,
};

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function normalizeText(value) {
  return String(value || "").trim();
}

function showQuestionError(message) {
  if (!message) {
    questionError.hidden = true;
    questionError.textContent = "";
    questionInput.removeAttribute("aria-invalid");
    return;
  }
  questionError.hidden = false;
  questionError.textContent = message;
  questionInput.setAttribute("aria-invalid", "true");
}

function showGlobalError(message) {
  errorBox.hidden = false;
  errorBox.textContent = message;
}

function clearGlobalError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

function mapApiError(rawDetail) {
  const detail = normalizeText(rawDetail);
  if (!detail) {
    return "Не удалось сформировать ответ. Проверьте настройки LLM/API и повторите запрос.";
  }

  if (detail.includes("extended_mode is allowed only for tutorial mode")) {
    return "Расширенный учебный режим доступен только для обучающего режима.";
  }
  if (detail.includes("No relevant documentation fragments found for selected version")) {
    return "По выбранной версии PostgreSQL не найдено релевантных фрагментов документации.";
  }
  if (detail.includes("Unsupported PostgreSQL version")) {
    return "Выбрана неподдерживаемая версия PostgreSQL.";
  }

  if (
    detail.includes("GROQ_API_KEY") ||
    detail.includes("GROQ_MODEL") ||
    detail.includes("Groq") ||
    detail.includes("LLM")
  ) {
    return "Не удалось сформировать ответ. Проверьте настройки LLM/API и повторите запрос.";
  }

  return detail;
}

async function readApiError(response) {
  let detail = "";

  try {
    const payload = await response.json();
    if (Array.isArray(payload?.detail)) {
      detail = payload.detail
        .map((item) => normalizeText(item?.msg || item))
        .filter(Boolean)
        .join("; ");
    } else {
      detail = normalizeText(payload?.detail || payload?.message || "");
    }
  } catch {
    detail = "";
  }

  return mapApiError(detail || `Ошибка сервера (HTTP ${response.status}).`);
}

function setLoading(isLoading) {
  state.isLoading = isLoading;
  submitBtn.classList.toggle("is-loading", isLoading);
  submitBtnText.textContent = isLoading ? "Формируем ответ..." : "Получить ответ";
  loadingPanel.hidden = !isLoading;
  updateSubmitButtonState();
}

function clearAnswerUI() {
  answerText.textContent = "";
  answerBlock.hidden = true;
}

function clearTutorialUI() {
  tutorialSummary.textContent = "";
  tutorialPrereq.innerHTML = "";
  tutorialSteps.innerHTML = "";
  tutorialNotes.innerHTML = "";
  tutorialBlock.hidden = true;
}

function clearSourcesUI() {
  sourcesSection.hidden = true;
  sourcesList.innerHTML = "";
}

function resetResultHeader() {
  resultBadge.textContent = "";
  resultVersion.textContent = "";

  resultExtended.textContent = "";
  resultExtended.hidden = true;
  resultExtended.classList.remove("badge-warning", "badge-outline");
}

function clearRenderedResult() {
  state.currentResult = null;
  resetResultHeader();
  clearAnswerUI();
  clearTutorialUI();
  clearSourcesUI();
  resultPanel.hidden = true;
}

function setExtendedAvailability() {
  const tutorialMode = modeSelect.value === "tutorial";

  if (!tutorialMode) {
    extendedCheckbox.checked = false;
  }

  additionalSettings.classList.toggle("is-visible", tutorialMode);
  additionalSettings.hidden = !tutorialMode;
  extendedCheckbox.disabled = false;
  extendedGroup.classList.remove("is-disabled");
  extendedLabel.classList.remove("disabled");
}

function updateSubmitButtonState() {
  const hasQuestion = normalizeText(questionInput.value).length > 0;
  submitBtn.disabled = state.isLoading || !hasQuestion;
}

async function loadVersions() {
  const response = await fetch("/api/versions");
  if (!response.ok) {
    throw new Error(await readApiError(response));
  }

  const payload = await response.json();
  const versions = (payload.versions || [])
    .map((item) => String(item.major_version))
    .filter(Boolean)
    .sort((a, b) => Number(b) - Number(a));

  versionSelect.innerHTML = "";
  versions.forEach((version) => {
    const option = document.createElement("option");
    option.value = version;
    option.textContent = version;
    versionSelect.appendChild(option);
  });

  if (!versions.length) {
    throw new Error("Не удалось получить список поддерживаемых версий PostgreSQL.");
  }
}

function payloadFromForm() {
  const question = normalizeText(questionInput.value).replace(/\s+/g, " ");
  const mode = modeSelect.value;
  const extendedMode = mode === "tutorial" && extendedCheckbox.checked;

  return {
    question,
    pg_version: versionSelect.value,
    mode,
    extended_mode: extendedMode,
  };
}

function renderSimpleList(target, items, fallbackText) {
  const normalized = Array.isArray(items)
    ? items.map((item) => normalizeText(item)).filter(Boolean)
    : [];

  if (!normalized.length) {
    target.innerHTML = `<li class="list-empty">${escapeHtml(fallbackText)}</li>`;
    return;
  }

  target.innerHTML = normalized
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
}

function renderSources(sources) {
  if (!Array.isArray(sources) || !sources.length) {
    sourcesSection.hidden = false;
    sourcesList.innerHTML = '<div class="source-empty">Источники не найдены</div>';
    return;
  }

  sourcesSection.hidden = false;
  sourcesList.innerHTML = sources
    .map((source, index) => {
      const title = normalizeText(source.title) || `Источник #${index + 1}`;
      const sectionPath = normalizeText(source.section_path) || "Раздел не указан";
      const sourceUrl = normalizeText(source.url);
      const corpusType = normalizeText(source.corpus_type) || "unknown";
      const sourceRole = normalizeText(source.source_role) || "base";
      const rank = Number(source.rank_position);
      const score = Number(source.similarity_score);

      const corpusBadgeClass =
        corpusType === "supplementary" ? "badge-source-supplementary" : "badge-source-official";
      const corpusLabel = corpusType === "supplementary" ? "supplementary" : "official";
      const roleLabel = sourceRole === "supplementary" ? "supplementary" : "base";

      const rankText = Number.isFinite(rank) ? `rank #${rank}` : "";
      const scoreText = Number.isFinite(score) ? `score ${score.toFixed(3)}` : "";

      const urlHtml = sourceUrl.startsWith("http")
        ? `<a class="source-item-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(sourceUrl)}</a>`
        : '<span class="source-item-link muted">URL отсутствует</span>';

      return `
        <article class="source-item">
          <div class="source-item-top">
            <h4 class="source-item-title">${escapeHtml(title)}</h4>
            <div class="source-item-tags">
              <span class="source-tag ${corpusBadgeClass}">${escapeHtml(corpusLabel)}</span>
              <span class="source-tag source-tag-role">${escapeHtml(roleLabel)}</span>
            </div>
          </div>
          <p class="source-item-path">${escapeHtml(sectionPath)}</p>
          <div class="source-item-meta">
            ${urlHtml}
            ${rankText ? `<span>${escapeHtml(rankText)}</span>` : ""}
            ${scoreText ? `<span>${escapeHtml(scoreText)}</span>` : ""}
          </div>
        </article>
      `;
    })
    .join("");
}

function renderAnswerResult(result) {
  const answer = normalizeText(result.answer);
  if (!answer) {
    clearRenderedResult();
    showGlobalError("Некорректный формат answer-ответа");
    return;
  }

  resetResultHeader();
  resultBadge.textContent = MODE_LABELS.answer;
  resultVersion.textContent = `PostgreSQL ${result.pg_version || "—"}`;
  resultExtended.hidden = false;
  resultExtended.classList.add("badge-outline");
  resultExtended.textContent = "Только официальный корпус";

  clearTutorialUI();
  answerText.textContent = answer;
  answerBlock.hidden = false;

  renderSources(result.sources || []);
  resultPanel.hidden = false;
}

function renderTutorialResult(result) {
  const tutorial = result.tutorial;
  if (!tutorial || typeof tutorial !== "object" || Array.isArray(tutorial)) {
    clearRenderedResult();
    showGlobalError("Некорректный формат tutorial-ответа");
    return;
  }

  resetResultHeader();
  resultBadge.textContent = MODE_LABELS.tutorial;
  resultVersion.textContent = `PostgreSQL ${result.pg_version || "—"}`;

  resultExtended.hidden = false;
  if (result.extended_mode) {
    resultExtended.textContent = "Расширенный режим включён";
    resultExtended.classList.add("badge-warning");
  } else {
    resultExtended.textContent = "Только официальный корпус";
    resultExtended.classList.add("badge-outline");
  }

  clearAnswerUI();

  tutorialSummary.textContent =
    normalizeText(tutorial.short_explanation) || "Недостаточно подтвержденных данных в найденном контексте.";

  const prerequisites = Array.isArray(tutorial.prerequisites)
    ? tutorial.prerequisites.map((item) => normalizeText(item)).filter(Boolean)
    : [];
  const steps = Array.isArray(tutorial.steps)
    ? tutorial.steps.map((item) => normalizeText(item)).filter(Boolean)
    : [];
  const notes = Array.isArray(tutorial.notes)
    ? tutorial.notes.map((item) => normalizeText(item)).filter(Boolean)
    : [];

  const prereqSection = document.getElementById("prereq-section");
  const stepsSection = document.getElementById("steps-section");
  const notesSection = document.getElementById("notes-section");

  prereqSection.hidden = prerequisites.length === 0;
  stepsSection.hidden = steps.length === 0;
  notesSection.hidden = notes.length === 0;

  if (prerequisites.length > 0) {
    renderSimpleList(tutorialPrereq, prerequisites, "");
  } else {
    tutorialPrereq.innerHTML = "";
  }

  if (steps.length > 0) {
    renderSimpleList(tutorialSteps, steps, "");
  } else {
    tutorialSteps.innerHTML = "";
  }

  if (notes.length > 0) {
    renderSimpleList(tutorialNotes, notes, "");
  } else {
    tutorialNotes.innerHTML = "";
  }

  tutorialBlock.hidden = false;

  renderSources(result.sources || []);
  resultPanel.hidden = false;
}

function renderCurrentResult() {
  const result = state.currentResult;
  if (!result) {
    clearRenderedResult();
    return;
  }

  if (result.mode === "answer") {
    renderAnswerResult(result);
    return;
  }

  if (result.mode === "tutorial") {
    renderTutorialResult(result);
    return;
  }

  clearRenderedResult();
  showGlobalError("Некорректный режим ответа от backend.");
}

function setCurrentResult(result) {
  state.currentResult = result;
  renderCurrentResult();
}

function showClarification(clarification, basePayload) {
  state.pendingClarificationPayload = basePayload;
  clarificationQuestion.textContent = normalizeText(clarification.question) || "Нужно уточнить вопрос.";
  clarificationInput.value = "";
  clarificationPanel.hidden = false;
  clarificationInput.focus();
}

async function submitAsk(payload) {
  setLoading(true);
  clearGlobalError();
  clearRenderedResult();

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(await readApiError(response));
    }

    const data = await response.json();

    if (data?.clarification) {
      showClarification(data.clarification, payload);
      return;
    }

    clarificationPanel.hidden = true;
    state.pendingClarificationPayload = null;
    setCurrentResult(data);
  } catch (error) {
    clearRenderedResult();
    showGlobalError(normalizeText(error.message) || "Ошибка при выполнении запроса.");
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  clearGlobalError();
  showQuestionError("");
  clarificationPanel.hidden = true;

  const payload = payloadFromForm();

  if (!payload.question) {
    showQuestionError("Введите вопрос перед отправкой.");
    questionInput.focus();
    return;
  }

  if (payload.question.length < 3) {
    showQuestionError("Вопрос должен содержать минимум 3 символа.");
    questionInput.focus();
    return;
  }

  state.pendingClarificationPayload = null;
  await submitAsk(payload);
});

clarificationBtn.addEventListener("click", async () => {
  clearGlobalError();

  if (!state.pendingClarificationPayload) {
    showGlobalError("Сначала отправьте основной вопрос.");
    return;
  }

  const clarificationAnswer = normalizeText(clarificationInput.value);
  if (!clarificationAnswer) {
    showGlobalError("Введите уточнение, чтобы продолжить.");
    clarificationInput.focus();
    return;
  }

  const payload = {
    ...state.pendingClarificationPayload,
    clarification_answer: clarificationAnswer,
  };

  clarificationPanel.hidden = true;
  await submitAsk(payload);
});

questionInput.addEventListener("input", () => {
  if (!questionError.hidden) {
    showQuestionError("");
  }
  updateSubmitButtonState();
});

modeSelect.addEventListener("change", () => {
  setExtendedAvailability();
  clearGlobalError();

  if (modeSelect.value === "answer") {
    extendedCheckbox.checked = false;
  } else {
    extendedCheckbox.checked = false;
  }

  state.pendingClarificationPayload = null;
  clarificationPanel.hidden = true;
  clearRenderedResult();
});

window.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadVersions();
  } catch (error) {
    showGlobalError(normalizeText(error.message) || "Не удалось загрузить версии PostgreSQL.");
  }

  setExtendedAvailability();
  clearRenderedResult();
  updateSubmitButtonState();
});
