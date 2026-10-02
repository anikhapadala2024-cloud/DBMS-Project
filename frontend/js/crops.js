/**
 * AgriTech Crop Catalog Management Script
 */

let cropModalInstance = null;
let searchDebounce = null;

document.addEventListener("DOMContentLoaded", () => {
  cropModalInstance = new bootstrap.Modal(document.getElementById("cropModal"));
  loadCrops();
});

function handleCropSearch() {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    loadCrops();
  }, 350);
}

async function loadCrops() {
  const search = document.getElementById("cropSearchInput")?.value || "";
  const tbody = document.getElementById("cropsTableBody");
  tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Loading crops...</td></tr>';

  try {
    const params = {};
    if (search) params.search = search;

    const res = await api.get("/crops", params);
    if (!res.success || !res.data) return;

    const crops = res.data;
    if (crops.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No crop varieties found matching your criteria.</td></tr>';
      return;
    }

    const isAdmin = auth.isAdmin();

    tbody.innerHTML = crops.map(c => `
      <tr>
        <td class="fw-bold text-muted">#${c.crop_id}</td>
        <td>
          <div class="fw-bold text-success">${c.crop_name}</div>
        </td>
        <td>
          <span class="badge bg-light text-dark border">
            ${c.crop_type}
          </span>
        </td>
        <td>
          <span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle">
            <i class="fas fa-sun me-1"></i>${c.season}
          </span>
        </td>
        <td>
          <span class="fw-bold text-dark">${c.expected_yield} Q / Acre</span>
        </td>
        <td>
          <span class="badge bg-primary-subtle text-primary border border-primary-subtle">
            ${c.batches_count} batch(es)
          </span>
        </td>
        <td class="text-end">
          <div class="d-inline-flex gap-1">
            ${isAdmin ? `
              <button class="btn-action-icon" title="Edit Crop" onclick="openEditCropModal(${JSON.stringify(c).replace(/"/g, '&quot;')})">
                <i class="fas fa-edit text-success"></i>
              </button>
              <button class="btn-action-icon btn-action-delete" title="Delete Crop" onclick="deleteCrop(${c.crop_id}, '${c.crop_name}')">
                <i class="fas fa-trash-alt text-danger"></i>
              </button>
            ` : '<span class="text-muted small">View only</span>'}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger">Failed to load crops: ${err.message}</td></tr>`;
  }
}

function openAddCropModal() {
  document.getElementById("cropForm").reset();
  document.getElementById("cropId").value = "";
  document.getElementById("cropModalTitle").innerHTML = '<i class="fas fa-plus-circle me-2 text-success"></i>Add Crop Variety';
  cropModalInstance.show();
}

function openEditCropModal(crop) {
  document.getElementById("cropId").value = crop.crop_id;
  document.getElementById("cropName").value = crop.crop_name;
  document.getElementById("cropType").value = crop.crop_type;
  document.getElementById("cropSeason").value = crop.season;
  document.getElementById("cropYield").value = crop.expected_yield;
  document.getElementById("cropModalTitle").innerHTML = '<i class="fas fa-edit me-2 text-success"></i>Edit Crop Variety';
  cropModalInstance.show();
}

async function saveCrop(e) {
  e.preventDefault();
  const id = document.getElementById("cropId").value;
  const crop_name = document.getElementById("cropName").value.trim();
  const crop_type = document.getElementById("cropType").value;
  const season = document.getElementById("cropSeason").value;
  const expected_yield = document.getElementById("cropYield").value;

  const btn = document.getElementById("saveCropBtn");
  btn.disabled = true;

  try {
    if (id) {
      const res = await api.put(`/crops/${id}`, { crop_name, crop_type, season, expected_yield });
      showToast(res.message || "Crop variety updated successfully");
    } else {
      const res = await api.post("/crops", { crop_name, crop_type, season, expected_yield });
      showToast(res.message || "Crop variety added successfully");
    }
    cropModalInstance.hide();
    loadCrops();
  } catch (err) {
    showToast(err.message || "Error saving crop", "error");
  } finally {
    btn.disabled = false;
  }
}

async function deleteCrop(cropId, name) {
  if (!confirm(`Are you sure you want to delete crop variety "${name}"?`)) return;

  try {
    const res = await api.delete(`/crops/${cropId}`);
    showToast(res.message || "Crop deleted successfully");
    loadCrops();
  } catch (err) {
    showToast(err.message || "Cannot delete crop with active batches", "error");
  }
}
