/* ============================================
   PostgreSQL RAG Assistant — Main Page Logic
   ============================================ */

const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const questionError = document.getElementById("question-error");
const versionSelect = document.getElementById("pg-version");
const modeInputs = Array.from(document.querySelectorAll('input[name="answer-mode"]'));
const modeDescription = document.getElementById("mode-description");

const submitBtn = document.getElementById("submit-btn");
const submitBtnText = submitBtn.querySelector(".btn-text");
const loadingHint = document.getElementById("loading-hint");
const loadingStage = document.getElementById("loading-stage");
const answerLoading = document.getElementById("answer-loading");

const errorBox = document.getElementById("error-box");
const errorText = document.getElementById("error-text");
const errorDetails = document.getElementById("error-details");
const retryBtn = document.getElementById("retry-btn");
const copyErrorBtn = document.getElementById("copy-error-btn");

const answerZone = document.getElementById("answer-zone");
const resultBadge = document.getElementById("result-badge");
const resultVersion = document.getElementById("result-version");
const resultPolicy = document.getElementById("result-policy");

const answerEmpty = document.getElementById("answer-empty");
const answerBlock = document.getElementById("answer-block");
const answerText = document.getElementById("answer-text");

const tutorialBlock = document.getElementById("tutorial-block");
const tutorialSummarySection = document.getElementById("tutorial-summary-section");
const tutorialSummary = document.getElementById("tutorial-summary");
const tutorialPrereqSection = document.getElementById("prereq-section");
const tutorialStepsSection = document.getElementById("steps-section");
const tutorialNotesSection = document.getElementById("notes-section");
const tutorialPrereq = document.getElementById("tutorial-prereq");
const tutorialSteps = document.getElementById("tutorial-steps");
const tutorialNotes = document.getElementById("tutorial-notes");

const sourcesList = document.getElementById("sources");
const sourcesEmpty = document.getElementById("sources-empty");
const sourcesMoreBtn = document.getElementById("sources-more-btn");

const recentHistoryList = document.getElementById("recent-history");
const recentHistoryEmpty = document.getElementById("recent-history-empty");

const sidebarExamples = document.getElementById("sidebar-examples");

const MODE_LABELS = {
  short: "Краткий",
  detailed: "Подробный",
  tutorial: "Обучающий",
};

const HISTORY_MODE_LABELS = {
  short: "Краткий",
  detailed: "Подробный",
  tutorial: "Обучающий",
};

const MODE_DESCRIPTIONS = {
  short: "Быстро по официальной документации.",
  detailed: "Развёрнуто по официальной документации.",
  tutorial: "Простое объяснение, шаги и примеры.",
};

const POLICY_LABELS = {
  short: "official docs",
  detailed: "official docs",
  tutorial: "official + tutorial",
};

const LOADING_STAGES = [
  "Ищу источники...",
  "Формирую ответ...",
  "Проверяю формулировку ответа...",
];

const SOURCES_VISIBLE_LIMIT = 5;

const state = {
  currentResult: null,
  isLoading: false,
  loadingTimer: null,
  loadingIdx: 0,
  lastPayload: null,
  renderedSources: [],
  hiddenSupplementaryCount: 0,
  sourcesExpanded: false,
};

function normalizeText(value) {
  return String(value || "").trim();
}

function selectedAnswerMode() {
  const active = modeInputs.find((item) => item.checked);
  return active ? active.value : "short";
}

function setAnswerMode(mode) {
  if (!modeInputs.some((input) => input.value === mode)) {
    return;
  }
  modeInputs.forEach((input) => {
    input.checked = input.value === mode;
  });
  setModeDescription();
}

function setModeDescription() {
  modeDescription.textContent = MODE_DESCRIPTIONS[selectedAnswerMode()] || MODE_DESCRIPTIONS.short;
}

