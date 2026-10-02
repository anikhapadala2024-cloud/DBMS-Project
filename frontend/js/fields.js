/**
 * AgriTech Field Management Script
 */

let fieldModalInstance = null;
let fieldDetailsModalInstance = null;
let searchDebounce = null;
let farmersList = [];

document.addEventListener("DOMContentLoaded", async () => {
  fieldModalInstance = new bootstrap.Modal(document.getElementById("fieldModal"));
  fieldDetailsModalInstance = new bootstrap.Modal(document.getElementById("fieldDetailsModal"));
  await loadFarmersDropdown();
  await loadFields();
});

function handleFieldSearch() {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    loadFields();
  }, 350);
}

async function loadFarmersDropdown() {
  try {
    const res = await api.get("/farmers", { limit: 100 });
    if (res.success && res.data) {
      farmersList = res.data.farmers || [];
      const filterSelect = document.getElementById("farmerFilterSelect");
      const modalSelect = document.getElementById("fieldFarmerId");

      let filterOptions = '<option value="">All Farmers</option>';
      let modalOptions = '<option value="">Select Farmer...</option>';

      farmersList.forEach(f => {
        const opt = `<option value="${f.farmer_id}">${f.name} (${f.village})</option>`;
        filterOptions += opt;
        modalOptions += opt;
      });

      if (filterSelect) filterSelect.innerHTML = filterOptions;
      if (modalSelect) modalSelect.innerHTML = modalOptions;
    }
  } catch (err) {
    console.error("Error loading farmers for dropdown:", err);
  }
}

async function loadFields() {
  const search = document.getElementById("fieldSearchInput")?.value || "";
  const farmer_id = document.getElementById("farmerFilterSelect")?.value || "";
  const tbody = document.getElementById("fieldsTableBody");
  tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Loading fields...</td></tr>';

  try {
    const params = {};
    if (search) params.search = search;
    if (farmer_id) params.farmer_id = farmer_id;

    const res = await api.get("/fields", params);
    if (!res.success || !res.data) return;

    const fields = res.data;
    if (fields.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No field plots found matching your criteria.</td></tr>';
      return;
    }

    const isAdmin = auth.isAdmin();

    tbody.innerHTML = fields.map(f => `
      <tr>
        <td class="fw-bold text-muted">#${f.field_id}</td>
        <td>
          <div class="fw-bold text-dark">${f.field_name}</div>
        </td>
        <td>
          <span class="badge bg-light text-dark border">
            <i class="fas fa-user-circle me-1 text-success"></i>${f.farmer_name}
          </span>
        </td>
        <td><i class="fas fa-map-marker-alt text-danger me-1 small"></i>${f.location}</td>
        <td><span class="fw-bold text-success">${f.area} Acres</span></td>
        <td>
          <span class="badge bg-secondary-subtle text-secondary border">
            ${f.soil_type}
          </span>
        </td>
        <td>
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle">
            ${f.batches_count} batch(es)
          </span>
        </td>
        <td class="text-end">
          <div class="d-inline-flex gap-1">
            <button class="btn-action-icon" title="View Field Details" onclick="viewFieldDetails(${f.field_id})">
              <i class="fas fa-eye text-primary"></i>
            </button>
            ${isAdmin ? `
              <button class="btn-action-icon" title="Edit Field" onclick="openEditFieldModal(${JSON.stringify(f).replace(/"/g, '&quot;')})">
                <i class="fas fa-edit text-success"></i>
              </button>
              <button class="btn-action-icon btn-action-delete" title="Delete Field" onclick="deleteField(${f.field_id}, '${f.field_name}')">
                <i class="fas fa-trash-alt text-danger"></i>
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-danger">Failed to load fields: ${err.message}</td></tr>`;
  }
}

function openAddFieldModal() {
  document.getElementById("fieldForm").reset();
  document.getElementById("fieldId").value = "";
  document.getElementById("fieldModalTitle").innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Add New Field Plot';
  fieldModalInstance.show();
}

