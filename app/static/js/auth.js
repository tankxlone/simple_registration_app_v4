/**
 * Authentication utilities and token management
 */
const Auth = {
  _initialized: false, // Prevent multiple initializations

  /**
   * Check if user is authenticated
   */
  isAuthenticated: function () {
    const token = this.getAccessToken();
    console.log("Checking authentication...");
    console.log("Access token found:", token ? "YES" : "NO");
    console.log("All cookies:", document.cookie);

    // Just return the token status, don't attempt refresh here
    return token !== null;
  },

  /**
   * Get access token from cookies
   */
  getAccessToken: function () {
    const token = this.getCookie("access_token_cookie");
    console.log("getAccessToken called");
    console.log("Looking for cookie: access_token_cookie");
    console.log("Cookie value:", token);
    return token;
  },

  /**
   * Get refresh token from cookies
   */
  getRefreshToken: function () {
    return this.getCookie("refresh_token_cookie");
  },

  /**
   * Get cookie value by name
   */
  getCookie: function (name) {
    // Debug: log all cookies
    console.log("getCookie called for:", name);
    console.log("document.cookie:", document.cookie);

    // Split cookies by semicolon and space
    const cookies = document.cookie.split("; ");
    console.log("Cookies array:", cookies);

    // Find the cookie with the specified name
    for (let cookie of cookies) {
      const [cookieName, cookieValue] = cookie.split("=");
      console.log("Checking cookie:", cookieName, "=", cookieValue);
      if (cookieName === name) {
        console.log("Found cookie:", name, "=", cookieValue);
        return cookieValue;
      }
    }

    console.log("Cookie not found:", name);
    return null;
  },

  /**
   * Set cookie
   */
  setCookie: function (name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
  },

  /**
   * Delete cookie
   */
  deleteCookie: function (name) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
  },

  /**
   * Refresh access token
   */
  async refreshToken() {
    try {
      const response = await fetch("/auth/refresh", {
        method: "POST",
        credentials: "include",
      });

      if (response.ok) {
        return true;
      } else {
        // Refresh failed, redirect to login
        this.logout();
        return false;
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      this.logout();
      return false;
    }
  },

  /**
   * Attempt to refresh token automatically
   */
  async attemptRefresh() {
    console.log("Attempting to refresh token...");
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      console.log("No refresh token available, redirecting to login");
      this.logout();
      return;
    }

    const success = await this.refreshToken();
    if (success) {
      console.log("Token refreshed successfully, updating navigation...");
      // Don't call init() again to prevent infinite loop
      const user = await this.getCurrentUser();
      if (user) {
        this.updateNavigation(user);
      }
    }
  },

  /**
   * Logout user
   */
  async logout() {
    try {
      // Call logout endpoint
      await fetch("/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear cookies and redirect
      this.deleteCookie("access_token_cookie");
      this.deleteCookie("refresh_token_cookie");
      window.location.href = "/auth/login";
    }
  },

  /**
   * Get current user info
   */
  async getCurrentUser() {
    try {
      const response = await fetch("/auth/me", {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        return data.user;
      } else {
        return null;
      }
    } catch (error) {
      console.error("Failed to get user info:", error);
      return null;
    }
  },

  /**
   * Update navigation based on auth state
   */
  updateNavigation: function (user) {
    const authNav = document.getElementById("auth-nav");

    if (user) {
      // User is logged in
      authNav.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" 
                       data-bs-toggle="dropdown" aria-expanded="false" aria-label="User menu">
                        <i class="bi bi-person-circle"></i> ${user.name}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                        <li><a class="dropdown-item" href="/dashboard">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a></li>
                        <li><a class="dropdown-item" href="/profile">
                            <i class="bi bi-person"></i> Profile
                        </a></li>
                        ${
                          user.has_submitted_feedback
                            ? `
                        <li><a class="dropdown-item" href="/feedback/my-feedback">
                            <i class="bi bi-list-ul"></i> My Feedback
                        </a></li>
                        `
                            : `
                        <li><a class="dropdown-item" href="/feedback/welcome">
                            <i class="bi bi-chat-dots"></i> Complete Welcome Feedback
                        </a></li>
                        `
                        }
                        ${
                          user.role === "admin"
                            ? `
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="/admin/dashboard">
                            <i class="bi bi-shield-check"></i> Admin Dashboard
                        </a></li>
                        <li><a class="dropdown-item" href="/admin/users">
                            <i class="bi bi-people"></i> Manage Users
                        </a></li>
                        <li><a class="dropdown-item" href="/admin/feedback">
                            <i class="bi bi-chat-square-text"></i> Manage Feedback
                        </a></li>
                        `
                            : ""
                        }
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item" href="#" id="logout-btn">
                            <i class="bi bi-box-arrow-right"></i> Logout
                        </a></li>
                    </ul>
                </li>
            `;

      // Add logout event listener
      document.getElementById("logout-btn").addEventListener("click", (e) => {
        e.preventDefault();
        this.logout();
      });

      // Update homepage content for authenticated users
      this.updateHomepageContent(user);
    } else {
      // User is not logged in
      authNav.innerHTML = `
                <li class="nav-item">
                    <a class="nav-link" href="/auth/login" aria-label="Login">
                        <i class="bi bi-box-arrow-in-right"></i> Login
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/auth/register" aria-label="Register">
                        <i class="bi bi-person-plus"></i> Register
                    </a>
                </li>
            `;

      // Update homepage content for guests
      this.updateHomepageContent(null);
    }
  },

  /**
   * Update homepage content based on auth state
   * Note: Homepage content is handled server-side, this is just a placeholder
   */
  updateHomepageContent: function (user) {
    // Homepage content is already rendered server-side based on user state
    // No need to update DOM elements here
    console.log(
      "Homepage content update called for user:",
      user ? user.email : "guest"
    );
  },

  /**
   * Initialize authentication
   */
  async init() {
    if (this._initialized) {
      console.log("Auth already initialized, skipping...");
      return;
    }

    console.log("Auth.init() called");
    this._initialized = true;

    console.log("Is authenticated:", this.isAuthenticated());

    if (this.isAuthenticated()) {
      console.log("User is authenticated, getting user info...");
      const user = await this.getCurrentUser();
      console.log("User info received:", user);
      if (user) {
        this.updateNavigation(user);
      } else {
        console.log("Token is invalid, logging out...");
        // Token is invalid, clear and redirect
        this.logout();
      }
    } else {
      console.log("User not authenticated, showing guest navigation");
      this.updateNavigation(null);
    }
  },
};

// Export Auth to global scope
window.Auth = Auth;
console.log("Auth object exported to window:", window.Auth);

// Add logout button event listener when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Logout button event delegation
  document.addEventListener("click", function (e) {
    if (e.target && e.target.id === "logout-btn") {
      e.preventDefault();
      Auth.logout();
    }
  });
});
