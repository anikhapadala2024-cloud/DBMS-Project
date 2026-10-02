/**
 * AgriTech Authentication & Authorization Utility
 */

const auth = {
  checkAuth() {
    const token = api.getToken();
    const user = api.getUser();

    const isLoginPage = window.location.pathname.endsWith("login.html") || window.location.pathname.endsWith("index.html") || window.location.pathname === "/";

    if (!token || !user) {
      if (!isLoginPage && !window.location.pathname.endsWith("login.html")) {
        window.location.href = "login.html";
      }
      return null;
    }

    if (window.location.pathname.endsWith("login.html")) {
      window.location.href = "dashboard.html";
      return user;
    }

    this.applyRoleRestrictions(user);
    return user;
  },

  getCurrentUser() {
    return api.getUser();
  },

  isAdmin() {
    const user = this.getCurrentUser();
    return user && user.role === "admin";
  },

  isFarmer() {
    const user = this.getCurrentUser();
    return user && user.role === "farmer";
  },

  applyRoleRestrictions(user) {
    if (!user) return;

    // Elements with data-role="admin" are hidden if user is not admin
    if (user.role !== "admin") {
      document.querySelectorAll('[data-role="admin"]').forEach(el => {
        el.style.display = "none";
      });
    }

    // Elements with data-role="farmer" are hidden if user is not farmer
    if (user.role !== "farmer") {
      document.querySelectorAll('[data-role="farmer"]').forEach(el => {
        el.style.display = "none";
      });
    }
  },

  logout() {
    api.clearSession();
    window.location.href = "login.html";
  }
};
