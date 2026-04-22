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

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(isoStr) {
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString("ru-RU", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoStr;
  }
}

function sourceItemHtml(source) {
  const title = escapeHtml(source.source_title || source.title || "");
  const section = escapeHtml(source.section_path || "");
  const url = source.source_url || source.url || "";
  const corpusType = escapeHtml(source.corpus_type || "");
  const sourceRole = escapeHtml(source.source_role || "");

  let linkHtml = "";
  if (url.startsWith("http")) {
    linkHtml = ` &middot; <a class="source-item-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">Источник</a>`;
  }

  return `<li>${title}<br/><span style="color:var(--color-text-muted);font-size:0.8rem;">${section}${linkHtml}</span><br/><span style="color:var(--color-text-secondary);font-size:0.78rem;">Тип корпуса: ${corpusType} · Роль: ${sourceRole}</span></li>`;
}

function renderHistory(items) {
  historyList.innerHTML = "";

  if (!items.length) {
    historyList.innerHTML = '<div class="history-empty">Запросов пока нет</div>';
    return;
  }

  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "history-item fade-in";

    const modeLabel = MODE_LABELS[item.mode] || item.mode;
    const statusLabel = STATUS_LABELS[item.status] || item.status;
    const statusClass = item.status === "success" ? "badge-success" : "badge-error";
    const version = item.pg_version || "—";
    const extendedBadge = item.mode === "tutorial"
      ? `<span class="badge badge-warning">Расширенный учебный режим: ${item.extended_mode ? "вкл" : "выкл"}</span>`
      : `<span class="badge badge-outline">Расширенный учебный режим: недоступен</span>`;

    const preview = item.mode === "answer"
      ? (item.answer_text || "")
      : (item.tutorial_json?.short_explanation || "");

    const sourcesCount = (item.sources || []).length;
    const sourcesHtml = sourcesCount > 0
      ? `<details>
           <summary>Материалы (${sourcesCount})</summary>
           <ul class="history-sources-list">
             ${item.sources.map(sourceItemHtml).join("")}
           </ul>
         </details>`
      : "";

    article.innerHTML = `
      <div class="history-item-header">
        <span class="badge badge-default">${escapeHtml(modeLabel)}</span>
        <span class="badge badge-outline">PostgreSQL ${escapeHtml(version)}</span>
        ${extendedBadge}
        <span class="badge ${statusClass}">${escapeHtml(statusLabel)}</span>
        <span class="history-item-time">${formatDate(item.created_at)}</span>
      </div>
      <div class="history-item-question">${escapeHtml(item.user_question)}</div>
      ${preview ? `<div class="history-item-preview">${escapeHtml(preview)}</div>` : ""}
      ${sourcesHtml}
    `;

    historyList.appendChild(article);
  });
}

async function loadHistory() {
  refreshBtn.disabled = true;
  try {
    const response = await fetch("/api/history?limit=100");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Не удалось загрузить историю");
    }
    renderHistory(data.items || []);
  } catch (err) {
    historyList.innerHTML = `<div class="alert alert-error">${escapeHtml(err.message || "Ошибка загрузки")}</div>`;
  } finally {
    refreshBtn.disabled = false;
  }
}

refreshBtn.addEventListener("click", loadHistory);
loadHistory();
