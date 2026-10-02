/**
 * AgriTech API Client
 * Centralized Fetch wrapper with JWT authentication, error interception, and standard response handling.
 */

const API_BASE_URL = window.location.origin.includes("http") ? "/api" : "http://127.0.0.1:5000/api";

const api = {
  getToken() {
    return localStorage.getItem("agritech_token");
  },

  setToken(token) {
    localStorage.setItem("agritech_token", token);
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem("agritech_user") || "null");
    } catch {
      return null;
    }
  },

  setUser(user) {
    localStorage.setItem("agritech_user", JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem("agritech_token");
    localStorage.removeItem("agritech_user");
  },

  async request(endpoint, options = {}) {
    const url = new URL(endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`, window.location.origin);
    
    // Append query params if provided
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          url.searchParams.append(key, value);
        }
      });
    }

    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const config = {
      method: options.method || "GET",
      headers,
      ...options
    };

    if (options.body && typeof options.body === "object") {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url.toString(), config);

      if (response.status === 401) {
        // Token expired or invalid
        this.clearSession();
        if (!window.location.pathname.endsWith("login.html")) {
          window.location.href = "login.html";
        }
        throw new Error("Session expired. Please log in again.");
      }

      // Check if response is file download (CSV / Blob)
      const contentType = response.headers.get("Content-Type");
      if (contentType && (contentType.includes("text/csv") || contentType.includes("application/octet-stream"))) {
        return await response.blob();
      }

      const json = await response.json();
      if (!response.ok || json.success === false) {
        throw new Error(json.message || "Request failed with status " + response.status);
      }

      return json;
    } catch (error) {
      console.error(`API Error [${config.method} ${endpoint}]:`, error);
      throw error;
    }
  },

  get(endpoint, params = {}) {
    return this.request(endpoint, { method: "GET", params });
  },

  post(endpoint, body = {}) {
    return this.request(endpoint, { method: "POST", body });
  },

  put(endpoint, body = {}) {
    return this.request(endpoint, { method: "PUT", body });
  },

  patch(endpoint, body = {}) {
    return this.request(endpoint, { method: "PATCH", body });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" });
  }
};
