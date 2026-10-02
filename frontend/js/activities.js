/**
 * AgriTech Cultivation Activity Management Script
 */

let activityModalInstance = null;
let batchesList = [];

document.addEventListener("DOMContentLoaded", async () => {
  activityModalInstance = new bootstrap.Modal(document.getElementById("activityModal"));

  // Check URL param for pre-filtering or auto-selecting batch
  const urlParams = new URLSearchParams(window.location.search);
  const batchIdParam = urlParams.get("batch_id");

  await loadBatchesDropdown();

  if (batchIdParam) {
    document.getElementById("filterBatchSelect").value = batchIdParam;
  }

  await loadActivities();
});

async function loadBatchesDropdown() {
  try {
    const res = await api.get("/batches");
    if (res.success && res.data) {
      batchesList = res.data;
      const filterSelect = document.getElementById("filterBatchSelect");
      const modalSelect = document.getElementById("activityBatchSelect");

      let filterHtml = '<option value="">All Crop Batches</option>';
      let modalHtml = '<option value="">Select Batch...</option>';

      batchesList.forEach(b => {
        const opt = `<option value="${b.batch_id}">${b.batch_code} - ${b.crop_name} (${b.farmer_name})</option>`;
        filterHtml += opt;
        modalHtml += opt;
      });

      if (filterSelect) filterSelect.innerHTML = filterHtml;
      if (modalSelect) modalSelect.innerHTML = modalHtml;
    }
  } catch (err) {
    console.error("Error loading batches:", err);
  }
}

function resetActivityFilters() {
  document.getElementById("filterBatchSelect").value = "";
  document.getElementById("filterTypeSelect").value = "";
  document.getElementById("filterDateFrom").value = "";
  document.getElementById("filterDateTo").value = "";
  loadActivities();
}

function onActivityTypeChange() {
  const type = document.getElementById("activityTypeSelect").value;
  const unitInput = document.getElementById("activityUnit");
  const descInput = document.getElementById("activityDescription");

  if (type === "Irrigation") {
    unitInput.value = "Liters";
    descInput.placeholder = "e.g. Drip irrigation for root zone / flood irrigation canal water";
  } else if (type === "Fertilization") {
    unitInput.value = "Kg";
    descInput.placeholder = "e.g. NPK 12:32:16 application / Urea top dressing";
  } else if (type === "Pest/Disease") {
    unitInput.value = "Liters";
    descInput.placeholder = "e.g. Observed aphid infestation; sprayed organic neem oil / chemical treatment";
  } else if (type === "Harvesting") {
    unitInput.value = "Quintals";
    descInput.placeholder = "e.g. Manual hand picking / combine harvester output yield";
  }
}

