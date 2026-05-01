const panels = {
  "ask-panel": "Ask your corpus",
  "ingest-panel": "Ingest documents",
  "evaluate-panel": "Evaluate pipeline",
  "metrics-panel": "Monitor metrics",
};

const $ = (selector) => document.querySelector(selector);

const toast = (message) => {
  const node = $("#toast");
  node.textContent = message;
  node.classList.add("show");
  window.setTimeout(() => node.classList.remove("show"), 3200);
};

const setBusy = (button, busy, label) => {
  if (!button) return;
  button.disabled = busy;
  if (busy) {
    button.dataset.label = button.textContent;
    button.textContent = label;
  } else {
    button.textContent = button.dataset.label || button.textContent;
  }
};

const asJson = (value) => JSON.stringify(value, null, 2);

const renderList = (node, items) => {
  node.innerHTML = "";
  (items || []).filter(Boolean).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = typeof item === "string" ? item : asJson(item);
    node.appendChild(li);
  });
};

const renderSnippets = (docs) => {
  const container = $("#retrieved-docs");
  container.innerHTML = "";
  (docs || []).forEach((doc, index) => {
    const snippet = document.createElement("div");
    snippet.className = "snippet";
    snippet.textContent = `${index + 1}. ${doc}`;
    container.appendChild(snippet);
  });
  if (!container.children.length) {
    container.innerHTML = '<div class="snippet empty-state">No retrieved snippets returned.</div>';
  }
};

const qualityClass = (score) => {
  const value = Number(score);
  if (Number.isNaN(value)) return "muted";
  if (value >= 0.75) return "good";
  if (value >= 0.45) return "warn";
  return "bad";
};

const metricCard = (label, value, detail = "") => `
  <article class="metric-card">
    <span>${label}</span>
    <strong>${value === undefined || value === null ? "n/a" : value}</strong>
    ${detail ? `<p>${detail}</p>` : ""}
  </article>
`;

const parsePrometheusMetrics = (text) => {
  const wanted = [
    "rag_requests_total",
    "rag_request_errors_total",
    "rag_grounded_total",
    "rag_ungrounded_total",
    "rag_retrieval_accuracy",
    "rag_answer_quality_score",
    "rag_pdf_total_ingestion_latency_seconds_count",
    "rag_total_latency_seconds_count",
  ];
  const values = new Map();

  text.split("\n").forEach((line) => {
    if (!line || line.startsWith("#")) return;
    const match = line.match(/^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{[^}]*\})?\s+(.+)$/);
    if (!match) return;
    const [, name, rawValue] = match;
    if (wanted.includes(name) && !values.has(name)) {
      values.set(name, rawValue.trim());
    }
  });

  return wanted.map((name) => ({
    name,
    value: values.get(name) || "0",
  }));
};

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((panel) => panel.classList.remove("active-panel"));
    button.classList.add("active");
    $(`#${button.dataset.target}`).classList.add("active-panel");
    $("#workspace-title").textContent = panels[button.dataset.target];
  });
});

$("#question-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = $("#question-input").value.trim();
  const role = $("#role-input").value.trim();
  if (!question || !role) {
    toast("Question and role are required.");
    return;
  }

  const data = new FormData();
  data.append("question", question);
  data.append("role", role);

  const button = $("#ask-button");
  setBusy(button, true, "Asking...");
  try {
    const response = await fetch("/api/question", {
      method: "POST",
      body: data,
    });
    const payload = await response.json();
    if (!response.ok || payload.error) {
      throw new Error(payload.reason || payload.detail || payload.error || "Question failed");
    }

    $("#answer-output").classList.remove("empty-state");
    $("#answer-output").textContent = payload.answer || "No answer returned.";
    renderList($("#sources-list"), payload.sources);
    renderSnippets(payload.retrieved_docs);
    $("#quality-reason").textContent = payload.answer_quality_reason || "No quality reason returned.";

    const pill = $("#quality-pill");
    const score = payload.answer_quality_score;
    pill.className = `pill ${qualityClass(score)}`;
    pill.textContent = score === undefined ? "No score" : `Score ${score}`;
  } catch (error) {
    toast(error.message);
  } finally {
    setBusy(button, false);
  }
});

