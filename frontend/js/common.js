/**
 * AgriTech Common UI Components & Helpers
 * Injects sidebar, navbar, toasts, and shared formatters.
 */

let assistantHistory = [];

document.addEventListener("DOMContentLoaded", () => {
  const user = auth.checkAuth();
  if (user) {
    renderSidebar(user);
    renderTopbar(user);
    renderAssistantWidget(user);
    auth.applyRoleRestrictions(user);
  }
});

function renderSidebar(user) {
  const sidebarContainer = document.getElementById("app-sidebar-container");
  if (!sidebarContainer) return;

  const currentPath = window.location.pathname;
  const isAdmin = user.role === "admin";

  const navItems = [
    { label: "Dashboard", href: "dashboard.html", icon: "fa-tachometer-alt" },
    { label: isAdmin ? "Farmers" : "My Farm Profile", href: "farmers.html", icon: "fa-users" },
    { label: isAdmin ? "Fields" : "My Fields", href: "fields.html", icon: "fa-map-marked-alt" },
    { label: isAdmin ? "Crops" : "Crop Guide", href: "crops.html", icon: "fa-seedling" },
    { label: isAdmin ? "Crop Batches" : "My Crop Batches", href: "batches.html", icon: "fa-layer-group" },
    { label: isAdmin ? "Activities" : "My Activity Log", href: "activities.html", icon: "fa-clipboard-check" },
    { label: isAdmin ? "Analytics" : "My Farm Insights", href: "analytics.html", icon: "fa-chart-line" },
    ...(isAdmin ? [{ label: "Users", href: "users.html", icon: "fa-user-shield", role: "admin" }] : [])
  ];

  const navHtml = navItems.map(item => {
    const isActive = currentPath.endsWith(item.href) ? "active" : "";
    return `
      <a href="${item.href}" class="nav-link-custom ${isActive}">
        <i class="fas ${item.icon}"></i>
        <span>${item.label}</span>
      </a>
    `;
  }).join("");

  const initials = user.name ? user.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() : "AG";
  const roleClass = user.role === "admin" ? "role-admin" : "role-farmer";

  sidebarContainer.innerHTML = `
    <aside class="app-sidebar" id="mainSidebar">
      <div class="sidebar-brand">
        <div class="brand-icon"><i class="fas fa-leaf"></i></div>
        <div>
          <div class="brand-title">AgriTech</div>
          <div class="brand-sub">Crop Batch Portal</div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-category">Main Navigation</div>
        ${navHtml}
        <div class="nav-category" style="margin-top: auto;">Account</div>
        <a href="#" onclick="auth.logout(); return false;" class="nav-link-custom" style="color: #dc2626;">
          <i class="fas fa-sign-out-alt" style="color: #dc2626;"></i>
          <span>Logout</span>
        </a>
      </nav>
      <div class="sidebar-user">
        <div class="user-card-mini">
          <div class="avatar-circle">${initials}</div>
          <div class="user-info-text">
            <div class="user-name-display" title="${user.name}">${user.name}</div>
            <span class="user-role-badge ${roleClass}">${user.role}</span>
          </div>
        </div>
      </div>
    </aside>
  `;
}

