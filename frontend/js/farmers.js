/**
 * AgriTech Farmer Management Script
 */

let currentPage = 1;
const pageSize = 10;
let searchDebounce = null;
let farmerModalInstance = null;
let detailsModalInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  farmerModalInstance = new bootstrap.Modal(document.getElementById("farmerModal"));
  detailsModalInstance = new bootstrap.Modal(document.getElementById("farmerDetailsModal"));
  if (!auth.isAdmin()) {
    document.querySelector(".page-title").textContent = "My Farm Profile";
    document.querySelector(".page-subtitle").textContent = "Your registered profile and assigned farm information";
    document.getElementById("farmerSearchInput").placeholder = "Search your profile...";
  }
  loadFarmers(1);
});

function handleFarmerSearch() {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    loadFarmers(1);
  }, 350);
}

async function loadFarmers(page = 1) {
  currentPage = page;
  const search = document.getElementById("farmerSearchInput")?.value || "";
  const tbody = document.getElementById("farmersTableBody");
  tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Loading farmers...</td></tr>';

  try {
    const res = await api.get("/farmers", { page, limit: pageSize, search });
    if (!res.success || !res.data) return;

    const { farmers, total, total_pages } = res.data;

    document.getElementById("paginationInfo").textContent = `Showing ${farmers.length} of ${total} farmers (Page ${page} of ${total_pages || 1})`;
    renderPagination(page, total_pages);

    if (farmers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No farmers found matching your criteria.</td></tr>';
      return;
    }

    const isAdmin = auth.isAdmin();

    tbody.innerHTML = farmers.map(f => `
      <tr>
        <td class="fw-bold text-muted">#${f.farmer_id}</td>
        <td>
          <div class="fw-bold text-dark">${f.name}</div>
          <div class="small text-muted" style="font-size: 0.78rem;">Reg: ${f.created_at || "Recent"}</div>
        </td>
        <td><i class="fas fa-phone-alt text-muted me-1 small"></i>${f.phone}</td>
        <td><span class="badge bg-light text-dark border">${f.village}</span></td>
        <td class="small text-muted" style="max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${f.address}">
          ${f.address}
        </td>
        <td>
          <span class="badge bg-success-subtle text-success border border-success-subtle">
            <i class="fas fa-vector-square me-1"></i>${f.fields_count} field(s) (${f.total_area} ac)
          </span>
        </td>
        <td class="text-end">
          <div class="d-inline-flex gap-1">
            <button class="btn-action-icon" title="View Details" onclick="viewFarmerDetails(${f.farmer_id})">
              <i class="fas fa-eye text-primary"></i>
            </button>
            ${isAdmin ? `
              <button class="btn-action-icon" title="Edit Farmer" onclick="openEditFarmerModal(${JSON.stringify(f).replace(/"/g, '&quot;')})">
                <i class="fas fa-edit text-success"></i>
              </button>
              <button class="btn-action-icon btn-action-delete" title="Delete Farmer" onclick="deleteFarmer(${f.farmer_id}, '${f.name}')">
                <i class="fas fa-trash-alt text-danger"></i>
              </button>
            ` : `
              <button class="btn-action-icon" title="Edit My Profile" onclick="openEditFarmerModal(${JSON.stringify(f).replace(/"/g, '&quot;')})">
                <i class="fas fa-edit text-success"></i>
              </button>
            `}
          </div>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger">Failed to load farmers: ${err.message}</td></tr>`;
  }
}

function renderPagination(page, totalPages) {
  const container = document.getElementById("paginationBtns");
  if (!container || totalPages <= 1) {
    if (container) container.innerHTML = "";
    return;
  }

  let html = `
    <button class="btn btn-sm btn-outline-secondary ${page <= 1 ? 'disabled' : ''}" onclick="loadFarmers(${page - 1})">
      <i class="fas fa-chevron-left"></i>
    </button>
  `;

  for (let i = 1; i <= totalPages; i++) {
    html += `
      <button class="btn btn-sm ${i === page ? 'btn-success' : 'btn-outline-secondary'}" onclick="loadFarmers(${i})">${i}</button>
    `;
  }

  html += `
    <button class="btn btn-sm btn-outline-secondary ${page >= totalPages ? 'disabled' : ''}" onclick="loadFarmers(${page + 1})">
      <i class="fas fa-chevron-right"></i>
    </button>
  `;

  container.innerHTML = html;
}

function openAddFarmerModal() {
  document.getElementById("farmerForm").reset();
  document.getElementById("farmerId").value = "";
  document.getElementById("farmerModalTitle").innerHTML = '<i class="fas fa-user-plus me-2 text-success"></i>Add New Farmer';
  farmerModalInstance.show();
}

