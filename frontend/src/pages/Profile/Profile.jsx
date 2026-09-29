import "./Profile.css";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FaUser,
  FaEnvelope,
  FaCalendarAlt,
  FaVenusMars,
  FaKey,
  FaLock,
  FaShieldAlt,
  FaHeartbeat,
  FaCheckCircle,
  FaTimesCircle,
  FaIdBadge,
  FaEye,
  FaEyeSlash,
  FaNotesMedical,
  FaUtensils,
  FaCamera,
  FaArrowRight,
  FaGlobe,
  FaChartLine,
} from "react-icons/fa";

import { authService, userService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";

function Profile() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Active tab: 'personal' | 'security' | 'health'
  const [activeTab, setActiveTab] = useState("personal");

  // Profile data
  const [userId, setUserId] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Male");
  const [memberSince, setMemberSince] = useState("");
  const [stats, setStats] = useState({
    totalAssessments: 0,
    latestPrediction: null,
    latestRiskScore: null,
    latestDate: null,
  });

  // Password update form
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPw, setShowCurrentPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);

  // States
  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [changingPw, setChangingPw] = useState(false);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    setLoading(true);
    try {
      const res = await authService.getProfile();
      if (res.data) {
        const data = res.data;
        setUserId(data.id || "");
        setFullName(data.full_name || "");
        setEmail(data.email || "");
        setAge(data.age ? String(data.age) : "");
        setGender(data.gender || "Male");
        if (data.created_at) {
          const d = new Date(data.created_at);
          setMemberSince(
            d.toLocaleDateString("en-US", { month: "short", year: "numeric" })
          );
        }
        setStats({
          totalAssessments: data.total_assessments || 0,
          latestPrediction: data.latest_prediction || null,
          latestRiskScore:
            data.latest_risk_score !== null ? data.latest_risk_score : null,
          latestDate: data.latest_assessment_date || null,
        });
      }
    } catch (err) {
      toast.error(err.message || "Failed to load user profile.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!fullName.trim()) {
      toast.error("Full name cannot be blank.");
      return;
    }

    setSavingProfile(true);
    try {
      await userService.updateProfile({
        full_name: fullName.trim(),
        age: age ? parseInt(age, 10) : undefined,
        gender: gender,
      });

      // Update local storage user
      try {
        const savedUser = JSON.parse(localStorage.getItem("user") || "{}");
        savedUser.full_name = fullName.trim();
        savedUser.age = age ? parseInt(age, 10) : undefined;
        savedUser.gender = gender;
        localStorage.setItem("user", JSON.stringify(savedUser));
      } catch (err) {}

      toast.success(`✅ ${t("profile.profileUpdated") || "Profile updated successfully!"}`);
    } catch (err) {
      toast.error(err.message || "Failed to update profile.");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error("Please fill in all password fields.");
      return;
    }

    if (!isNewPwValid) {
      toast.error(t("profile.passCriteriaTitle") || "Password does not meet requirements.");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error(t("auth.validationPasswordMatch") || "Passwords do not match.");
      return;
    }

    setChangingPw(true);
    try {
      await userService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      toast.success(`✅ ${t("profile.passwordUpdated") || "Password updated successfully!"}`);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      toast.error(
        err.message || "Failed to update password. Verify current password."
      );
    } finally {
      setChangingPw(false);
    }
  };

  // Password criteria check
  const criteria = {
    length: newPassword.length >= 8,
    uppercase: /[A-Z]/.test(newPassword),
    lowercase: /[a-z]/.test(newPassword),
    number: /[0-9]/.test(newPassword),
    special: /[^A-Za-z0-9]/.test(newPassword),
  };
  const isNewPwValid = Object.values(criteria).every(Boolean);

  const getInitials = (name) => {
    if (!name) return "DS";
    const parts = name.trim().split(" ");
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.substring(0, 2).toUpperCase();
  };

  if (loading) {
    return (
      <div className="profile-loading-screen">
        <div className="profile-spinner" />
        <p>{t("common.loading")}</p>
      </div>
    );
  }

  return (
    <div className="profile-page-container">
      {/* Background Ambience Lighting */}
      <div className="profile-ambient-glow-1" />
      <div className="profile-ambient-glow-2" />

      <div className="profile-content-wrapper">
        {/* Top Floating Navigation Header */}
        <div className="profile-top-bar">
          <button className="profile-back-btn" onClick={() => navigate(-1)}>
            ← {t("common.goBack")}
          </button>
          <div className="profile-breadcrumb">
            <span>{t("nav.home")}</span> / <span className="current">{t("nav.profile")}</span>
          </div>
        </div>

        {/* 1. Compact Unified Profile Header Card */}
        <div className="profile-compact-header-card">
          <div className="profile-header-identity">
            <div className="profile-avatar-wrapper">
              <span className="avatar-letters">{getInitials(fullName)}</span>
              <span className="avatar-status-dot" title="Online" />
            </div>

            <div className="profile-header-text">
              <div className="profile-name-badge-row">
                <h2>{fullName || "DiaSense Patient"}</h2>
                <span className="verified-patient-badge">
                  <FaCheckCircle className="badge-icon" /> {t("profile.verifiedPatient")}
                </span>
              </div>
              <div className="profile-meta-subrow">
                <span className="meta-email">{email}</span>
                <span className="meta-dot">•</span>
                <span className="meta-chip">
                  <FaCalendarAlt className="meta-icon" /> {t("profile.memberSince")}: {memberSince || t("profile.recent") || "Recent"}
                </span>
                <span className="meta-dot">•</span>
                <span className="meta-chip">
                  <FaVenusMars className="meta-icon" /> {gender === "Female" ? t("auth.female") : gender === "Other" ? t("auth.other") : t("auth.male")} {age ? `(${age} ${t("profile.years")})` : ""}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Modern 2-Column Responsive Dashboard Layout */}
        <div className="profile-main-grid">
          {/* LEFT COLUMN: Clean Active Tab Form Section */}
          <div className="profile-left-col">
            {/* Compact Tabs Bar */}
            <div className="profile-nav-tabs">
              <button
                type="button"
                className={`tab-btn-pill ${activeTab === "personal" ? "active" : ""}`}
                onClick={() => setActiveTab("personal")}
              >
                <FaUser className="tab-icon" />
                <span>{t("profile.tabPersonal")}</span>
              </button>
              <button
                type="button"
                className={`tab-btn-pill ${activeTab === "security" ? "active" : ""}`}
                onClick={() => setActiveTab("security")}
              >
                <FaKey className="tab-icon" />
                <span>{t("profile.tabSecurity")}</span>
              </button>
              <button
                type="button"
                className={`tab-btn-pill ${activeTab === "health" ? "active" : ""}`}
                onClick={() => setActiveTab("health")}
              >
                <FaHeartbeat className="tab-icon" />
                <span>{t("profile.tabHealth")}</span>
              </button>
            </div>

            {/* TAB 1: Personal Information Form */}
            {activeTab === "personal" && (
              <div className="profile-pane-card">
                <div className="pane-title-box">
                  <h3>{t("profile.editPersonalTitle") || t("profile.headerTitle")}</h3>
                  <p>{t("profile.editPersonalDesc") || t("profile.headerDesc")}</p>
                </div>

                <form onSubmit={handleUpdateProfile} className="compact-profile-form">
                  <div className="form-field-group">
                    <label>
                      <FaUser className="field-lbl-icon" /> {t("auth.fullNameLabel")}
                    </label>
                    <input
                      type="text"
                      placeholder={t("auth.fullNamePlaceholder")}
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-field-group">
                    <label>
                      <FaEnvelope className="field-lbl-icon" /> {t("auth.emailLabel")}
                    </label>
                    <input
                      type="email"
                      value={email}
                      disabled
                      title={t("profile.emailHint")}
                      className="input-field-disabled"
                    />
                    <span className="field-sub-hint">{t("profile.emailHint")}</span>
                  </div>

                  <div className="form-two-cols">
                    <div className="form-field-group">
                      <label>
                        <FaCalendarAlt className="field-lbl-icon" /> {t("auth.ageLabel")}
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="120"
                        placeholder="e.g. 35"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                      />
                    </div>

                    <div className="form-field-group">
                      <label>
                        <FaVenusMars className="field-lbl-icon" /> {t("auth.genderLabel")}
                      </label>
                      <select
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                      >
                        <option value="Male">{t("auth.male")}</option>
                        <option value="Female">{t("auth.female")}</option>
                        <option value="Other">{t("auth.other")}</option>
                      </select>
                    </div>
                  </div>

                  {/* Preferred Language Selector */}
                  <div className="form-field-group">
                    <label>
                      <FaGlobe className="field-lbl-icon" /> {t("profile.preferredLanguage")}
                    </label>
                    <div className="profile-lang-selector-box">
                      <LanguageSelector />
                    </div>
                  </div>

                  {/* Primary Save Action Button */}
                  <div className="form-save-action-box">
                    <button
                      type="submit"
                      className="btn-primary-save"
                      disabled={savingProfile}
                    >
                      {savingProfile ? (
                        <>
                          <span className="btn-spinner" />
                          <span>{t("profile.updatingBtn") || t("common.saving")}</span>
                        </>
                      ) : (
                        <>
                          <span>💾</span>
                          <span>{t("profile.updateBtn") || t("common.save")}</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 2: Security & Change Password */}
            {activeTab === "security" && (
              <div className="profile-pane-card">
                <div className="pane-title-box">
                  <h3>{t("profile.changePasswordTitle") || t("profile.changePasswordBtn")}</h3>
                  <p>{t("profile.changePasswordDesc")}</p>
                </div>

                <form onSubmit={handleChangePassword} className="compact-profile-form">
                  <div className="form-field-group">
                    <label>
                      <FaLock className="field-lbl-icon" /> {t("profile.currentPassword")}
                    </label>
                    <div className="input-pw-wrapper">
                      <input
                        type={showCurrentPw ? "text" : "password"}
                        placeholder={t("profile.currentPassword")}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        required
                      />
                      <button
                        type="button"
                        className="btn-pw-eye"
                        onClick={() => setShowCurrentPw(!showCurrentPw)}
                        aria-label="Toggle password visibility"
                      >
                        {showCurrentPw ? <FaEyeSlash /> : <FaEye />}
                      </button>
                    </div>
                  </div>

                  <div className="form-field-group">
                    <label>
                      <FaKey className="field-lbl-icon" /> {t("profile.newPassword")}
                    </label>
                    <div className="input-pw-wrapper">
                      <input
                        type={showNewPw ? "text" : "password"}
                        placeholder={t("profile.newPassword")}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                      />
                      <button
                        type="button"
                        className="btn-pw-eye"
                        onClick={() => setShowNewPw(!showNewPw)}
                        aria-label="Toggle password visibility"
                      >
                        {showNewPw ? <FaEyeSlash /> : <FaEye />}
                      </button>
                    </div>
                  </div>

                  {/* Compact Security Criteria Checklist */}
                  {newPassword.length > 0 && (
                    <div className="compact-pw-criteria">
                      <div className="criteria-head">
                        <FaShieldAlt className="crit-shield" />
                        <span>{t("profile.passCriteriaTitle")}</span>
                      </div>
                      <div className="criteria-grid">
                        <div className={`crit-pill ${criteria.length ? "pass" : "fail"}`}>
                          {criteria.length ? <FaCheckCircle className="crit-chk" /> : <FaTimesCircle className="crit-chk" />}
                          <span>{t("profile.critLength")}</span>
                        </div>
                        <div className={`crit-pill ${criteria.uppercase ? "pass" : "fail"}`}>
                          {criteria.uppercase ? <FaCheckCircle className="crit-chk" /> : <FaTimesCircle className="crit-chk" />}
                          <span>{t("profile.critUpper")}</span>
                        </div>
                        <div className={`crit-pill ${criteria.lowercase ? "pass" : "fail"}`}>
                          {criteria.lowercase ? <FaCheckCircle className="crit-chk" /> : <FaTimesCircle className="crit-chk" />}
                          <span>{t("profile.critLower")}</span>
                        </div>
                        <div className={`crit-pill ${criteria.number ? "pass" : "fail"}`}>
                          {criteria.number ? <FaCheckCircle className="crit-chk" /> : <FaTimesCircle className="crit-chk" />}
                          <span>{t("profile.critNumber")}</span>
                        </div>
                        <div className={`crit-pill ${criteria.special ? "pass" : "fail"}`}>
                          {criteria.special ? <FaCheckCircle className="crit-chk" /> : <FaTimesCircle className="crit-chk" />}
                          <span>{t("profile.critSpecial")}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="form-field-group">
                    <label>
                      <FaLock className="field-lbl-icon" /> {t("profile.confirmNewPassword")}
                    </label>
                    <input
                      type={showNewPw ? "text" : "password"}
                      placeholder={t("profile.confirmNewPassword")}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-save-action-box">
                    <button
                      type="submit"
                      className="btn-primary-save"
                      disabled={changingPw}
                    >
                      {changingPw ? (
                        <>
                          <span className="btn-spinner" />
                          <span>{t("profile.updatingBtn") || t("common.saving")}</span>
                        </>
                      ) : (
                        <>
                          <span>🔒</span>
                          <span>{t("profile.changePasswordBtn")}</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 3: Quick Health Shortcuts */}
            {activeTab === "health" && (
              <div className="profile-pane-card">
                <div className="pane-title-box">
                  <h3>{t("profile.quickHealthNav")}</h3>
                  <p>{t("profile.quickHealthDesc")}</p>
                </div>

                <div className="compact-shortcuts-grid">
                  <div
                    className="shortcut-tile"
                    onClick={() => navigate("/assessment")}
                    role="button"
                    tabIndex={0}
                  >
                    <div className="shortcut-icon-box cyan">
                      <FaNotesMedical />
                    </div>
                    <div className="shortcut-text-box">
                      <h4>{t("dashboard.startNewAssessment")}</h4>
                      <p>{t("nav.assessment")}</p>
                    </div>
                    <FaArrowRight className="tile-arrow" />
                  </div>

                  <div
                    className="shortcut-tile"
                    onClick={() => navigate("/diet-plan")}
                    role="button"
                    tabIndex={0}
                  >
                    <div className="shortcut-icon-box emerald">
                      <FaUtensils />
                    </div>
                    <div className="shortcut-text-box">
                      <h4>{t("nav.dietPlan")}</h4>
                      <p>{t("dietPlan.headerBadge")}</p>
                    </div>
                    <FaArrowRight className="tile-arrow" />
                  </div>

                  <div
                    className="shortcut-tile"
                    onClick={() => navigate("/food-analyzer")}
                    role="button"
                    tabIndex={0}
                  >
                    <div className="shortcut-icon-box purple">
                      <FaCamera />
                    </div>
                    <div className="shortcut-text-box">
                      <h4>{t("nav.foodAnalyzer")}</h4>
                      <p>{t("home.featuresSubtitle")}</p>
                    </div>
                    <FaArrowRight className="tile-arrow" />
                  </div>

                  <div
                    className="shortcut-tile"
                    onClick={() => navigate("/dashboard")}
                    role="button"
                    tabIndex={0}
                  >
                    <div className="shortcut-icon-box blue">
                      <FaHeartbeat />
                    </div>
                    <div className="shortcut-text-box">
                      <h4>{t("nav.healthDashboard")}</h4>
                      <p>{t("nav.dashboard")}</p>
                    </div>
                    <FaArrowRight className="tile-arrow" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* RIGHT COLUMN: Compact Health Summary & Quick Info Sidebar */}
          <div className="profile-right-col">
            <div className="health-summary-sidebar-card">
              <div className="summary-card-header">
                <FaHeartbeat className="header-heart-icon" />
                <h3>{t("result.patientSummary")}</h3>
              </div>

              {/* 3 Compact Metric Tiles */}
              <div className="compact-stats-stack">
                <div className="compact-stat-row">
                  <span className="stat-name">{t("profile.totalAssessments")}</span>
                  <span className="stat-number cyan">{stats.totalAssessments}</span>
                </div>

                <div className="compact-stat-row">
                  <span className="stat-name">{t("profile.latestRisk")}</span>
                  <span
                    className={`risk-status-pill ${
                      stats.latestPrediction === "Diabetic" ? "diabetic" : "non-diabetic"
                    }`}
                  >
                    {stats.latestPrediction
                      ? stats.latestPrediction === "Diabetic"
                        ? t("result.diabetic")
                        : t("result.nonDiabetic")
                      : t("profile.pending")}
                  </span>
                </div>

                <div className="compact-stat-row">
                  <span className="stat-name">{t("dashboard.probability")}</span>
                  <span className="stat-number">
                    {stats.latestRiskScore !== null
                      ? `${stats.latestRiskScore}%`
                      : "N/A"}
                  </span>
                </div>
              </div>

              {/* Patient Quick Info List */}
              <div className="sidebar-info-divider" />
              <div className="sidebar-patient-details">
                <div className="detail-item-line">
                  <span className="item-key"><FaIdBadge /> {t("profile.patientId")}:</span>
                  <span className="item-val">#{userId || "1"}</span>
                </div>
                <div className="detail-item-line">
                  <span className="item-key"><FaCalendarAlt /> {t("profile.memberSince")}:</span>
                  <span className="item-val">{memberSince || "Recent"}</span>
                </div>
              </div>

              {/* Sidebar Quick Action CTAs */}
              <div className="sidebar-action-buttons">
                <button
                  onClick={() => navigate("/assessment")}
                  className="btn-sidebar-cta primary"
                >
                  <FaNotesMedical />
                  <span>{t("dashboard.startNewAssessment")}</span>
                </button>
                <button
                  onClick={() => navigate("/dashboard")}
                  className="btn-sidebar-cta secondary"
                >
                  <FaChartLine />
                  <span>{t("nav.healthDashboard")}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