async function loadActivities() {
  const batch_id = document.getElementById("filterBatchSelect")?.value || "";
  const activity_type = document.getElementById("filterTypeSelect")?.value || "";
  const date_from = document.getElementById("filterDateFrom")?.value || "";
  const date_to = document.getElementById("filterDateTo")?.value || "";

  const tbody = document.getElementById("activitiesTableBody");
  tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Loading activities...</td></tr>';

  try {
    const params = {};
    if (batch_id) params.batch_id = batch_id;
    if (activity_type) params.activity_type = activity_type;
    if (date_from) params.date_from = date_from;
    if (date_to) params.date_to = date_to;

    const res = await api.get("/activities", params);
    if (!res.success || !res.data) return;

    const activities = res.data;
    if (activities.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No cultivation activities found matching criteria.</td></tr>';
      return;
    }

    const typeBadges = {
      "Irrigation": "bg-info-subtle text-info border-info-subtle",
      "Fertilization": "bg-success-subtle text-success border-success-subtle",
      "Pest/Disease": "bg-danger-subtle text-danger border-danger-subtle",
      "Harvesting": "bg-warning-subtle text-warning-emphasis border-warning-subtle"
    };

    tbody.innerHTML = activities.map(a => `
      <tr>
        <td class="fw-bold text-muted">#${a.activity_id}</td>
        <td>
          <div class="fw-semibold text-dark">${a.activity_date}</div>
        </td>
        <td>
          <span class="badge border ${typeBadges[a.activity_type] || 'bg-light text-dark'}">
            ${a.activity_type}
          </span>
        </td>
        <td>
          <a href="batches.html?search=${encodeURIComponent(a.batch_code)}" class="fw-bold text-success">
            ${a.batch_code}
          </a>
        </td>
        <td>
          <div>${a.crop_name}</div>
          <div class="small text-muted">${a.farmer_name}</div>
        </td>
        <td>
          <span class="fw-bold text-dark">${a.quantity_used} ${a.unit}</span>
        </td>
        <td class="small text-muted" style="max-width: 250px;" title="${a.description}">
          ${a.description}
        </td>
        <td class="text-end">
          <div class="d-inline-flex gap-1">
            <button class="btn-action-icon" title="Edit Activity" onclick="openEditActivityModal(${JSON.stringify(a).replace(/"/g, '&quot;')})">
              <i class="fas fa-edit text-success"></i>
            </button>
            <button class="btn-action-icon btn-action-delete" title="Delete Activity" onclick="deleteActivity(${a.activity_id})">
              <i class="fas fa-trash-alt text-danger"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-danger">Failed to load activities: ${err.message}</td></tr>`;
  }
}

function openAddActivityModal() {
  document.getElementById("activityForm").reset();
  document.getElementById("activityId").value = "";
  document.getElementById("activityDate").valueAsDate = new Date();
  document.getElementById("activityCropName").value = "";
  
  // Pre-select batch if filter is set
  const filterBatch = document.getElementById("filterBatchSelect").value;
  if (filterBatch) {
    document.getElementById("activityBatchSelect").value = filterBatch;
  }

  onActivityTypeChange();
  document.getElementById("activityModalTitle").innerHTML = '<i class="fas fa-clipboard-check me-2 text-success"></i>Log Cultivation Activity';
  activityModalInstance.show();
}

function openEditActivityModal(activity) {
  document.getElementById("activityId").value = activity.activity_id;
  document.getElementById("activityBatchSelect").value = activity.batch_id;
  document.getElementById("activityCropName").value = activity.crop_name || "";
  document.getElementById("activityTypeSelect").value = activity.activity_type;
  document.getElementById("activityDate").value = activity.activity_date;
  document.getElementById("activityQuantity").value = activity.quantity_used;
  document.getElementById("activityUnit").value = activity.unit;
  document.getElementById("activityDescription").value = activity.description;
  document.getElementById("activityModalTitle").innerHTML = '<i class="fas fa-edit me-2 text-success"></i>Edit Cultivation Activity';
  activityModalInstance.show();
}

async function saveActivity(e) {
  e.preventDefault();
  const id = document.getElementById("activityId").value;
  const batch_id = document.getElementById("activityBatchSelect").value;
  const crop_name = document.getElementById("activityCropName").value.trim();
  const activity_type = document.getElementById("activityTypeSelect").value;
  const activity_date = document.getElementById("activityDate").value;
  const quantity_used = document.getElementById("activityQuantity").value;
  const unit = document.getElementById("activityUnit").value.trim();
  const description = document.getElementById("activityDescription").value.trim();

  const btn = document.getElementById("saveActivityBtn");
  btn.disabled = true;

  try {
    const payload = { batch_id: batch_id || null, crop_name: crop_name || null, activity_type, activity_date, quantity_used, unit, description };

    if (id) {
      const res = await api.put(`/activities/${id}`, payload);
      showToast(res.message || "Activity updated successfully");
    } else {
      const res = await api.post("/activities", payload);
      showToast(res.message || "Activity recorded successfully");
    }
    activityModalInstance.hide();
    loadActivities();
  } catch (err) {
    showToast(err.message || "Error saving activity", "error");
  } finally {
    btn.disabled = false;
  }
}

async function deleteActivity(activityId) {
  if (!confirm("Are you sure you want to delete this activity log?")) return;

  try {
    const res = await api.delete(`/activities/${activityId}`);
    showToast(res.message || "Activity deleted successfully");
    loadActivities();
  } catch (err) {
    showToast(err.message || "Failed to delete activity", "error");
  }
}

async function exportActivitiesCsv() {
  const batch_id = document.getElementById("filterBatchSelect")?.value || "";
  const activity_type = document.getElementById("filterTypeSelect")?.value || "";

  try {
    const params = {};
    if (batch_id) params.batch_id = batch_id;
    if (activity_type) params.activity_type = activity_type;

    const blob = await api.get("/analytics/export-activities", params);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `cultivation_activities_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast("Activities CSV downloaded successfully!");
  } catch (err) {
    showToast("Export failed: " + err.message, "error");
  }
}