function autoResizeTextarea() {
  questionInput.style.height = "auto";
  questionInput.style.height = `${Math.max(156, questionInput.scrollHeight)}px`;
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

function showGlobalError(message, details = "") {
  errorBox.hidden = false;
  errorText.textContent = normalizeText(message) || "Сервис ответа временно недоступен. Проверьте настройки backend или повторите запрос.";
  errorDetails.textContent = normalizeText(details) || "Технические детали недоступны.";
  copyErrorBtn.textContent = "Скопировать ошибку";
}

function clearGlobalError() {
  errorBox.hidden = true;
  errorText.textContent = "";
  errorDetails.textContent = "";
  copyErrorBtn.textContent = "Скопировать ошибку";
}

function parseApiError(detailRaw) {
  const detail = normalizeText(detailRaw);

  if (!detail) {
    return {
      userMessage: "Сервис ответа временно недоступен. Проверьте настройки backend или повторите запрос.",
      technical: "Пустой ответ об ошибке от backend.",
    };
  }

  if (detail.includes("No relevant documentation fragments found for selected version")) {
    return {
      userMessage: "Не удалось найти релевантные фрагменты в выбранной версии документации.",
      technical: detail,
    };
  }

  if (detail.includes("Unsupported PostgreSQL version")) {
    return {
      userMessage: "Выбрана неподдерживаемая версия PostgreSQL.",
      technical: detail,
    };
  }

  if (
    detail.includes("GROQ_API_KEY") ||
    detail.includes("LLM_MODEL") ||
    detail.includes("LLM_PROVIDER") ||
    detail.includes("LLM") ||
    detail.includes("embedding") ||
    detail.includes("EMBEDDING_PROVIDER")
  ) {
    return {
      userMessage: "Сервис ответа временно недоступен. Проверьте настройки backend или повторите запрос.",
      technical: detail,
    };
  }

  return {
    userMessage: "Сервис ответа временно недоступен. Проверьте настройки backend или повторите запрос.",
    technical: detail,
  };
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

  return parseApiError(detail || `Ошибка сервера (HTTP ${response.status}).`);
}

function updateSubmitButtonState() {
  const hasQuestion = normalizeText(questionInput.value).length > 0;
  submitBtn.disabled = state.isLoading || !hasQuestion;
}

function setLoading(isLoading) {
  state.isLoading = isLoading;
  submitBtn.classList.toggle("is-loading", isLoading);
  submitBtnText.textContent = isLoading ? "Ищу источники..." : "Получить ответ";
  loadingHint.hidden = !isLoading;

  answerLoading.hidden = !isLoading;
  if (isLoading) {
    answerEmpty.hidden = true;
    answerBlock.hidden = true;
    tutorialBlock.hidden = true;

    state.loadingIdx = 0;
    loadingStage.textContent = LOADING_STAGES[state.loadingIdx];
    if (state.loadingTimer) {
      clearInterval(state.loadingTimer);
    }
    state.loadingTimer = setInterval(() => {
      state.loadingIdx = (state.loadingIdx + 1) % LOADING_STAGES.length;
      loadingStage.textContent = LOADING_STAGES[state.loadingIdx];
    }, 1300);
  } else if (state.loadingTimer) {
    clearInterval(state.loadingTimer);
    state.loadingTimer = null;
    loadingStage.textContent = LOADING_STAGES[0];
  }

  updateSubmitButtonState();
}

function clearAnswerUI() {
  answerText.innerHTML = "";
  answerBlock.hidden = true;
}

function clearTutorialUI() {
  tutorialSummary.innerHTML = "";
  tutorialPrereq.innerHTML = "";
  tutorialSteps.innerHTML = "";
  tutorialNotes.innerHTML = "";
  tutorialSummarySection.hidden = true;
  tutorialPrereqSection.hidden = true;
  tutorialStepsSection.hidden = true;
  tutorialNotesSection.hidden = true;
  tutorialBlock.hidden = true;
}

function clearSourcesUI(message = "Источники появятся после ответа.") {
  sourcesList.innerHTML = "";
  sourcesList.hidden = true;
  sourcesMoreBtn.hidden = true;
  sourcesEmpty.hidden = false;
  sourcesEmpty.textContent = message;

  state.renderedSources = [];
  state.hiddenSupplementaryCount = 0;
  state.sourcesExpanded = false;
}

function clearResultBadges() {
  resultBadge.textContent = "";
  resultVersion.textContent = "";
  resultPolicy.textContent = "";
  resultPolicy.classList.remove("badge-policy-tutorial");
}

function showEmptyAnswerState() {
  answerLoading.hidden = true;
  clearResultBadges();
  clearAnswerUI();
  clearTutorialUI();
  clearSourcesUI("Источники появятся после ответа.");
  answerEmpty.hidden = false;
}

function clearRenderedResult() {
  state.currentResult = null;
  showEmptyAnswerState();
}

function maybeScrollToAnswer() {
  const rect = answerZone.getBoundingClientRect();
  const belowViewport = rect.top > window.innerHeight - 160;
  const aboveViewport = rect.top < 70;
  if (belowViewport || aboveViewport) {
    requestAnimationFrame(() => {
      answerZone.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
}

async function loadVersions() {
  const response = await fetch("/api/versions");
  if (!response.ok) {
    const apiErr = await readApiError(response);
    throw new Error(apiErr.userMessage);
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
    option.textContent = `PostgreSQL ${version}`;
    versionSelect.appendChild(option);
  });

  if (!versions.length) {
    throw new Error("Не удалось получить список поддерживаемых версий PostgreSQL.");
  }
}

function payloadFromForm() {
  const question = normalizeText(questionInput.value).replace(/\s+/g, " ");
  return {
    question,
    pg_version: versionSelect.value,
    answer_mode: selectedAnswerMode(),
  };
}

function maybeParseObjectLikeString(raw) {
  const trimmed = normalizeText(raw);
  if (!(trimmed.startsWith("{") && trimmed.endsWith("}"))) {
    return null;
  }

  const normalized = trimmed
    .replace(/'/g, '"')
    .replace(/\bNone\b/g, "null")
    .replace(/\bTrue\b/g, "true")
    .replace(/\bFalse\b/g, "false");

  try {
    return JSON.parse(normalized);
  } catch {
    return null;
  }
}

function isEmptySection(value) {
  if (value === null || value === undefined) {
    return true;
  }
  if (typeof value === "string") {
    return normalizeText(value).length === 0;
  }
  if (Array.isArray(value)) {
    return value.length === 0 || value.every((item) => isEmptySection(item));
  }
  if (typeof value === "object") {
    return Object.values(value).every((item) => isEmptySection(item));
  }
  return false;
}

function normalizeStepItem(item) {
  if (item === null || item === undefined) {
    return null;
  }

  if (typeof item === "string") {
    const parsed = maybeParseObjectLikeString(item);
    if (parsed && typeof parsed === "object") {
      return normalizeStepItem(parsed);
    }

    const trimmed = normalizeText(item);
    if (!trimmed) {
      return null;
    }

    const sqlFence = trimmed.match(/^```\s*sql\s*\n([\s\S]*?)```$/i);
    if (sqlFence) {
      return { kind: "sql", sql: normalizeText(sqlFence[1]) };
    }

    return { kind: "text", text: trimmed };
  }

  if (typeof item === "object") {
    const title = normalizeText(item.title);
    const description = normalizeText(item.description);
    const text = normalizeText(item.text);
    const sql = normalizeText(item.sql);
    const step = normalizeText(item.step);
    const instruction = normalizeText(item.instruction);
    const value = normalizeText(item.value);

    if (sql) {
      return { kind: "sql", sql };
    }
    if (title && description) {
      return { kind: "pair", title, description };
    }
    if (text) {
      return { kind: "text", text };
    }
    if (step) {
      return { kind: "text", text: step };
    }
    if (instruction) {
      return { kind: "text", text: instruction };
    }
    if (value) {
      return { kind: "text", text: value };
    }

    const plainParts = Object.entries(item)
      .filter(([, raw]) => ["string", "number", "boolean"].includes(typeof raw))
      .map(([key, raw]) => `${key}: ${String(raw).trim()}`)
      .filter((part) => normalizeText(part).length > 0);

    if (plainParts.length) {
      return { kind: "text", text: plainParts.join("; ") };
    }
  }

  const fallback = normalizeText(item);
  return fallback ? { kind: "text", text: fallback } : null;
}

function renderSQLBlock(sqlRaw, language = "SQL") {
  const sql = normalizeText(sqlRaw);
  const wrapper = document.createElement("div");
  wrapper.className = "sql-block";

  const head = document.createElement("div");
  head.className = "sql-head";

  const label = document.createElement("span");
  label.className = "sql-label";
  label.textContent = normalizeText(language).toUpperCase() || "SQL";

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "copy-sql-btn";
  copyBtn.textContent = "Копировать";
  copyBtn.dataset.sql = sql;

  head.appendChild(label);
  head.appendChild(copyBtn);

  const pre = document.createElement("pre");
  const code = document.createElement("code");
  code.textContent = sql;
  pre.appendChild(code);

  wrapper.appendChild(head);
  wrapper.appendChild(pre);
  return wrapper;
}

function appendTextBlock(container, textBlock) {
  const trimmed = normalizeText(textBlock);
  if (!trimmed) {
    return;
  }

  const chunks = trimmed
    .split(/\n{2,}/)
    .map((chunk) => chunk.trim())
    .filter(Boolean);

  chunks.forEach((chunk) => {
    const lines = chunk.split("\n").map((line) => line.trim()).filter(Boolean);
    const isBullet = lines.length > 0 && lines.every((line) => /^[-*]\s+/.test(line));
    const isOrdered = lines.length > 0 && lines.every((line) => /^\d+[.)]\s+/.test(line));

    if (isBullet) {
      const ul = document.createElement("ul");
      ul.className = "text-list";
      lines.forEach((line) => {
        const li = document.createElement("li");
        li.textContent = line.replace(/^[-*]\s+/, "");
        ul.appendChild(li);
      });
      container.appendChild(ul);
      return;
    }

    if (isOrdered) {
      const ol = document.createElement("ol");
      ol.className = "text-list ordered";
      lines.forEach((line) => {
        const li = document.createElement("li");
        li.textContent = line.replace(/^\d+[.)]\s+/, "");
        ol.appendChild(li);
      });
      container.appendChild(ol);
      return;
    }

    const p = document.createElement("p");
    p.textContent = lines.join(" ");
    container.appendChild(p);
  });
}

function renderRichContent(target, rawText) {
  target.innerHTML = "";
  const text = normalizeText(rawText);
  if (!text) {
    return;
  }

  const codeFence = /```\s*(\w+)?\s*\n([\s\S]*?)```/gi;
  let lastIdx = 0;
  let match;

  while ((match = codeFence.exec(text)) !== null) {
    const [full, language, code] = match;
    const start = match.index;

    if (start > lastIdx) {
      appendTextBlock(target, text.slice(lastIdx, start));
    }

    target.appendChild(renderSQLBlock(code, language || "SQL"));
    lastIdx = start + full.length;
  }

  if (lastIdx < text.length) {
    appendTextBlock(target, text.slice(lastIdx));
  }
}

function renderStepItem(target, normalizedItem) {
  if (!normalizedItem) {
    return;
  }

  const li = document.createElement("li");

  if (normalizedItem.kind === "pair") {
    const title = document.createElement("strong");
    title.textContent = normalizedItem.title;
    const desc = document.createElement("span");
    desc.textContent = ` — ${normalizedItem.description}`;
    li.appendChild(title);
    li.appendChild(desc);
    target.appendChild(li);
    return;
  }

  if (normalizedItem.kind === "sql") {
    li.className = "list-item-sql";
    li.appendChild(renderSQLBlock(normalizedItem.sql, "SQL"));
    target.appendChild(li);
    return;
  }

  li.textContent = normalizedItem.text;
  target.appendChild(li);
}

function renderSection(sectionEl, listEl, items) {
  const normalized = (Array.isArray(items) ? items : [])
    .map((item) => normalizeStepItem(item))
    .filter(Boolean);

  const empty = isEmptySection(normalized);
  sectionEl.hidden = empty;
  listEl.innerHTML = "";
  if (empty) {
    return;
  }

  normalized.forEach((item) => renderStepItem(listEl, item));
}

function inferPgVersionFromSource(sourceUrl, fallbackVersion) {
  const url = normalizeText(sourceUrl);
  const match = url.match(/\/docs\/(\d+)\//);
  if (match) {
    return match[1];
  }
  return fallbackVersion || "—";
}

function normalizeCorpusType(corpusTypeRaw) {
  const raw = normalizeText(corpusTypeRaw).toLowerCase();
  if (raw === "supplementary" || raw === "tutorial") {
    return "tutorial";
  }
  return "official";
}

function renderSourceCard(item) {
  const card = document.createElement("article");
  card.className = "source-card";

  const head = document.createElement("div");
  head.className = "source-card-head";

  const tags = document.createElement("div");
  tags.className = "source-card-tags";

  const corpusBadge = document.createElement("span");
  corpusBadge.className = `source-chip ${item.corpusType === "tutorial" ? "source-chip-tutorial" : "source-chip-official"}`;
  corpusBadge.textContent = item.corpusType;

  const versionBadge = document.createElement("span");
  versionBadge.className = "source-chip source-chip-version";
  versionBadge.textContent = `PostgreSQL ${item.sourceVersion}`;

  tags.appendChild(corpusBadge);
  tags.appendChild(versionBadge);

  const titleEl = document.createElement("h4");
  titleEl.className = "source-title";
  titleEl.textContent = item.title;

  const pathEl = document.createElement("p");
  pathEl.className = "source-path";
  pathEl.textContent = item.sectionPath;

  const meta = document.createElement("div");
  meta.className = "source-meta";

  if (item.sourceUrl) {
    const link = document.createElement("a");
    link.href = item.sourceUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Открыть источник";
    meta.appendChild(link);
  }

  if (Number.isFinite(item.score) || Number.isFinite(item.rank)) {
    const details = document.createElement("details");
    details.className = "source-details";

    const summary = document.createElement("summary");
    summary.textContent = "Метаданные";

    const detailText = document.createElement("p");
    const scoreText = Number.isFinite(item.score) ? item.score.toFixed(3) : "n/a";
    const rankText = Number.isFinite(item.rank) && item.rank > 0 ? String(item.rank) : "n/a";
    detailText.textContent = `relevance: ${scoreText}; rank: ${rankText}`;

    details.appendChild(summary);
    details.appendChild(detailText);
    meta.appendChild(details);
  }

  head.appendChild(tags);
  head.appendChild(titleEl);

  card.appendChild(head);
  card.appendChild(pathEl);
  card.appendChild(meta);
  return card;
}

function paintSources() {
  sourcesList.innerHTML = "";

  const items = state.renderedSources;
  const hasMore = items.length > SOURCES_VISIBLE_LIMIT;
  const visibleItems = state.sourcesExpanded || !hasMore ? items : items.slice(0, SOURCES_VISIBLE_LIMIT);

  if (state.hiddenSupplementaryCount > 0) {
    const warning = document.createElement("article");
    warning.className = "source-warning";
    warning.textContent = `Скрыто tutorial-источников для режима official docs: ${state.hiddenSupplementaryCount}.`;
    sourcesList.appendChild(warning);
  }

  visibleItems.forEach((item) => {
    sourcesList.appendChild(renderSourceCard(item));
  });

  if (!hasMore) {
    sourcesMoreBtn.hidden = true;
    return;
  }

  const remaining = items.length - SOURCES_VISIBLE_LIMIT;
  sourcesMoreBtn.hidden = false;
  sourcesMoreBtn.textContent = state.sourcesExpanded ? "Скрыть" : `Показать ещё (${remaining})`;
}

function renderSources(sources, answerMode, pgVersion) {
  state.renderedSources = [];
  state.hiddenSupplementaryCount = 0;
  state.sourcesExpanded = false;

  const safeSources = Array.isArray(sources) ? sources : [];
  if (!safeSources.length) {
    clearSourcesUI("Источники появятся после ответа.");
    return;
  }

  const normalized = safeSources.map((source, index) => {
    const sourceUrl = normalizeText(source.url);
    return {
      title: normalizeText(source.title) || `Источник #${index + 1}`,
      sectionPath: normalizeText(source.section_path) || "Раздел не указан",
      sourceUrl,
      corpusType: normalizeCorpusType(source.corpus_type),
      rank: Number(source.rank_position),
      score: Number(source.similarity_score),
      sourceVersion: inferPgVersionFromSource(sourceUrl, pgVersion),
    };
  });

  let filtered = normalized;
  if (answerMode === "short" || answerMode === "detailed") {
    filtered = normalized.filter((item) => item.corpusType !== "tutorial");
    state.hiddenSupplementaryCount = normalized.length - filtered.length;
  }

  if (!filtered.length) {
    clearSourcesUI("Для выбранного режима отображаются только official источники.");
    return;
  }

  state.renderedSources = filtered;
  sourcesEmpty.hidden = true;
  sourcesList.hidden = false;
  paintSources();
}

function renderAnswerResult(result) {
  const answer = normalizeText(result.answer);
  if (!answer) {
    showGlobalError("Не удалось сформировать ответ", "Backend вернул пустой ответ.");
    showEmptyAnswerState();
    return;
  }

  answerLoading.hidden = true;
  answerEmpty.hidden = true;
  clearTutorialUI();

  const mode = result.answer_mode;
  resultBadge.textContent = MODE_LABELS[mode] || "Ответ";
  resultVersion.textContent = `PostgreSQL ${result.pg_version || "—"}`;
  resultPolicy.textContent = POLICY_LABELS[mode] || POLICY_LABELS.short;
  resultPolicy.classList.remove("badge-policy-tutorial");

  renderRichContent(answerText, answer);
  answerBlock.hidden = false;

  renderSources(result.sources || [], mode, result.pg_version);
  maybeScrollToAnswer();
}

function renderTutorialResult(result) {
  const tutorial = result.tutorial;
  if (!tutorial || typeof tutorial !== "object" || Array.isArray(tutorial)) {
    showGlobalError("Не удалось сформировать ответ", "Некорректный формат tutorial-ответа от backend.");
    showEmptyAnswerState();
    return;
  }

  answerLoading.hidden = true;
  answerEmpty.hidden = true;
  clearAnswerUI();

  resultBadge.textContent = MODE_LABELS.tutorial;
  resultVersion.textContent = `PostgreSQL ${result.pg_version || "—"}`;
  resultPolicy.textContent = POLICY_LABELS.tutorial;
  resultPolicy.classList.add("badge-policy-tutorial");

  const summary = normalizeText(tutorial.short_explanation);
  tutorialSummarySection.hidden = isEmptySection(summary);
  renderRichContent(tutorialSummary, summary);

  renderSection(tutorialPrereqSection, tutorialPrereq, tutorial.prerequisites);
  renderSection(tutorialStepsSection, tutorialSteps, tutorial.steps);
  renderSection(tutorialNotesSection, tutorialNotes, tutorial.notes);

  const hasVisibleSection =
    !tutorialSummarySection.hidden ||
    !tutorialPrereqSection.hidden ||
    !tutorialStepsSection.hidden ||
    !tutorialNotesSection.hidden;

  if (!hasVisibleSection) {
    showGlobalError("Не удалось сформировать ответ", "Tutorial-ответ не содержит заполненных секций.");
    showEmptyAnswerState();
    return;
  }

  tutorialBlock.hidden = false;
  renderSources(result.sources || [], "tutorial", result.pg_version);
  maybeScrollToAnswer();
}

function renderCurrentResult() {
  const result = state.currentResult;
  if (!result) {
    showEmptyAnswerState();
    return;
  }

  if (result.answer_mode === "short" || result.answer_mode === "detailed") {
    renderAnswerResult(result);
    return;
  }

  if (result.answer_mode === "tutorial") {
    renderTutorialResult(result);
    return;
  }

  showGlobalError("Не удалось сформировать ответ", "Backend вернул некорректный режим ответа.");
  showEmptyAnswerState();
}

function setCurrentResult(result) {
  state.currentResult = result;
  renderCurrentResult();
}

async function submitAsk(payload) {
  setLoading(true);
  clearGlobalError();

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const apiErr = await readApiError(response);
      throw new Error(JSON.stringify(apiErr));
    }

    const data = await response.json();

    setCurrentResult(data);
    loadRecentHistory();
  } catch (error) {
    let userMessage = "Сервис ответа временно недоступен. Проверьте настройки backend или повторите запрос.";
    let technical = "Backend недоступен или вернул ошибку.";

    try {
      const parsed = JSON.parse(error.message || "{}");
      userMessage = normalizeText(parsed.userMessage) || userMessage;
      technical = normalizeText(parsed.technical) || technical;
    } catch {
      technical = normalizeText(error.message) || technical;
    }

    showGlobalError(userMessage, technical);
  } finally {
    setLoading(false);
  }
}

async function loadRecentHistory() {
  try {
    const response = await fetch("/api/history?limit=4");
    if (!response.ok) {
      return;
    }

    const payload = await response.json();
    const items = Array.isArray(payload.items) ? payload.items : [];

    recentHistoryList.innerHTML = "";
    if (!items.length) {
      recentHistoryEmpty.hidden = false;
      return;
    }

    recentHistoryEmpty.hidden = true;

    items.slice(0, 4).forEach((item) => {
      const question = normalizeText(item.user_question);
      if (!question) {
        return;
      }

      const li = document.createElement("li");
      li.className = "recent-history-item";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "recent-history-btn";
      button.dataset.question = question;
      if (item.pg_version) {
        button.dataset.version = String(item.pg_version);
      }
      if (item.mode) {
        button.dataset.mode = String(item.mode);
      }

      const title = document.createElement("span");
      title.className = "recent-history-question";
      title.textContent = question;

      const meta = document.createElement("span");
      const mode = HISTORY_MODE_LABELS[item.mode] || item.mode;
      const version = item.pg_version ? `PG ${item.pg_version}` : "PG —";
      meta.className = "recent-history-meta";
      meta.textContent = `${mode} · ${version}`;

      button.appendChild(title);
      button.appendChild(meta);
      li.appendChild(button);
      recentHistoryList.appendChild(li);
    });
  } catch {
    recentHistoryEmpty.hidden = false;
  }
}

function applyQuestionPreset(question, mode = "") {
  questionInput.value = normalizeText(question);
  autoResizeTextarea();
  if (mode) {
    setAnswerMode(mode);
  }
  updateSubmitButtonState();
  questionInput.focus();
}

function applyHistoryItem(button) {
  const question = normalizeText(button.dataset.question);
  const version = normalizeText(button.dataset.version);
  const mode = normalizeText(button.dataset.mode);

  if (question) {
    applyQuestionPreset(question);
  }

  if (version && Array.from(versionSelect.options).some((opt) => opt.value === version)) {
    versionSelect.value = version;
  }

  if (mode) {
    setAnswerMode(mode);
  }
}

function handleCopySql(button) {
  const sql = normalizeText(button.dataset.sql);
  if (!sql) {
    return;
  }

  navigator.clipboard.writeText(sql).then(() => {
    const prev = button.textContent;
    button.textContent = "Скопировано";
    button.disabled = true;
    setTimeout(() => {
      button.textContent = prev;
      button.disabled = false;
    }, 1200);
  }).catch(() => {
    button.textContent = "Ошибка";
    setTimeout(() => {
      button.textContent = "Копировать";
    }, 1200);
  });
}

function handleCopyError() {
  const details = normalizeText(errorDetails.textContent) || normalizeText(errorText.textContent);
  if (!details) {
    return;
  }

  navigator.clipboard.writeText(details).then(() => {
    copyErrorBtn.textContent = "Скопировано";
    setTimeout(() => {
      copyErrorBtn.textContent = "Скопировать ошибку";
    }, 1200);
  }).catch(() => {
    copyErrorBtn.textContent = "Ошибка";
    setTimeout(() => {
      copyErrorBtn.textContent = "Скопировать ошибку";
    }, 1200);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  clearGlobalError();
  showQuestionError("");

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

  state.lastPayload = payload;
  await submitAsk(payload);
});

retryBtn.addEventListener("click", async () => {
  if (!state.lastPayload || state.isLoading) {
    return;
  }
  await submitAsk(state.lastPayload);
});

copyErrorBtn.addEventListener("click", handleCopyError);

sourcesMoreBtn.addEventListener("click", () => {
  state.sourcesExpanded = !state.sourcesExpanded;
  paintSources();
});

questionInput.addEventListener("input", () => {
  autoResizeTextarea();
  if (!questionError.hidden) {
    showQuestionError("");
  }
  updateSubmitButtonState();
});

modeInputs.forEach((input) => {
  input.addEventListener("change", () => {
    clearGlobalError();
    setModeDescription();
  });
});

if (sidebarExamples) {
  sidebarExamples.addEventListener("click", (event) => {
    const target = event.target.closest(".prompt-item");
    if (!target) {
      return;
    }
    const question = target.dataset.question;
    const mode = normalizeText(target.dataset.mode);
    if (question) {
      applyQuestionPreset(question, mode);
    }
  });
}

recentHistoryList.addEventListener("click", (event) => {
  const button = event.target.closest(".recent-history-btn");
  if (!button) {
    return;
  }
  applyHistoryItem(button);
});

document.addEventListener("click", (event) => {
  const copyBtn = event.target.closest(".copy-sql-btn");
  if (!copyBtn) {
    return;
  }
  handleCopySql(copyBtn);
});

window.addEventListener("DOMContentLoaded", async () => {
  try {
    await loadVersions();
    await loadRecentHistory();
  } catch (error) {
    showGlobalError(
      "Не удалось сформировать ответ",
      normalizeText(error.message) || "Ошибка инициализации UI."
    );
  }

  autoResizeTextarea();
  clearRenderedResult();
  setModeDescription();
  updateSubmitButtonState();
});
