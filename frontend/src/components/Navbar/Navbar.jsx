import "./Navbar.css";
import { useState, useEffect, useRef } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FaHeartbeat,
  FaUser,
  FaSignOutAlt,
  FaBars,
  FaTimes,
  FaCircle,
  FaMapMarkerAlt,
  FaChevronDown,
  FaInfoCircle,
  FaEnvelope,
  FaUtensils,
} from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";
import LanguageSelector from "../LanguageSelector/LanguageSelector";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, currentLanguage } = useTranslation();
  const [currentUser, setCurrentUser] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [userDropdown, setUserDropdown] = useState(false);
  const [moreDropdown, setMoreDropdown] = useState(false);
  const moreRef = useRef(null);
  const userRef = useRef(null);

  // Tamil and Malayalam script detection for optimized spacing and "More" menu
  const isIndicLongScript = currentLanguage === "ta" || currentLanguage === "ml";
  const isMoreActive = [
    "/food-analyzer",
    "/find-care",
    "/profile",
    "/about",
    "/contact",
  ].includes(location.pathname);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (moreRef.current && !moreRef.current.contains(e.target)) {
        setMoreDropdown(false);
      }
      if (userRef.current && !userRef.current.contains(e.target)) {
        setUserDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("user");
    if (token && savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (e) {
        setCurrentUser(null);
      }
    } else {
      setCurrentUser(null);
    }
    setMenuOpen(false);
    setUserDropdown(false);
    setMoreDropdown(false);
  }, [location]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    localStorage.removeItem("latest_prediction");
    setCurrentUser(null);
    toast.success(`✅ ${t("auth.loggedOutSuccess")}`);
    navigate("/login");
  };

  const getInitials = (name) => {
    if (!name) return "U";
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <nav className="navbar-container">
      <div className="navbar-content">
        {/* Brand Logo */}
        <NavLink to="/" className="brand-logo">
          <div className="logo-icon-wrapper">
            <FaHeartbeat className="logo-icon" />
          </div>
          <div className="brand-text">
            <span className="brand-title">
              DiaSense <span className="brand-ai">AI</span>
            </span>
            <span className="brand-subtitle">
              <FaCircle className="pulse-dot" /> {t("common.engineActive")}
            </span>
          </div>
        </NavLink>

        {/* Desktop & Mobile Navigation Links */}
        <ul className={`nav-links ${menuOpen ? "mobile-open" : ""}`}>
          <li>
            <NavLink
              to="/"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {t("nav.home")}
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {t("nav.dashboard")}
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/assessment"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {t("nav.assessment")}
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/diet-plan"
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {t("nav.dietPlan")}
            </NavLink>
          </li>

          {/* For Tamil & Malayalam in desktop mode: Move secondary items into the clean "More" dropdown */}
          {isIndicLongScript && !menuOpen ? (
            <li className="more-dropdown-wrapper" ref={moreRef}>
              <button
                type="button"
                className={`more-nav-btn ${isMoreActive ? "active" : ""}`}
                onClick={() => setMoreDropdown(!moreDropdown)}
                aria-expanded={moreDropdown}
                aria-haspopup="true"
              >
                <span>{t("nav.more")}</span>
                <FaChevronDown
                  className={`more-chevron ${moreDropdown ? "rotate" : ""}`}
                />
              </button>

              {moreDropdown && (
                <div className="more-dropdown-menu">
                  <NavLink
                    to="/food-analyzer"
                    className={({ isActive }) =>
                      isActive ? "more-dropdown-item active" : "more-dropdown-item"
                    }
                    onClick={() => setMoreDropdown(false)}
                  >
                    <FaUtensils className="more-item-icon" />
                    <span>{t("nav.foodAnalyzer")}</span>
                  </NavLink>
                  <NavLink
                    to="/find-care"
                    className={({ isActive }) =>
                      isActive ? "more-dropdown-item active" : "more-dropdown-item"
                    }
                    onClick={() => setMoreDropdown(false)}
                  >
                    <FaMapMarkerAlt className="more-item-icon" />
                    <span>{t("nav.findCare")}</span>
                  </NavLink>
                  <NavLink
                    to="/profile"
                    className={({ isActive }) =>
                      isActive ? "more-dropdown-item active" : "more-dropdown-item"
                    }
                    onClick={() => setMoreDropdown(false)}
                  >
                    <FaUser className="more-item-icon" />
                    <span>{t("nav.profile")}</span>
                  </NavLink>
                  <NavLink
                    to="/about"
                    className={({ isActive }) =>
                      isActive ? "more-dropdown-item active" : "more-dropdown-item"
                    }
                    onClick={() => setMoreDropdown(false)}
                  >
                    <FaInfoCircle className="more-item-icon" />
                    <span>{t("nav.about")}</span>
                  </NavLink>
                  <NavLink
                    to="/contact"
                    className={({ isActive }) =>
                      isActive ? "more-dropdown-item active" : "more-dropdown-item"
                    }
                    onClick={() => setMoreDropdown(false)}
                  >
                    <FaEnvelope className="more-item-icon" />
                    <span>{t("nav.contact")}</span>
                  </NavLink>
                </div>
              )}
            </li>
          ) : (
            <>
              <li>
                <NavLink
                  to="/food-analyzer"
                  className={({ isActive }) =>
                    isActive ? "nav-link active" : "nav-link"
                  }
                >
                  {t("nav.foodAnalyzer")}
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/find-care"
                  className={({ isActive }) =>
                    isActive ? "nav-link active" : "nav-link"
                  }
                >
                  {t("nav.findCare")}
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/profile"
                  className={({ isActive }) =>
                    isActive ? "nav-link active" : "nav-link"
                  }
                >
                  {t("nav.profile")}
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/about"
                  className={({ isActive }) =>
                    isActive ? "nav-link active" : "nav-link"
                  }
                >
                  {t("nav.about")}
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/contact"
                  className={({ isActive }) =>
                    isActive ? "nav-link active" : "nav-link"
                  }
                >
                  {t("nav.contact")}
                </NavLink>
              </li>
            </>
          )}

          {/* Mobile Language Selector */}
          {menuOpen && (
            <li className="mobile-lang-item">
              <LanguageSelector />
            </li>
          )}

          {/* Mobile Auth Button */}
          {menuOpen && (
            <li className="mobile-auth-item">
              {currentUser ? (
                <button className="nav-btn logout" onClick={handleLogout}>
                  <FaSignOutAlt /> {t("nav.signOut")} (
                  {currentUser.full_name?.split(" ")[0] || "User"})
                </button>
              ) : (
                <NavLink to="/login" className="nav-btn primary">
                  {t("nav.login")}
                </NavLink>
              )}
            </li>
          )}
        </ul>

        {/* User Auth & Language Section */}
        <div className="auth-section">
          {/* Global Language Selector (Desktop & Tablet) */}
          <div className="desktop-lang-wrapper">
            <LanguageSelector />
          </div>

          {currentUser ? (
            <div className="user-profile-wrapper" ref={userRef}>
              <div
                className="user-avatar"
                onClick={() => setUserDropdown(!userDropdown)}
                title={t("nav.profileSettings")}
              >
                {getInitials(currentUser.full_name)}
              </div>

              {userDropdown && (
                <div className="user-dropdown-menu">
                  <div className="dropdown-user-info">
                    <p className="user-name">
                      {currentUser.full_name || "User"}
                    </p>
                    <p className="user-email">{currentUser.email}</p>
                  </div>
                  <hr className="dropdown-divider" />
                  <NavLink
                    to="/profile"
                    className="dropdown-item"
                    onClick={() => setUserDropdown(false)}
                  >
                    <FaUser /> {t("nav.profileSettings")}
                  </NavLink>
                  <NavLink
                    to="/dashboard"
                    className="dropdown-item"
                    onClick={() => setUserDropdown(false)}
                  >
                    <FaHeartbeat /> {t("nav.healthDashboard")}
                  </NavLink>
                  <NavLink
                    to="/find-care"
                    className="dropdown-item"
                    onClick={() => setUserDropdown(false)}
                  >
                    <FaMapMarkerAlt /> {t("nav.findCareNearYou")}
                  </NavLink>
                  <button
                    className="dropdown-item logout"
                    onClick={handleLogout}
                  >
                    <FaSignOutAlt /> {t("nav.signOut")}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <NavLink to="/login">
              <button className="nav-btn primary">{t("nav.signIn")}</button>
            </NavLink>
          )}

          {/* Mobile Menu Toggle */}
          <button
            className="mobile-hamburger"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle navigation"
          >
            {menuOpen ? <FaTimes /> : <FaBars />}
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;