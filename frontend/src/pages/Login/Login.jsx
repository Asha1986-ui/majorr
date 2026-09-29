import "./Login.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { FaEnvelope, FaLock, FaEye, FaEyeSlash, FaArrowLeft } from "react-icons/fa";
import { authService } from "../../services/api";
import AuthShowcase from "../../components/AuthShowcase/AuthShowcase";
import { useTranslation } from "../../context/LanguageContext";

function Login() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error(t("auth.enterEmailPassword"));
      return;
    }

    setLoading(true);
    try {
      const response = await authService.login({ email, password });
      const authData = response.data;

      localStorage.setItem("access_token", authData.access_token);
      localStorage.setItem("user", JSON.stringify(authData));

      toast.success(`✅ ${t("auth.signedInSuccess")}`);
      setTimeout(() => {
        navigate("/dashboard");
      }, 700);
    } catch (err) {
      toast.error(err.message || t("auth.invalidCredentials"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split-page">
      {/* Background Decorative Glow Elements */}
      <div className="auth-bg-glow-1" />
      <div className="auth-bg-glow-2" />

      <div className="auth-split-container">
        {/* Floating Back Button */}
        <button className="auth-back-floating-btn" onClick={() => navigate("/")}>
          <FaArrowLeft /> {t("common.backToHome")}
        </button>

        {/* Left Side Designed Medical AI Showcase */}
        <AuthShowcase />

        {/* Right Side Form Card */}
        <div className="auth-right-form">
          <div className="auth-form-card">
            <div className="form-header">
              <h1>{t("auth.signInTitle")}</h1>
              <p>{t("auth.signInSubtitle")}</p>
            </div>

            <form onSubmit={handleLogin}>
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

              <button className="auth-submit-btn" type="submit" disabled={loading}>
                {loading ? t("common.loading") : `${t("auth.signInBtn")} →`}
              </button>
            </form>

            <div className="auth-footer-link">
              {t("auth.noAccount")} <Link to="/register">{t("auth.registerLink")}</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;