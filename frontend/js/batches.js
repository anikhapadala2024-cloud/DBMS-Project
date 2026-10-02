/**
 * AgriTech Crop Batches Management & Lifecycle Tracker
 */

let batchModalInstance = null;
let statusModalInstance = null;
let batchDetailsModalInstance = null;
let searchDebounce = null;

let cropsList = [];
let fieldsList = [];
let farmersList = [];

document.addEventListener("DOMContentLoaded", async () => {
  batchModalInstance = new bootstrap.Modal(document.getElementById("batchModal"));
  statusModalInstance = new bootstrap.Modal(document.getElementById("statusModal"));
  batchDetailsModalInstance = new bootstrap.Modal(document.getElementById("batchDetailsModal"));

  // Check URL search parameters
  const urlParams = new URLSearchParams(window.location.search);
  const searchParam = urlParams.get("search");
  if (searchParam) {
    document.getElementById("batchSearchInput").value = searchParam;
  }

  await loadDropdownData();
  await loadBatches();
});

function handleBatchSearch() {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    loadBatches();
  }, 350);
}

function resetFilters() {
  document.getElementById("batchSearchInput").value = "";
  document.getElementById("filterCropSelect").value = "";
  document.getElementById("filterStatusSelect").value = "";
  document.getElementById("filterFarmerSelect").value = "";
  document.getElementById("filterDateFrom").value = "";
  document.getElementById("filterDateTo").value = "";
  loadBatches();
}

async function loadDropdownData() {
  try {
    const [cropsRes, fieldsRes, farmersRes] = await Promise.all([
      api.get("/crops"),
      api.get("/fields"),
      api.get("/farmers", { limit: 100 })
    ]);

    if (cropsRes.success) {
      cropsList = cropsRes.data || [];
      const filterCrop = document.getElementById("filterCropSelect");
      const modalCrop = document.getElementById("batchCropSelect");
      let filterHtml = '<option value="">All Crops</option>';
      let modalHtml = '<option value="">Select Crop...</option>';
      cropsList.forEach(c => {
        const opt = `<option value="${c.crop_id}">${c.crop_name} (${c.crop_type})</option>`;
        filterHtml += opt;
        modalHtml += opt;
      });
      if (filterCrop) filterCrop.innerHTML = filterHtml;
      if (modalCrop) modalCrop.innerHTML = modalHtml;
    }

    if (fieldsRes.success) {
      fieldsList = fieldsRes.data || [];
      const modalField = document.getElementById("batchFieldSelect");
      let modalHtml = '<option value="">Select Field...</option>';
      fieldsList.forEach(f => {
        modalHtml += `<option value="${f.field_id}">${f.field_name} - ${f.farmer_name} (${f.area} ac)</option>`;
      });
      if (modalField) modalField.innerHTML = modalHtml;
    }

    if (farmersRes.success) {
      farmersList = farmersRes.data.farmers || [];
      const filterFarmer = document.getElementById("filterFarmerSelect");
      let filterHtml = '<option value="">All Farmers</option>';
      farmersList.forEach(f => {
        filterHtml += `<option value="${f.farmer_id}">${f.name}</option>`;
      });
      if (filterFarmer) filterFarmer.innerHTML = filterHtml;
    }
  } catch (err) {
    console.error("Error loading dropdowns:", err);
  }
}