function renderTopbar(user) {
  const topbarContainer = document.getElementById("app-topbar-container");
  if (!topbarContainer) return;

  const isAdmin = user.role === "admin";
  const initials = user.name ? user.name.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase() : "AG";
  const roleClass = user.role === "admin" ? "role-admin" : "role-farmer";

  topbarContainer.innerHTML = `
    <header class="app-topbar">
      <div class="topbar-left">
        <button class="sidebar-toggle-btn" id="sidebarToggle" onclick="toggleSidebar()">
          <i class="fas fa-bars"></i>
        </button>
        <div class="topbar-search">
          <i class="fas fa-search"></i>
          <input type="text" id="globalSearchInput" placeholder="${isAdmin ? "Search batches, crops, farmers..." : "Search my batches and crops..."}" onkeydown="handleGlobalSearch(event)">
        </div>
      </div>
      <div class="topbar-right">
        <button class="topbar-icon-btn" title="Live Database Status" onclick="checkBackendStatus()">
          <i class="fas fa-database text-success"></i>
        </button>
        <div class="dropdown">
          <div class="d-flex align-items-center gap-2" style="cursor: pointer;" data-bs-toggle="dropdown" aria-expanded="false">
            <div class="avatar-circle" style="width: 38px; height: 38px;">${initials}</div>
            <div class="d-none d-md-block text-start">
              <div class="fw-bold small lh-1">${user.name}</div>
              <span class="user-role-badge ${roleClass}" style="font-size: 0.65rem;">${user.role}</span>
            </div>
            <i class="fas fa-chevron-down text-muted small ms-1"></i>
          </div>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm">
            <li><h6 class="dropdown-header">${user.email}</h6></li>
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item" href="dashboard.html"><i class="fas fa-tachometer-alt me-2 text-muted"></i>Dashboard</a></li>
            <li><a class="dropdown-item text-danger" href="#" onclick="auth.logout(); return false;"><i class="fas fa-sign-out-alt me-2"></i>Sign Out</a></li>
          </ul>
        </div>
      </div>
    </header>
  `;
}

function renderAssistantWidget(user) {
  const widget = document.createElement("div");
  widget.className = "assistant-widget";
  widget.innerHTML = `
    <section class="assistant-panel" id="assistantPanel" aria-label="AgriTech Assistant" hidden>
      <header class="assistant-header">
        <div>
          <h2>AgriTech Assistant</h2>
          <p>${user.role === "admin" ? "Farm records and management support" : "Your fields and cultivation guidance"}</p>
        </div>
        <button type="button" class="assistant-close" onclick="toggleAssistant()" aria-label="Close assistant">
          <i class="fas fa-times"></i>
        </button>
      </header>
      <div class="assistant-messages" id="assistantMessages" role="log" aria-live="polite"></div>
      <form class="assistant-form" onsubmit="sendAssistantMessage(event)">
        <input id="assistantInput" type="text" maxlength="1500" autocomplete="off" placeholder="${user.role === "admin" ? "Ask about any farmer or farm operations..." : "Ask about your farm..."}" aria-label="Your question" required>
        <button type="submit" id="assistantSend" title="Send question" aria-label="Send question">
          <i class="fas fa-paper-plane"></i>
        </button>
      </form>
      <p class="assistant-footnote">Local AI is optional. If Ollama is offline, the assistant stays helpful with field guidance.</p>
    </section>
    <button type="button" class="assistant-toggle" id="assistantToggle" onclick="toggleAssistant()" aria-expanded="false" aria-controls="assistantPanel" title="Ask the AgriTech assistant">
      <i class="fas fa-comment-dots"></i>
      <span class="visually-hidden">Ask the AgriTech assistant</span>
    </button>
  `;
  document.body.appendChild(widget);
  const greeting = user.role === "admin"
    ? `Hello ${user.name}. Ask about farmers, farm records, or management.`
    : `Hello ${user.name}. Ask about your fields or cultivation.`;
  appendAssistantMessage(greeting, "assistant");
}

function toggleAssistant() {
  const panel = document.getElementById("assistantPanel");
  const toggle = document.getElementById("assistantToggle");
  if (!panel || !toggle) return;

  panel.hidden = !panel.hidden;
  toggle.setAttribute("aria-expanded", String(!panel.hidden));
  if (!panel.hidden) document.getElementById("assistantInput")?.focus();
}

function appendAssistantMessage(content, role) {
  const messages = document.getElementById("assistantMessages");
  const message = document.createElement("div");
  message.className = `assistant-message assistant-message-${role}`;
  message.textContent = content;
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
  return message;
}

