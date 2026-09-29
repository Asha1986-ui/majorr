import "./Features.css";
import { FaBrain, FaChartPie, FaUtensils, FaRunning, FaFilePdf, FaLock } from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function Features() {
  const { t } = useTranslation();

  const featuresList = [
    {
      icon: <FaBrain />,
      title: t("home.feat1Title"),
      desc: t("home.feat1Desc"),
    },
    {
      icon: <FaChartPie />,
      title: t("home.feat2Title"),
      desc: t("home.feat2Desc"),
    },
    {
      icon: <FaUtensils />,
      title: t("home.feat3Title"),
      desc: t("home.feat3Desc"),
    },
    {
      icon: <FaRunning />,
      title: t("home.feat4Title"),
      desc: t("home.feat4Desc"),
    },
    {
      icon: <FaFilePdf />,
      title: t("home.feat5Title"),
      desc: t("home.feat5Desc"),
    },
    {
      icon: <FaLock />,
      title: t("home.feat6Title"),
      desc: t("home.feat6Desc"),
    },
  ];

  return (
    <section className="features-section">
      <div className="features-container">
        <div className="section-header text-center">
          <span className="section-subtitle">{t("home.featuresSubtitle")}</span>
          <h2 className="section-title">{t("home.featuresTitle")}</h2>
          <p className="section-desc">{t("home.featuresDesc")}</p>
        </div>

        <div className="features-grid">
          {featuresList.map((item, idx) => (
            <div className="feature-card" key={idx}>
              <div className="feature-icon-box">{item.icon}</div>
              <h3>{item.title}</h3>
              <p>{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Features;