$("#clear-answer").addEventListener("click", () => {
  $("#question-input").value = "";
  $("#answer-output").className = "answer-output empty-state";
  $("#answer-output").textContent = "The grounded answer will appear here.";
  $("#quality-reason").textContent = "Waiting for a response.";
  $("#quality-pill").className = "pill muted";
  $("#quality-pill").textContent = "No score";
  $("#sources-list").innerHTML = "";
  $("#retrieved-docs").innerHTML = "";
});

$("#file-input").addEventListener("change", (event) => {
  const file = event.target.files[0];
  $("#file-label").textContent = file ? file.name : "Choose a PDF or ZIP file";
});

$("#ingest-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("#file-input").files[0];
  const role = $("#role-input").value.trim();
  const userId = $("#user-input").value.trim();
  const accessDetails = $("#access-input").value.split(",").map((value) => value.trim()).filter(Boolean);

  if (!file || !role || !userId || !accessDetails.length) {
    toast("File, role, user ID, and access details are required.");
    return;
  }

  const data = new FormData();
  data.append("file", file);
  data.append("user_id", userId);
  data.append("role", role);
  accessDetails.forEach((item) => data.append("access_details", item));

  const button = $("#ingest-button");
  const pill = $("#ingest-pill");
  setBusy(button, true, "Ingesting...");
  pill.className = "pill warn";
  pill.textContent = "Running";

  try {
    const response = await fetch("/api/input-document", {
      method: "POST",
      body: data,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Ingestion failed");
    }
    $("#ingest-output").classList.remove("empty-state");
    $("#ingest-output").textContent = asJson(payload);
    pill.className = "pill good";
    pill.textContent = "Complete";
  } catch (error) {
    pill.className = "pill bad";
    pill.textContent = "Failed";
    toast(error.message);
  } finally {
    setBusy(button, false);
  }
});

$("#reset-ingest").addEventListener("click", () => {
  $("#ingest-form").reset();
  $("#file-label").textContent = "Choose a PDF or ZIP file";
  $("#ingest-output").className = "json-output empty-state";
  $("#ingest-output").textContent = "Upload results will appear here.";
  $("#ingest-pill").className = "pill muted";
  $("#ingest-pill").textContent = "Idle";
});

$("#evaluate-button").addEventListener("click", async () => {
  const button = $("#evaluate-button");
  setBusy(button, true, "Running...");
  try {
    const response = await fetch("/api/evaluate", { method: "POST" });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Evaluation failed");
    }
    $("#evaluation-output").innerHTML = [
      metricCard("Total questions", payload.total_questions),
      metricCard("Correct retrievals", payload.correct_retrievals),
      metricCard("Retrieval accuracy", payload.retrieval_accuracy),
      metricCard("Total quality score", payload.total_quality_score),
      metricCard("Answer quality", Array.isArray(payload.answer_quality) ? payload.answer_quality.length : "n/a", "Items returned by evaluator"),
    ].join("");
  } catch (error) {
    toast(error.message);
  } finally {
    setBusy(button, false);
  }
});

$("#refresh-metrics").addEventListener("click", async () => {
  const button = $("#refresh-metrics");
  setBusy(button, true, "Refreshing...");
  try {
    const response = await fetch("/metrics");
    if (!response.ok) throw new Error("Metrics request failed");
    const metrics = parsePrometheusMetrics(await response.text());
    $("#metrics-output").innerHTML = metrics
      .map((metric) => metricCard(metric.name.replace(/_/g, " "), metric.value))
      .join("");
  } catch (error) {
    toast(error.message);
  } finally {
    setBusy(button, false);
  }
});

const checkApi = async () => {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("offline");
    $("#status-dot").className = "status-dot online";
    $("#status-text").textContent = "API online";
  } catch {
    $("#status-dot").className = "status-dot offline";
    $("#status-text").textContent = "API offline";
  }
};

checkApi();