async function sendAssistantMessage(event) {
  event.preventDefault();
  const input = document.getElementById("assistantInput");
  const sendButton = document.getElementById("assistantSend");
  const question = input.value.trim();
  if (!question) return;

  const priorHistory = assistantHistory.slice(-8);
  assistantHistory.push({ role: "user", content: question });
  appendAssistantMessage(question, "user");
  input.value = "";
  sendButton.disabled = true;
  const pending = appendAssistantMessage("Thinking...", "assistant");

  try {
    const response = await api.post("/assistant/chat", { question, history: priorHistory });
    pending.textContent = response.data.answer;
    assistantHistory.push({ role: "assistant", content: response.data.answer });
    assistantHistory = assistantHistory.slice(-8);
  } catch (error) {
    pending.textContent = error.message || "The assistant is unavailable right now.";
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById("mainSidebar");
  if (sidebar) {
    sidebar.classList.toggle("show-sidebar");
  }
}

function handleGlobalSearch(e) {
  if (e.key === "Enter") {
    const q = e.target.value.trim();
    if (q) {
      window.location.href = `batches.html?search=${encodeURIComponent(q)}`;
    }
  }
}

async function checkBackendStatus() {
  const motivationalQuotes = [
    "Every seed you plant is a promise of a brighter harvest.",
    "Your work keeps the nation fed and the future growing.",
    "Strong farmers build resilient communities and better harvests.",
    "You are shaping the soil, the future, and the economy with every field.",
    "A farmer's discipline turns effort into abundance season after season."
  ];

  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const quote = motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];
    showToast(`${quote} • Status: ${data.status.toUpperCase()} | DB: ${data.database_engine.toUpperCase()}`, "success");
  } catch (err) {
    showToast("Your farm is still strong — the platform is temporarily offline, but the next harvest is on the way.", "warning");
  }
}

/**
 * Toast Notification System
 */
function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  const typeClass = type === "error" ? "toast-error" : (type === "warning" ? "toast-warning" : "");
  const icon = type === "error" ? "fa-exclamation-circle text-danger" : (type === "warning" ? "fa-exclamation-triangle text-warning" : "fa-check-circle text-success");

  toast.className = `agri-toast ${typeClass}`;
  toast.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <i class="fas ${icon} fs-5"></i>
      <div class="small fw-semibold">${message}</div>
    </div>
    <button type="button" class="btn-close ms-2" style="font-size: 0.75rem;" onclick="this.parentElement.remove()"></button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
}

/**
 * Visual Lifecycle Tracker Generator
 */
function generateLifecycleHtml(currentStatus) {
  const stages = [
    { label: "Planting", icon: "fa-seedling", status: "Planned" },
    { label: "Growing", icon: "fa-leaf", status: "Planted" },
    { label: "Cultivation", icon: "fa-tint", status: "Growing" },
    { label: "Ready for Harvest", icon: "fa-sun", status: "Ready for Harvest" },
    { label: "Harvested", icon: "fa-tractor", status: "Harvested" }
  ];

  const statusOrder = {
    "Planned": 1,
    "Planted": 2,
    "Growing": 3,
    "Ready for Harvest": 4,
    "Harvested": 5
  };

  const currentLevel = statusOrder[currentStatus] || 1;
  const fillPercent = ((currentLevel - 1) / (stages.length - 1)) * 100;

  const stepsHtml = stages.map((stage, idx) => {
    const stageLevel = idx + 1;
    let stateClass = "";
    if (stageLevel < currentLevel) stateClass = "completed";
    else if (stageLevel === currentLevel) stateClass = "active";

    return `
      <div class="lifecycle-step ${stateClass}">
        <div class="lifecycle-node">
          <i class="fas ${stage.icon}"></i>
        </div>
        <div class="lifecycle-label">${stage.label}</div>
      </div>
    `;
  }).join("");

  return `
    <div class="lifecycle-tracker">
      <div class="lifecycle-track-bar">
        <div class="lifecycle-track-fill" style="width: ${fillPercent}%;"></div>
      </div>
      ${stepsHtml}
    </div>
  `;
}
