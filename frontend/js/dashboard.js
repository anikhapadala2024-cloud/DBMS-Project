/**
 * AgriTech Dashboard Analytics & Chart.js Visualizer
 */

let charts = {};

document.addEventListener("DOMContentLoaded", async () => {
  await loadDashboardData();
  await loadActiveBatches();
});

async function loadDashboardData() {
  try {
    const res = await api.get("/analytics/dashboard");
    if (!res.success || !res.data) return;

    const data = res.data;

    // 1. Populate KPI Cards
    document.getElementById("kpiFarmers").textContent = data.kpis.total_farmers ?? 0;
    document.getElementById("kpiFields").textContent = data.kpis.total_fields ?? 0;
    document.getElementById("kpiActiveBatches").textContent = data.kpis.active_batches ?? 0;
    document.getElementById("kpiCompletedBatches").textContent = data.kpis.completed_batches ?? 0;
    document.getElementById("kpiProduction").textContent = (data.kpis.total_production || 0).toLocaleString() + " Q";
    document.getElementById("kpiAvgYield").textContent = (data.kpis.avg_yield || 0).toLocaleString() + " Q";

    // 2. Render 4 Chart.js Charts
    renderCropProductionChart(data.crop_production_chart);
    renderBatchStatusChart(data.batch_status_chart);
    renderYieldTrendChart(data.yield_trend_chart);
    renderResourceUtilChart(data.resource_utilization_chart);

    // 3. Render Recent Activities
    renderRecentActivities(data.recent_activities);
  } catch (err) {
    showToast("Failed to load dashboard metrics: " + err.message, "error");
  }
}

function renderCropProductionChart(chartData) {
  const ctx = document.getElementById("cropProductionChart")?.getContext("2d");
  if (!ctx) return;

  if (charts.cropProduction) charts.cropProduction.destroy();

  charts.cropProduction = new Chart(ctx, {
    type: "bar",
    data: {
      labels: chartData.labels || [],
      datasets: [{
        label: "Total Harvested Yield (Quintals/Units)",
        data: chartData.data || [],
        backgroundColor: "rgba(30, 126, 52, 0.75)",
        borderColor: "#1b5e20",
        borderWidth: 1.5,
        borderRadius: 8,
        hoverBackgroundColor: "rgba(22, 101, 52, 0.9)"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1e293b",
          titleFont: { family: "Plus Jakarta Sans", size: 13, weight: "bold" },
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#f1f5f9" },
          ticks: { font: { family: "Plus Jakarta Sans" } }
        },
        x: {
          grid: { display: false },
          ticks: { font: { family: "Plus Jakarta Sans" } }
        }
      }
    }
  });
}

function renderBatchStatusChart(chartData) {
  const ctx = document.getElementById("batchStatusChart")?.getContext("2d");
  if (!ctx) return;

  if (charts.batchStatus) charts.batchStatus.destroy();

  const colors = [
    "#94a3b8", // Planned (Slate)
    "#0284c7", // Planted (Sky Blue)
    "#16a34a", // Growing (Green)
    "#d97706", // Ready for Harvest (Amber)
    "#059669"  // Harvested (Emerald)
  ];

  charts.batchStatus = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: chartData.labels || [],
      datasets: [{
        data: chartData.data || [],
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: "#ffffff",
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "right",
          labels: {
            boxWidth: 14,
            font: { family: "Plus Jakarta Sans", size: 12 }
          }
        },
        tooltip: {
          backgroundColor: "#1e293b",
          cornerRadius: 8,
          padding: 10
        }
      },
      cutout: "68%"
    }
  });
}

