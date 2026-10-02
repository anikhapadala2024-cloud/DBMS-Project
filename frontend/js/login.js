/**
 * AgriTech Login Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // If already logged in, redirect directly to dashboard
  const token = api.getToken();
  if (token) {
    window.location.href = "dashboard.html";
  }
});

function toggleAuthMode() {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const toggle = document.getElementById("authModeToggle");
  const isRegistering = registerForm.classList.contains("d-none");

  loginForm.classList.toggle("d-none", isRegistering);
  registerForm.classList.toggle("d-none", !isRegistering);
  document.getElementById("loginAlert").classList.add("d-none");
  toggle.textContent = isRegistering ? "Already have an account? Sign in" : "Need an account? Create one";
}

function togglePasswordVisibility() {
  const pwdInput = document.getElementById("password");
  const icon = document.getElementById("togglePasswordIcon");
  if (pwdInput.type === "password") {
    pwdInput.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    pwdInput.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}

function fillCredentials(email, password) {
  document.getElementById("email").value = email;
  document.getElementById("password").value = password;
  hideAlert();
}

function showAlert(message) {
  const alertEl = document.getElementById("loginAlert");
  alertEl.textContent = message;
  alertEl.classList.remove("d-none");
}

function hideAlert() {
  const alertEl = document.getElementById("loginAlert");
  alertEl.classList.add("d-none");
}

async function handleLogin(e) {
  e.preventDefault();
  hideAlert();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const loginBtn = document.getElementById("loginBtn");

  if (!email || !password) {
    showAlert("Please enter both email and password.");
    return;
  }

  loginBtn.disabled = true;
  loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Authenticating...';

  try {
    const res = await api.post("/auth/login", { email, password });
    if (res.success && res.data && res.data.token) {
      api.setToken(res.data.token);
      api.setUser(res.data.user);
      window.location.href = "dashboard.html";
    } else {
      showAlert(res.message || "Invalid credentials.");
    }
  } catch (err) {
    showAlert(err.message || "Failed to connect to server.");
  } finally {
    loginBtn.disabled = false;
    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Sign In to Dashboard';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  hideAlert();

  const name = document.getElementById("registerName").value.trim();
  const email = document.getElementById("registerEmail").value.trim();
  const password = document.getElementById("registerPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;
  const role = document.getElementById("registerRole")?.value || "farmer";
  const registerBtn = document.getElementById("registerBtn");

  if (password !== confirmPassword) {
    showAlert("Passwords do not match.");
    return;
  }

  registerBtn.disabled = true;
  registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Creating account...';

  try {
    const res = await api.post("/auth/register", { name, email, password, role });
    if (res.success && res.data && res.data.token) {
      api.setToken(res.data.token);
      api.setUser(res.data.user);
      window.location.href = "dashboard.html";
    } else {
      showAlert(res.message || "Unable to create account.");
    }
  } catch (err) {
    showAlert(err.message || "Failed to connect to server.");
  } finally {
    registerBtn.disabled = false;
    const roleLabel = role === "admin" ? "Admin" : "Farmer";
    registerBtn.innerHTML = `<i class="fas fa-user-plus me-2"></i>Create ${roleLabel} Account`;
  }
}
