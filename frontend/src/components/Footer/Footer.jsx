import "./Footer.css";
import { Link } from "react-router-dom";
import { FaHeartbeat, FaShieldAlt } from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="footer-container">
      <div className="footer-content">
        <div className="footer-grid">
          {/* Brand Info */}
          <div className="footer-brand">
            <div className="footer-logo">
              <FaHeartbeat className="logo-icon" />
              <span>
                DiaSense <strong>AI</strong>
              </span>
            </div>
            <p className="brand-desc">{t("about.desc")}</p>
            <div className="tech-badge">
              <FaShieldAlt /> {t("common.appName")} Healthcare Engine
            </div>
          </div>

          {/* Quick Links */}
          <div className="footer-links-col">
            <h4>Platform</h4>
            <ul>
              <li>
                <Link to="/">{t("nav.home")}</Link>
              </li>
              <li>
                <Link to="/dashboard">{t("nav.dashboard")}</Link>
              </li>
              <li>
                <Link to="/find-care">{t("nav.findCareNearYou")}</Link>
              </li>
              <li>
                <Link to="/assessment">{t("home.startAssessment")}</Link>
              </li>
              <li>
                <Link to="/diet-plan">{t("nav.dietPlan")}</Link>
              </li>
            </ul>
          </div>

          {/* Resources & Info */}
          <div className="footer-links-col">
            <h4>Information</h4>
            <ul>
              <li>
                <Link to="/about">{t("nav.about")}</Link>
              </li>
              <li>
                <Link to="/contact">{t("nav.contact")}</Link>
              </li>
              <li>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                >
                  API Documentation
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>
            © {new Date().getFullYear()} DiaSense AI. {t("common.allRightsReserved")}
          </p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;