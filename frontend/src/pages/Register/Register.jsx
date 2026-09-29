import "../Login/Login.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { FaUser, FaEnvelope, FaLock, FaEye, FaEyeSlash, FaCheckCircle, FaTimesCircle, FaArrowLeft, FaShieldAlt, FaCalendarAlt, FaVenusMars } from "react-icons/fa";
import { authService } from "../../services/api";
import AuthShowcase from "../../components/AuthShowcase/AuthShowcase";
import { useTranslation } from "../../context/LanguageContext";

function Register() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Male");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  // Real-time password criteria validations
  const criteria = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  const isPasswordValid = Object.values(criteria).every(Boolean);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      toast.error(t("auth.fillRequiredFields"));
      return;
    }

    if (!isPasswordValid) {
      toast.error(t("auth.passwordRequirements"));
      return;
    }

    if (password !== confirmPassword) {
      toast.error(t("auth.pwMatchError"));
      return;
    }

    setLoading(true);
    try {
      const response = await authService.register({
        full_name: fullName,
        email: email,
        password: password,
        age: age ? parseInt(age, 10) : undefined,
        gender: gender || "Male",
      });

      const authData = response.data;
      localStorage.setItem("access_token", authData.access_token);
      localStorage.setItem("user", JSON.stringify(authData));

      toast.success(`✅ ${t("auth.registeredSuccess")}`);
      setTimeout(() => {
        navigate("/dashboard");
      }, 700);
    } catch (err) {
      toast.error(err.message || t("auth.regFailedEmailExists"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split-page">
      {/* Background Glow Accents */}
      <div className="auth-bg-glow-1" />
      <div className="auth-bg-glow-2" />

      <div className="auth-split-container">
        {/* Floating Back Button */}
        <button className="auth-back-floating-btn" onClick={() => navigate("/")}>
          <FaArrowLeft /> {t("common.backToHome")}
        </button>

        {/* Left Side Designed Medical AI Showcase */}
        <AuthShowcase />

        {/* Right Side Registration Form */}
        <div className="auth-right-form">
          <div className="auth-form-card">
            <div className="form-header">
              <h1>{t("auth.registerTitle")}</h1>
              <p>{t("auth.registerSubtitle")}</p>
            </div>

            <form onSubmit={handleRegister}>
              <div className="form-input-group">
                <label><FaUser /> {t("auth.fullNameLabel")}</label>
                <input
                  type="text"
                  placeholder={t("auth.fullNamePlaceholder")}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>

              <div className="form-input-group">
                <label><FaEnvelope /> {t("auth.emailLabel")}</label>
                <input
                  type="email"
                  placeholder={t("auth.emailPlaceholder")}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              {/* Age and Gender Inputs */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.85rem" }}>
                <div className="form-input-group">
                  <label><FaCalendarAlt /> {t("auth.ageLabel")}</label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    placeholder="e.g. 35"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                  />
                </div>

                <div className="form-input-group">
                  <label><FaVenusMars /> {t("auth.genderLabel")}</label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    style={{
                      width: "100%",
                      padding: "0.85rem 1rem",
                      borderRadius: "12px",
                      background: "#0f172a",
                      border: "1px solid rgba(255, 255, 255, 0.12)",
                      color: "#f8fafc",
                      fontSize: "0.95rem"
                    }}
                  >
                    <option value="Male">{t("auth.male")}</option>
                    <option value="Female">{t("auth.female")}</option>
                    <option value="Other">{t("auth.other")}</option>
                  </select>
                </div>
              </div>

              <div className="form-input-group">
                <label><FaLock /> {t("auth.passwordLabel")}</label>
                <div className="password-wrapper">
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder={t("auth.passwordPlaceholder")}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    className="toggle-pw-btn"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
              </div>

              {/* Password Criteria Real-Time Checklist */}
              {password.length > 0 && (
                <div className="password-criteria-box">
                  <div className="criteria-title"><FaShieldAlt /> {t("profile.passCriteriaTitle")}</div>
                  <div className="criteria-list">
                    <div className={`criteria-item ${criteria.length ? "valid" : "invalid"}`}>
                      {criteria.length ? <FaCheckCircle className="crit-icon" /> : <FaTimesCircle className="crit-icon" />}
                      {t("profile.critLength")}
                    </div>
                    <div className={`criteria-item ${criteria.uppercase ? "valid" : "invalid"}`}>
                      {criteria.uppercase ? <FaCheckCircle className="crit-icon" /> : <FaTimesCircle className="crit-icon" />}
                      {t("profile.critUpper")}
                    </div>
                    <div className={`criteria-item ${criteria.lowercase ? "valid" : "invalid"}`}>
                      {criteria.lowercase ? <FaCheckCircle className="crit-icon" /> : <FaTimesCircle className="crit-icon" />}
                      {t("profile.critLower")}
                    </div>
                    <div className={`criteria-item ${criteria.number ? "valid" : "invalid"}`}>
                      {criteria.number ? <FaCheckCircle className="crit-icon" /> : <FaTimesCircle className="crit-icon" />}
                      {t("profile.critNumber")}
                    </div>
                    <div className={`criteria-item ${criteria.special ? "valid" : "invalid"}`}>
                      {criteria.special ? <FaCheckCircle className="crit-icon" /> : <FaTimesCircle className="crit-icon" />}
                      {t("profile.critSpecial")}
                    </div>
                  </div>
                </div>
              )}

              <div className="form-input-group">
                <label><FaLock /> {t("auth.confirmPasswordLabel")}</label>
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder={t("auth.confirmPasswordPlaceholder")}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>

              <button className="auth-submit-btn" type="submit" disabled={loading}>
                {loading ? t("common.loading") : `${t("auth.registerBtn")} →`}
              </button>
            </form>

            <div className="auth-footer-link">
              {t("auth.haveAccount")} <Link to="/login">{t("auth.loginLink")}</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;