function openEditFarmerModal(farmer) {
  document.getElementById("farmerId").value = farmer.farmer_id;
  document.getElementById("farmerName").value = farmer.name;
  document.getElementById("farmerPhone").value = farmer.phone;
  document.getElementById("farmerVillage").value = farmer.village;
  document.getElementById("farmerAddress").value = farmer.address;
  document.getElementById("farmerLandSize").value = farmer.land_size_acres ?? "";
  document.getElementById("farmerSoilType").value = farmer.soil_type || "";
  document.getElementById("farmerPreferredCrop").value = farmer.preferred_crop || "";
  document.getElementById("farmerPhotoUrl").value = farmer.profile_photo_url || "";
  document.getElementById("farmerFarmNotes").value = farmer.farm_notes || "";
  document.getElementById("farmerModalTitle").innerHTML = '<i class="fas fa-user-edit me-2 text-success"></i>Edit Farmer Record';
  farmerModalInstance.show();
}

async function saveFarmer(e) {
  e.preventDefault();
  const id = document.getElementById("farmerId").value;
  const name = document.getElementById("farmerName").value.trim();
  const phone = document.getElementById("farmerPhone").value.trim();
  const village = document.getElementById("farmerVillage").value.trim();
  const address = document.getElementById("farmerAddress").value.trim();
  const land_size_acres = document.getElementById("farmerLandSize").value;
  const soil_type = document.getElementById("farmerSoilType").value.trim();
  const preferred_crop = document.getElementById("farmerPreferredCrop").value.trim();
  const profile_photo_url = document.getElementById("farmerPhotoUrl").value.trim();
  const farm_notes = document.getElementById("farmerFarmNotes").value.trim();

  const btn = document.getElementById("saveFarmerBtn");
  btn.disabled = true;

  try {
    if (id) {
      // Update
      const res = await api.put(`/farmers/${id}`, {
        name,
        phone,
        village,
        address,
        land_size_acres: land_size_acres || null,
        soil_type: soil_type || null,
        preferred_crop: preferred_crop || null,
        profile_photo_url: profile_photo_url || null,
        farm_notes: farm_notes || null
      });
      showToast(res.message || "Farmer updated successfully");
    } else {
      // Create
      const res = await api.post("/farmers", {
        name,
        phone,
        village,
        address,
        land_size_acres: land_size_acres || null,
        soil_type: soil_type || null,
        preferred_crop: preferred_crop || null,
        profile_photo_url: profile_photo_url || null,
        farm_notes: farm_notes || null
      });
      showToast(res.message || "Farmer added successfully");
    }
    farmerModalInstance.hide();
    loadFarmers(currentPage);
  } catch (err) {
    showToast(err.message || "Error saving farmer", "error");
  } finally {
    btn.disabled = false;
  }
}

async function deleteFarmer(farmerId, name) {
  if (!confirm(`Are you sure you want to delete farmer "${name}"? This action cannot be undone.`)) {
    return;
  }

  try {
    const res = await api.delete(`/farmers/${farmerId}`);
    showToast(res.message || "Farmer deleted successfully");
    loadFarmers(currentPage);
  } catch (err) {
    showToast(err.message || "Cannot delete farmer with active batches/holdings", "error");
  }
}

async function viewFarmerDetails(farmerId) {
  const body = document.getElementById("farmerDetailsBody");
  body.innerHTML = '<p class="text-center text-muted py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading profile...</p>';
  detailsModalInstance.show();

  try {
    const res = await api.get(`/farmers/${farmerId}`);
    if (!res.success || !res.data) return;

    const f = res.data;
    const fieldsList = f.fields && f.fields.length > 0 ? f.fields.map(fld => `
      <li class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <span class="fw-bold">${fld.field_name}</span>
          <div class="small text-muted">${fld.location} &bull; Soil: ${fld.soil_type}</div>
        </div>
        <span class="badge bg-success rounded-pill">${fld.area} Acres</span>
      </li>
    `).join("") : '<li class="list-group-item text-muted text-center py-3">No fields assigned yet</li>';

    body.innerHTML = `
      <div class="row g-3 mb-3">
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted text-uppercase fw-bold">Full Name</div>
            <div class="fs-5 fw-bold text-dark">${f.name}</div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted text-uppercase fw-bold">Phone Contact</div>
            <div class="fs-5 fw-bold text-dark">${f.phone}</div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted text-uppercase fw-bold">Village / Zone</div>
            <div class="fs-6 fw-bold text-dark">${f.village}</div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="p-3 bg-light rounded">
            <div class="small text-muted text-uppercase fw-bold">Full Address</div>
            <div class="fs-6 text-dark">${f.address}</div>
          </div>
        </div>
      </div>

      <h6 class="fw-bold text-success mb-2"><i class="fas fa-map-marked-alt me-2"></i>Assigned Field Holdings (${f.fields?.length || 0})</h6>
      <ul class="list-group mb-3">
        ${fieldsList}
      </ul>
    `;
  } catch (err) {
    body.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
  }
}