async function loadBatches() {
  const search = document.getElementById("batchSearchInput")?.value || "";
  const crop_id = document.getElementById("filterCropSelect")?.value || "";
  const status = document.getElementById("filterStatusSelect")?.value || "";
  const farmer_id = document.getElementById("filterFarmerSelect")?.value || "";
  const date_from = document.getElementById("filterDateFrom")?.value || "";
  const date_to = document.getElementById("filterDateTo")?.value || "";

  const tbody = document.getElementById("batchesTableBody");
  tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Loading batches...</td></tr>';

  try {
    const params = {};
    if (search) params.search = search;
    if (crop_id) params.crop_id = crop_id;
    if (status) params.status = status;
    if (farmer_id) params.farmer_id = farmer_id;
    if (date_from) params.date_from = date_from;
    if (date_to) params.date_to = date_to;

    const res = await api.get("/batches", params);
    if (!res.success || !res.data) return;

    const batches = res.data;
    if (batches.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-muted">No crop batches found matching criteria.</td></tr>';
      return;
    }

    const isAdmin = auth.isAdmin();

    tbody.innerHTML = batches.map(b => {
      const statusClass = "status-" + b.status.replace(/ /g, "-");
      const yieldText = b.yield && b.yield > 0 ? `<strong class="text-success">${b.yield} Q</strong>` : '<span class="text-muted">In Progress</span>';

      return `
        <tr>
          <td>
            <a href="#" onclick="viewBatchDetails(${b.batch_id}); return false;" class="fw-bold text-success text-decoration-underline" title="View details & lifecycle">
              ${b.batch_code}
            </a>
            <div class="small text-muted">${b.quantity} kg planted</div>
          </td>
          <td>
            <div class="fw-semibold text-dark">${b.farmer_name}</div>
          </td>
          <td>
            <div>${b.field_name}</div>
            <div class="small text-muted">${b.field_location}</div>
          </td>
          <td>
            <div class="fw-bold text-dark">${b.crop_name}</div>
            <div class="small text-muted">${b.crop_type}</div>
          </td>
          <td>${b.planting_date}</td>
          <td>
            <div>${b.expected_harvest_date}</div>
            ${b.actual_harvest_date ? `<div class="small text-success fw-bold">Actual: ${b.actual_harvest_date}</div>` : ''}
          </td>
          <td>
            <button class="btn p-0 border-0" onclick="openStatusModal(${JSON.stringify(b).replace(/"/g, '&quot;')})" title="Click to transition lifecycle stage">
              <span class="badge-status ${statusClass}">${b.status} <i class="fas fa-sync-alt ms-1 small opacity-75"></i></span>
            </button>
          </td>
          <td>${yieldText}</td>
          <td class="text-end">
            <div class="d-inline-flex gap-1">
              <button class="btn-action-icon" title="View Batch & Lifecycle" onclick="viewBatchDetails(${b.batch_id})">
                <i class="fas fa-eye text-primary"></i>
              </button>
              <button class="btn-action-icon" title="Update Lifecycle Status" onclick="openStatusModal(${JSON.stringify(b).replace(/"/g, '&quot;')})">
                <i class="fas fa-exchange-alt text-warning"></i>
              </button>
              <a href="activities.html?batch_id=${b.batch_id}" class="btn-action-icon" title="Log/View Activities">
                <i class="fas fa-clipboard-check text-info"></i>
              </a>
              ${isAdmin ? `
                <button class="btn-action-icon" title="Edit Batch" onclick="openEditBatchModal(${JSON.stringify(b).replace(/"/g, '&quot;')})">
                  <i class="fas fa-edit text-success"></i>
                </button>
                <button class="btn-action-icon btn-action-delete" title="Delete Batch" onclick="deleteBatch(${b.batch_id}, '${b.batch_code}')">
                  <i class="fas fa-trash-alt text-danger"></i>
                </button>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-danger">Failed to load crop batches: ${err.message}</td></tr>`;
  }
}

async function autoSuggestBatchCode() {
  const cropId = document.getElementById("batchCropSelect").value;
  if (!cropId) return;
  try {
    const res = await api.get("/batches/generate-code", { crop_id: cropId });
    if (res.success && res.data) {
      document.getElementById("batchCodeInput").value = res.data.batch_code;
    }
  } catch (err) {
    console.error("Error auto-generating code:", err);
  }
}

async function generateBatchCodeClick() {
  const cropId = document.getElementById("batchCropSelect").value;
  await autoSuggestBatchCode();
}

function toggleHarvestFields() {
  const status = document.getElementById("batchStatusSelect").value;
  const isHarvested = status === "Harvested";
  document.getElementById("actualHarvestDateGroup").style.display = isHarvested ? "block" : "none";
  document.getElementById("yieldGroup").style.display = isHarvested ? "block" : "none";
}

function openAddBatchModal() {
  document.getElementById("batchForm").reset();
  document.getElementById("batchId").value = "";
  document.getElementById("batchModalTitle").innerHTML = '<i class="fas fa-layer-group me-2 text-success"></i>Create New Crop Batch';
  document.getElementById("batchPlantingDate").valueAsDate = new Date();
  
  // Set default expected harvest 90 days from today
  const exp = new Date();
  exp.setDate(exp.getDate() + 90);
  document.getElementById("batchExpectedHarvestDate").valueAsDate = exp;

  toggleHarvestFields();
  batchModalInstance.show();
}

