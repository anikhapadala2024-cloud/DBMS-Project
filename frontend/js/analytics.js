/**
 * AgriTech Dedicated Analytics Portal Visualizer
 */

let analyticsCharts = {};

document.addEventListener("DOMContentLoaded", async () => {
  await loadFilterDropdowns();
  await loadAnalyticsData();
});

async function loadFilterDropdowns() {
  try {
    const [cropsRes, farmersRes, fieldsRes] = await Promise.all([
      api.get("/crops"),
      api.get("/farmers", { limit: 100 }),
      api.get("/fields")
    ]);

    if (cropsRes.success) {
      let html = '<option value="">All Crops</option>';
      cropsRes.data.forEach(c => html += `<option value="${c.crop_id}">${c.crop_name}</option>`);
      document.getElementById("analyticsCropSelect").innerHTML = html;
    }

    if (farmersRes.success) {
      let html = '<option value="">All Farmers</option>';
      farmersRes.data.farmers.forEach(f => html += `<option value="${f.farmer_id}">${f.name}</option>`);
      document.getElementById("analyticsFarmerSelect").innerHTML = html;
    }

    if (fieldsRes.success) {
      let html = '<option value="">All Fields</option>';
      fieldsRes.data.forEach(f => html += `<option value="${f.field_id}">${f.field_name}</option>`);
      document.getElementById("analyticsFieldSelect").innerHTML = html;
    }
  } catch (err) {
    console.error("Error loading analytics filters:", err);
  }
}

function resetAnalyticsFilters() {
  document.getElementById("analyticsCropSelect").value = "";
  document.getElementById("analyticsFarmerSelect").value = "";
  document.getElementById("analyticsFieldSelect").value = "";
  document.getElementById("analyticsDateFrom").value = "";
  document.getElementById("analyticsDateTo").value = "";
  loadAnalyticsData();
}

async function loadAnalyticsData() {
  const crop_id = document.getElementById("analyticsCropSelect")?.value || "";
  const farmer_id = document.getElementById("analyticsFarmerSelect")?.value || "";
  const field_id = document.getElementById("analyticsFieldSelect")?.value || "";
  const date_from = document.getElementById("analyticsDateFrom")?.value || "";
  const date_to = document.getElementById("analyticsDateTo")?.value || "";

  try {
    const params = {};
    if (crop_id) params.crop_id = crop_id;
    if (farmer_id) params.farmer_id = farmer_id;
    if (field_id) params.field_id = field_id;
    if (date_from) params.date_from = date_from;
    if (date_to) params.date_to = date_to;

    const [reportsRes, dashRes] = await Promise.all([
      api.get("/analytics/reports", params),
      api.get("/analytics/dashboard")
    ]);

    if (reportsRes.success && reportsRes.data) {
      const r = reportsRes.data;
      document.getElementById("reportTotalBatches").textContent = r.total_batches_analyzed || 0;

      const totalVol = r.farmer_production.data.reduce((acc, v) => acc + v, 0);
      document.getElementById("reportTotalVolume").textContent = totalVol.toLocaleString() + " Q";
      document.getElementById("reportActiveFarmers").textContent = r.farmer_production.labels.length;
      
      const avgY = r.total_batches_analyzed > 0 ? (totalVol / r.total_batches_analyzed).toFixed(1) : 0;
      document.getElementById("reportAvgYield").textContent = avgY + " Q";

      renderFarmerProductionChart(r.farmer_production);
      renderFieldProductionChart(r.field_production);
      renderCropComparisonChart(r.crop_comparison);
    }

    if (dashRes.success && dashRes.data) {
      renderAnalyticsBatchStatusChart(dashRes.data.batch_status_chart);
    }
  } catch (err) {
    showToast("Failed to load analytics: " + err.message, "error");
  }
}

function renderFarmerProductionChart(data) {
  const ctx = document.getElementById("farmerProductionChart")?.getContext("2d");
  if (!ctx) return;

  if (analyticsCharts.farmerProd) analyticsCharts.farmerProd.destroy();

  analyticsCharts.farmerProd = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels && data.labels.length ? data.labels : ["No Data"],
      datasets: [{
        label: "Production (Quintals)",
        data: data.data && data.data.length ? data.data : [0],
        backgroundColor: "rgba(16, 185, 129, 0.75)",
        borderColor: "#059669",
        borderWidth: 1.5,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderFieldProductionChart(data) {
  const ctx = document.getElementById("fieldProductionChart")?.getContext("2d");
  if (!ctx) return;

  if (analyticsCharts.fieldProd) analyticsCharts.fieldProd.destroy();

  analyticsCharts.fieldProd = new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels && data.labels.length ? data.labels : ["No Data"],
      datasets: [{
        label: "Field Harvest (Quintals)",
        data: data.data && data.data.length ? data.data : [0],
        backgroundColor: "rgba(2, 132, 199, 0.75)",
        borderColor: "#0284c7",
        borderWidth: 1.5,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderCropComparisonChart(cropData) {
  const ctx = document.getElementById("cropComparisonChart")?.getContext("2d");
  if (!ctx) return;

  if (analyticsCharts.cropComp) analyticsCharts.cropComp.destroy();

  const labels = cropData.map(c => c.crop_name);
  const expectedData = cropData.map(c => c.expected);
  const actualData = cropData.map(c => c.actual);

  analyticsCharts.cropComp = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels.length ? labels : ["No Data"],
      datasets: [
        {
          label: "Benchmark Expected Yield (Q/Ac)",
          data: expectedData.length ? expectedData : [0],
          backgroundColor: "rgba(148, 163, 184, 0.7)",
          borderRadius: 6
        },
        {
          label: "Average Harvested Yield (Q)",
          data: actualData.length ? actualData : [0],
          backgroundColor: "rgba(30, 126, 52, 0.85)",
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderAnalyticsBatchStatusChart(data) {
  const ctx = document.getElementById("analyticsBatchStatusChart")?.getContext("2d");
  if (!ctx) return;

  if (analyticsCharts.batchStatus) analyticsCharts.batchStatus.destroy();

  const colors = ["#94a3b8", "#0284c7", "#16a34a", "#d97706", "#059669"];

  analyticsCharts.batchStatus = new Chart(ctx, {
    type: "pie",
    data: {
      labels: data.labels || [],
      datasets: [{
        data: data.data || [],
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: "#ffffff"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right" }
      }
    }
  });
}

async function exportAnalyticsReportsCsv() {
  const crop_id = document.getElementById("analyticsCropSelect")?.value || "";
  const farmer_id = document.getElementById("analyticsFarmerSelect")?.value || "";

  try {
    const params = {};
    if (crop_id) params.crop_id = crop_id;
    if (farmer_id) params.farmer_id = farmer_id;

    const blob = await api.get("/analytics/export-batches", params);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analytics_batches_report_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast("Analytics batches report downloaded!");
  } catch (err) {
    showToast("Export error: " + err.message, "error");
  }
}

async function exportActivitiesReportsCsv() {
  try {
    const blob = await api.get("/analytics/export-activities");
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analytics_activities_report_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast("Cultivation activities report downloaded!");
  } catch (err) {
    showToast("Export error: " + err.message, "error");
  }
}
