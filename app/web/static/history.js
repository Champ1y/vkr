/* ============================================
   PostgreSQL Assistant — History Page Logic
   ============================================ */

const refreshBtn = document.getElementById("refresh-btn");
const historyList = document.getElementById("history-list");

const MODE_LABELS = {
  answer: "Краткий ответ",
  tutorial: "Обучающий режим",
};

const STATUS_LABELS = {
  success: "Успешно",
  failed: "Ошибка",
};

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formatDate(isoString) {
  try {
    const value = new Date(isoString);
    return value.toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString || "";
  }
}

function getPreview(item) {
  if (item.mode === "answer") {
    return (item.answer_text || "").trim();
  }

  const tutorial = item.tutorial_json || {};
  const short = (tutorial.short_explanation || "").trim();
  if (short) {
    return short;
  }

  if (Array.isArray(tutorial.steps) && tutorial.steps.length > 0) {
    return String(tutorial.steps[0]);
  }

  return "";
}

function sourceItemHtml(source) {
  const title = escapeHtml(source.source_title || "Без названия");
  const sectionPath = escapeHtml(source.section_path || "Раздел не указан");
  const sourceUrl = source.source_url || "";
  const corpus = escapeHtml(source.corpus_type || "unknown");
  const role = escapeHtml(source.source_role || "base");

  const urlHtml = sourceUrl.startsWith("http")
    ? `<a class="source-item-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(sourceUrl)}</a>`
    : "<span class=\"source-item-link muted\">URL отсутствует</span>";

  const corpusClass = source.corpus_type === "supplementary" ? "badge-source-supplementary" : "badge-source-official";

  return `
    <li class="history-source-item">
      <div class="history-source-top">
        <span class="history-source-title">${title}</span>
        <div class="history-source-tags">
          <span class="source-tag ${corpusClass}">${corpus}</span>
          <span class="source-tag source-tag-role">${role}</span>
        </div>
      </div>
      <p class="history-source-path">${sectionPath}</p>
      ${urlHtml}
    </li>
  `;
}

function renderHistory(items) {
  historyList.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    historyList.innerHTML = '<div class="history-empty-state">История запросов пока пуста</div>';
    return;
  }

  items.forEach((item) => {
    const modeLabel = MODE_LABELS[item.mode] || item.mode;
    const statusLabel = STATUS_LABELS[item.status] || item.status || "unknown";
    const statusClass = item.status === "success" ? "badge-success" : "badge-error";
    const versionLabel = item.pg_version ? `PostgreSQL ${item.pg_version}` : "Версия не указана";

    const preview = getPreview(item);

    let extendedBadge = '<span class="badge badge-muted">Расширенный режим: недоступен</span>';
    if (item.mode === "tutorial") {
      extendedBadge = item.extended_mode
        ? '<span class="badge badge-warning">Расширенный режим: включён</span>'
        : '<span class="badge badge-outline">Расширенный режим: выключен</span>';
    }

    const sources = Array.isArray(item.sources) ? item.sources : [];
    const sourcesHtml = sources.length
      ? `
        <details class="history-sources-details">
          <summary>Источники (${sources.length})</summary>
          <ul class="history-sources-list">
            ${sources.map(sourceItemHtml).join("")}
          </ul>
        </details>
      `
      : "";

    const article = document.createElement("article");
    article.className = "history-item";
    article.innerHTML = `
      <div class="history-item-top">
        <div class="history-item-meta-left">
          <span class="badge badge-default">${escapeHtml(modeLabel)}</span>
          <span class="badge badge-outline">${escapeHtml(versionLabel)}</span>
        </div>
        <time class="history-item-time">${escapeHtml(formatDate(item.created_at))}</time>
      </div>

      <p class="history-item-question">${escapeHtml(item.user_question || "")}</p>

      ${preview ? `<p class="history-item-preview">${escapeHtml(preview)}</p>` : ""}

      <div class="history-item-flags">
        <span class="badge ${statusClass}">${escapeHtml(statusLabel)}</span>
        ${extendedBadge}
      </div>

      ${sourcesHtml}
    `;

    historyList.appendChild(article);
  });
}

async function loadHistory() {
  refreshBtn.disabled = true;

  try {
    const response = await fetch("/api/history?limit=100");
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload?.detail || "Не удалось загрузить историю запросов.");
    }

    renderHistory(payload.items || []);
  } catch (error) {
    historyList.innerHTML = `<div class="alert alert-error">${escapeHtml(error.message || "Ошибка загрузки")}</div>`;
  } finally {
    refreshBtn.disabled = false;
  }
}

refreshBtn.addEventListener("click", loadHistory);
loadHistory();
