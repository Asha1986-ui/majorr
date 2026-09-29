import "./CTA.css";
import { useNavigate } from "react-router-dom";
import { FaArrowRight, FaStethoscope } from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function CTA() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <section className="cta-section">
      <div className="cta-container">
        <div className="cta-card">
          <div className="cta-icon-badge">
            <FaStethoscope />
          </div>
          <h2>{t("home.ctaTitle")}</h2>
          <p>{t("home.ctaDesc")}</p>
          <div className="cta-button-group">
            <button className="cta-main-btn" onClick={() => navigate("/assessment")}>
              {t("home.ctaBtn")} <FaArrowRight />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default CTA;