function openEditFieldModal(field) {
  document.getElementById("fieldId").value = field.field_id;
  document.getElementById("fieldFarmerId").value = field.farmer_id;
  document.getElementById("fieldName").value = field.field_name;
  document.getElementById("fieldLocation").value = field.location;
  document.getElementById("fieldArea").value = field.area;
  document.getElementById("fieldSoilType").value = field.soil_type;
  document.getElementById("fieldModalTitle").innerHTML = '<i class="fas fa-edit me-2 text-success"></i>Edit Field Plot';
  fieldModalInstance.show();
}

async function saveField(e) {
  e.preventDefault();
  const id = document.getElementById("fieldId").value;
  const farmer_id = document.getElementById("fieldFarmerId").value;
  const field_name = document.getElementById("fieldName").value.trim();
  const location = document.getElementById("fieldLocation").value.trim();
  const area = document.getElementById("fieldArea").value;
  const soil_type = document.getElementById("fieldSoilType").value;

  const btn = document.getElementById("saveFieldBtn");
  btn.disabled = true;

  try {
    if (id) {
      const res = await api.put(`/fields/${id}`, { farmer_id, field_name, location, area, soil_type });
      showToast(res.message || "Field plot updated successfully");
    } else {
      const res = await api.post("/fields", { farmer_id, field_name, location, area, soil_type });
      showToast(res.message || "Field plot created successfully");
    }
    fieldModalInstance.hide();
    loadFields();
  } catch (err) {
    showToast(err.message || "Error saving field", "error");
  } finally {
    btn.disabled = false;
  }
}

async function deleteField(fieldId, name) {
  if (!confirm(`Are you sure you want to delete field "${name}"?`)) return;

  try {
    const res = await api.delete(`/fields/${fieldId}`);
    showToast(res.message || "Field deleted successfully");
    loadFields();
  } catch (err) {
    showToast(err.message || "Cannot delete field with active batches", "error");
  }
}

async function viewFieldDetails(fieldId) {
  const body = document.getElementById("fieldDetailsBody");
  body.innerHTML = '<p class="text-center text-muted py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading details...</p>';
  fieldDetailsModalInstance.show();

  try {
    const res = await api.get(`/fields/${fieldId}`);
    if (!res.success || !res.data) return;

    const f = res.data;
    const batchesHtml = f.batches && f.batches.length > 0 ? f.batches.map(b => `
      <div class="d-flex justify-content-between align-items-center p-2 border-bottom">
        <div>
          <span class="fw-bold text-success">${b.batch_code}</span> &bull; ${b.crop_name}
          <div class="small text-muted">Planted: ${b.planting_date} | Expected: ${b.expected_harvest_date}</div>
        </div>
        <span class="badge-status status-${b.status.replace(/ /g, '-')}">${b.status}</span>
      </div>
    `).join("") : '<p class="text-muted text-center py-3">No batches recorded in this field yet.</p>';

    body.innerHTML = `
      <div class="row g-3 mb-4">
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Field Name</div>
            <div class="fs-5 fw-bold text-dark">${f.field_name}</div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Associated Farmer</div>
            <div class="fs-5 fw-bold text-success">${f.farmer_name}</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Total Area</div>
            <div class="fs-5 fw-bold text-primary">${f.area} Acres</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Soil Profile</div>
            <div class="fs-5 fw-bold text-dark">${f.soil_type}</div>
          </div>
        </div>
        <div class="col-sm-4">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted fw-bold text-uppercase">Geographic Zone</div>
            <div class="fs-6 fw-bold text-dark">${f.location}</div>
          </div>
        </div>
      </div>

      <h6 class="fw-bold text-success mb-2"><i class="fas fa-layer-group me-2"></i>Batches Associated With This Field</h6>
      <div class="border rounded p-2">
        ${batchesHtml}
      </div>
    `;
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
  }
}