function renderYieldTrendChart(chartData) {
  const ctx = document.getElementById("yieldTrendChart")?.getContext("2d");
  if (!ctx) return;

  if (charts.yieldTrend) charts.yieldTrend.destroy();

  charts.yieldTrend = new Chart(ctx, {
    type: "line",
    data: {
      labels: chartData.labels && chartData.labels.length ? chartData.labels : ["Past Seasons"],
      datasets: [{
        label: "Harvest Yield Trend",
        data: chartData.data && chartData.data.length ? chartData.data : [0],
        borderColor: "#059669",
        backgroundColor: "rgba(5, 150, 105, 0.12)",
        fill: true,
        tension: 0.35,
        borderWidth: 3,
        pointBackgroundColor: "#059669",
        pointBorderColor: "#ffffff",
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1e293b",
          cornerRadius: 8,
          padding: 10
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#f1f5f9" }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderResourceUtilChart(chartData) {
  const ctx = document.getElementById("resourceUtilChart")?.getContext("2d");
  if (!ctx) return;

  if (charts.resourceUtil) charts.resourceUtil.destroy();

  const colors = ["#0ea5e9", "#10b981", "#ef4444", "#f59e0b"];

  charts.resourceUtil = new Chart(ctx, {
    type: "bar",
    data: {
      labels: chartData.labels || [],
      datasets: [{
        label: "Resource Consumption / Activity Output",
        data: chartData.data || [],
        backgroundColor: colors,
        borderRadius: 8,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#1e293b",
          cornerRadius: 8,
          padding: 10
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#f1f5f9" }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

function renderRecentActivities(activities) {
  const container = document.getElementById("recentActivitiesList");
  if (!container) return;

  if (!activities || activities.length === 0) {
    container.innerHTML = '<p class="text-muted text-center py-4">No cultivation activities logged yet.</p>';
    return;
  }

  const typeIcons = {
    "Irrigation": { icon: "fa-tint", bg: "#e0f2fe", color: "#0284c7" },
    "Fertilization": { icon: "fa-leaf", bg: "#dcfce7", color: "#16a34a" },
    "Pest/Disease": { icon: "fa-bug", bg: "#fee2e2", color: "#dc2626" },
    "Harvesting": { icon: "fa-tractor", bg: "#fef3c7", color: "#d97706" }
  };

  container.innerHTML = activities.map(a => {
    const meta = typeIcons[a.activity_type] || { icon: "fa-seedling", bg: "#f1f5f9", color: "#64748b" };
    return `
      <div class="d-flex align-items-start gap-3 p-2 rounded" style="transition: background 0.2s ease;">
        <div class="stat-icon" style="width: 38px; height: 38px; min-width: 38px; background: ${meta.bg}; color: ${meta.color}; font-size: 1rem;">
          <i class="fas ${meta.icon}"></i>
        </div>
        <div class="flex-grow-1 overflow-hidden">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="fw-bold small text-dark">${a.activity_type}</span>
            <span class="text-muted" style="font-size: 0.75rem;">${a.activity_date || ""}</span>
          </div>
          <div class="small text-muted text-truncate" title="${a.description}">${a.description}</div>
          <div class="d-flex gap-2 mt-1" style="font-size: 0.75rem;">
            <span class="badge bg-light text-secondary border">${a.batch_code}</span>
            <span class="fw-bold text-success">${a.quantity_used} ${a.unit}</span>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

async function loadActiveBatches() {
  const tbody = document.getElementById("activeBatchesTableBody");
  if (!tbody) return;

  try {
    const res = await api.get("/batches");
    if (!res.success || !res.data) return;

    // Filter to active batches (status != Harvested) and take up to 6
    const active = res.data.filter(b => b.status !== "Harvested").slice(0, 6);

    if (active.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">No active batches right now. All batches harvested or none planned.</td></tr>';
      return;
    }

    tbody.innerHTML = active.map(b => {
      const statusClass = "status-" + b.status.replace(/ /g, "-");
      return `
        <tr>
          <td>
            <a href="batches.html?search=${encodeURIComponent(b.batch_code)}" class="fw-bold text-success">${b.batch_code}</a>
          </td>
          <td>
            <div class="fw-semibold">${b.crop_name}</div>
            <div class="small text-muted">${b.crop_type}</div>
          </td>
          <td>
            <div>${b.field_name}</div>
            <div class="small text-muted">${b.farmer_name}</div>
          </td>
          <td>
            <span class="badge-status ${statusClass}">${b.status}</span>
          </td>
          <td class="text-muted small">${b.expected_harvest_date || "--"}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-danger">Error loading batches: ${err.message}</td></tr>`;
  }
}
