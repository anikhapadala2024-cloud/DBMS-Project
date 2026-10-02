/**
 * AgriTech User Management Script (Admin Only)
 */

let userModalInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  if (!auth.isAdmin()) {
    showToast("Access forbidden: Administrator privileges required.", "error");
    window.location.href = "dashboard.html";
    return;
  }

  userModalInstance = new bootstrap.Modal(document.getElementById("userModal"));
  loadUsers();
});

async function loadUsers() {
  const tbody = document.getElementById("usersTableBody");
  tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Loading users...</td></tr>';

  try {
    const res = await api.get("/users");
    if (!res.success || !res.data) return;

    const users = res.data;
    const currentUserId = auth.getCurrentUser()?.id;

    tbody.innerHTML = users.map(u => {
      const isSelf = u.id === currentUserId;
      const roleBadge = u.role === "admin" 
        ? '<span class="user-role-badge role-admin">ADMIN</span>' 
        : '<span class="user-role-badge role-farmer">FARMER</span>';

      return `
        <tr>
          <td class="fw-bold text-muted">#${u.id}</td>
          <td>
            <div class="fw-bold text-dark">${u.name} ${isSelf ? '<span class="badge bg-secondary ms-1">You</span>' : ''}</div>
          </td>
          <td>${u.email}</td>
          <td>${roleBadge}</td>
          <td>
            ${u.farmer_id ? `<span class="badge bg-light text-success border"><i class="fas fa-tractor me-1"></i>Farmer #${u.farmer_id}</span>` : '<span class="text-muted small">System Admin</span>'}
          </td>
          <td class="small text-muted">${u.created_at || "--"}</td>
          <td class="text-end">
            <div class="d-inline-flex gap-1">
              <button class="btn-action-icon" title="Edit User" onclick="openEditUserModal(${JSON.stringify(u).replace(/"/g, '&quot;')})">
                <i class="fas fa-edit text-success"></i>
              </button>
              ${!isSelf ? `
                <button class="btn-action-icon btn-action-delete" title="Delete User" onclick="deleteUser(${u.id}, '${u.name}')">
                  <i class="fas fa-trash-alt text-danger"></i>
                </button>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger">Failed to load users: ${err.message}</td></tr>`;
  }
}

function openAddUserModal() {
  document.getElementById("userForm").reset();
  document.getElementById("userId").value = "";
  document.getElementById("userEmail").disabled = false;
  document.getElementById("userPassword").required = true;
  document.getElementById("userPasswordHelp").textContent = "Required for new users (minimum 6 characters).";
  document.getElementById("userModalTitle").innerHTML = '<i class="fas fa-user-plus me-2 text-success"></i>Create System User';
  userModalInstance.show();
}

function openEditUserModal(user) {
  document.getElementById("userId").value = user.id;
  document.getElementById("userName").value = user.name;
  document.getElementById("userEmail").value = user.email;
  document.getElementById("userEmail").disabled = true; // Email unique key
  document.getElementById("userRole").value = user.role;
  document.getElementById("userPassword").value = "";
  document.getElementById("userPassword").required = false;
  document.getElementById("userPasswordHelp").textContent = "Leave empty to keep existing password.";
  document.getElementById("userModalTitle").innerHTML = '<i class="fas fa-user-edit me-2 text-success"></i>Edit System User';
  userModalInstance.show();
}

async function saveUser(e) {
  e.preventDefault();
  const id = document.getElementById("userId").value;
  const name = document.getElementById("userName").value.trim();
  const email = document.getElementById("userEmail").value.trim();
  const role = document.getElementById("userRole").value;
  const password = document.getElementById("userPassword").value;

  const btn = document.getElementById("saveUserBtn");
  btn.disabled = true;

  try {
    if (id) {
      const payload = { name, role };
      if (password && password.length >= 6) payload.password = password;
      const res = await api.put(`/users/${id}`, payload);
      showToast(res.message || "User updated successfully");
    } else {
      if (!password || password.length < 6) {
        showToast("Password must be at least 6 characters.", "error");
        btn.disabled = false;
        return;
      }
      const res = await api.post("/users", { name, email, role, password });
      showToast(res.message || "User created successfully");
    }
    userModalInstance.hide();
    loadUsers();
  } catch (err) {
    showToast(err.message || "Error saving user", "error");
  } finally {
    btn.disabled = false;
  }
}

async function deleteUser(userId, name) {
  if (!confirm(`Are you sure you want to delete user account "${name}"?`)) return;

  try {
    const res = await api.delete(`/users/${userId}`);
    showToast(res.message || "User deleted successfully");
    loadUsers();
  } catch (err) {
    showToast(err.message || "Failed to delete user", "error");
  }
}