function openEditBatchModal(batch) {
  document.getElementById("batchId").value = batch.batch_id;
  document.getElementById("batchCropSelect").value = batch.crop_id;
  document.getElementById("batchFieldSelect").value = batch.field_id;
  document.getElementById("batchCodeInput").value = batch.batch_code;
  document.getElementById("batchQuantityInput").value = batch.quantity;
  document.getElementById("batchPlantingDate").value = batch.planting_date;
  document.getElementById("batchExpectedHarvestDate").value = batch.expected_harvest_date;
  document.getElementById("batchStatusSelect").value = batch.status;

  if (batch.status === "Harvested") {
    document.getElementById("batchActualHarvestDate").value = batch.actual_harvest_date || "";
    document.getElementById("batchYieldInput").value = batch.yield || "";
  }
  toggleHarvestFields();

  document.getElementById("batchModalTitle").innerHTML = '<i class="fas fa-edit me-2 text-success"></i>Edit Crop Batch';
  batchModalInstance.show();
}

async function saveBatch(e) {
  e.preventDefault();
  const id = document.getElementById("batchId").value;
  const crop_id = document.getElementById("batchCropSelect").value;
  const field_id = document.getElementById("batchFieldSelect").value;
  const batch_code = document.getElementById("batchCodeInput").value.trim();
  const quantity = document.getElementById("batchQuantityInput").value;
  const planting_date = document.getElementById("batchPlantingDate").value;
  const expected_harvest_date = document.getElementById("batchExpectedHarvestDate").value;
  const status = document.getElementById("batchStatusSelect").value;
  const actual_harvest_date = document.getElementById("batchActualHarvestDate").value;
  const yield_amount = document.getElementById("batchYieldInput").value;

  const btn = document.getElementById("saveBatchBtn");
  btn.disabled = true;

  try {
    const payload = {
      crop_id,
      field_id,
      batch_code,
      quantity,
      planting_date,
      expected_harvest_date,
      status,
      actual_harvest_date: status === "Harvested" ? actual_harvest_date : null,
      yield: status === "Harvested" ? yield_amount : 0
    };

    if (id) {
      const res = await api.put(`/batches/${id}`, payload);
      showToast(res.message || "Batch updated successfully");
    } else {
      const res = await api.post("/batches", payload);
      showToast(res.message || "Crop batch created successfully");
    }
    batchModalInstance.hide();
    loadBatches();
  } catch (err) {
    showToast(err.message || "Error saving batch", "error");
  } finally {
    btn.disabled = false;
  }
}

function openStatusModal(batch) {
  document.getElementById("statusBatchId").value = batch.batch_id;
  document.getElementById("statusBatchCode").textContent = batch.batch_code;
  document.getElementById("statusBatchCrop").textContent = `${batch.crop_name} (${batch.field_name})`;
  document.getElementById("newStatusSelect").value = batch.status;

  // Render visual lifecycle in modal
  document.getElementById("statusLifecyclePreview").innerHTML = generateLifecycleHtml(batch.status);

  onStatusSelectChange();
  statusModalInstance.show();
}

function onStatusSelectChange() {
  const newStatus = document.getElementById("newStatusSelect").value;
  // Update live preview in modal
  document.getElementById("statusLifecyclePreview").innerHTML = generateLifecycleHtml(newStatus);

  const isHarvested = newStatus === "Harvested";
  document.getElementById("harvestFieldsBox").style.display = isHarvested ? "block" : "none";
  if (isHarvested && !document.getElementById("statusHarvestDateInput").value) {
    document.getElementById("statusHarvestDateInput").valueAsDate = new Date();
  }
}

async function saveBatchStatus(e) {
  e.preventDefault();
  const batchId = document.getElementById("statusBatchId").value;
  const status = document.getElementById("newStatusSelect").value;
  const yieldVal = document.getElementById("statusYieldInput").value;
  const actualDate = document.getElementById("statusHarvestDateInput").value;

  const btn = document.getElementById("saveStatusBtn");
  btn.disabled = true;

  try {
    const payload = {
      status,
      yield: status === "Harvested" ? yieldVal : null,
      actual_harvest_date: status === "Harvested" ? actualDate : null
    };

    const res = await api.patch(`/batches/${batchId}/status`, payload);
    showToast(res.message || "Batch lifecycle updated!");
    statusModalInstance.hide();
    loadBatches();
  } catch (err) {
    showToast(err.message || "Failed to update lifecycle status", "error");
  } finally {
    btn.disabled = false;
  }
}

async function deleteBatch(batchId, code) {
  if (!confirm(`Are you sure you want to delete batch "${code}" and all its activities?`)) return;

  try {
    const res = await api.delete(`/batches/${batchId}`);
    showToast(res.message || "Batch deleted successfully");
    loadBatches();
  } catch (err) {
    showToast(err.message || "Cannot delete batch", "error");
  }
}

async function viewBatchDetails(batchId) {
  const body = document.getElementById("batchDetailsBody");
  body.innerHTML = '<p class="text-center text-muted py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading batch details...</p>';
  batchDetailsModalInstance.show();

  try {
    const res = await api.get(`/batches/${batchId}`);
    if (!res.success || !res.data) return;

    const b = res.data;
    const lifecycleHtml = generateLifecycleHtml(b.status);

    const activitiesHtml = b.activities && b.activities.length > 0 ? b.activities.map(a => `
      <div class="d-flex justify-content-between align-items-center p-2 border-bottom">
        <div>
          <span class="fw-bold text-dark">${a.activity_type}</span> &bull; <span class="text-muted small">${a.activity_date}</span>
          <div class="small text-muted">${a.description}</div>
        </div>
        <span class="badge bg-success-subtle text-success border border-success-subtle fw-bold">
          ${a.quantity_used} ${a.unit}
        </span>
      </div>
    `).join("") : '<p class="text-muted text-center py-3">No cultivation activities logged yet.</p>';

    body.innerHTML = `
      <div class="mb-4">
        <h6 class="fw-bold text-success mb-2"><i class="fas fa-stream me-2"></i>Live Crop Lifecycle Progress</h6>
        ${lifecycleHtml}
      </div>

      <div class="row g-3 mb-4">
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Batch Code</div>
            <div class="fs-5 fw-bold text-success">${b.batch_code}</div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Crop Variety</div>
            <div class="fs-5 fw-bold text-dark">${b.crop_name} (${b.crop_type})</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Farmer Cultivator</div>
            <div class="fs-6 fw-bold text-dark">${b.farmer_name}</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Field Plot</div>
            <div class="fs-6 fw-bold text-dark">${b.field_name} (${b.field_area} ac)</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Planted Seeds</div>
            <div class="fs-6 fw-bold text-primary">${b.quantity} Kg</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Planting Date</div>
            <div class="fs-6 text-dark">${b.planting_date}</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Expected Harvest</div>
            <div class="fs-6 text-dark">${b.expected_harvest_date}</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Harvested Yield</div>
            <div class="fs-6 fw-bold text-success">${b.yield ? b.yield + ' Quintals' : 'Not Harvested Yet'}</div>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-between align-items-center mb-2">
        <h6 class="fw-bold text-success m-0"><i class="fas fa-clipboard-list me-2"></i>Cultivation Activities Logged (${b.activities_count})</h6>
        <a href="activities.html?batch_id=${b.batch_id}" class="btn btn-sm btn-agri-outline">
          <i class="fas fa-plus me-1"></i>Add Activity
        </a>
      </div>
      <div class="border rounded p-2">
        ${activitiesHtml}
      </div>
    `;
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
  }
}

async function exportBatchesCsv() {
  const crop_id = document.getElementById("filterCropSelect")?.value || "";
  const status = document.getElementById("filterStatusSelect")?.value || "";
  const farmer_id = document.getElementById("filterFarmerSelect")?.value || "";

  try {
    const params = {};
    if (crop_id) params.crop_id = crop_id;
    if (status) params.status = status;
    if (farmer_id) params.farmer_id = farmer_id;

    const blob = await api.get("/analytics/export-batches", params);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `crop_batches_export_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast("Crop batches CSV downloaded successfully!");
  } catch (err) {
    showToast("Export failed: " + err.message, "error");
  }
}
