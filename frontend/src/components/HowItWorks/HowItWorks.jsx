import "./HowItWorks.css";
import { FaUserEdit, FaMicrochip, FaChartBar, FaFileDownload } from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function HowItWorks() {
  const { t } = useTranslation();

  const steps = [
    {
      number: "01",
      icon: <FaUserEdit />,
      title: t("home.step1Title"),
      desc: t("home.step1Desc"),
    },
    {
      number: "02",
      icon: <FaMicrochip />,
      title: t("home.step2Title"),
      desc: t("home.step2Desc"),
    },
    {
      number: "03",
      icon: <FaChartBar />,
      title: t("home.step3Title"),
      desc: t("home.step3Desc"),
    },
    {
      number: "04",
      icon: <FaFileDownload />,
      title: t("home.step4Title"),
      desc: t("home.step4Desc"),
    },
  ];

  return (
    <section className="how-it-works-section">
      <div className="how-container">
        <div className="section-header text-center">
          <span className="section-subtitle">{t("home.howSubtitle")}</span>
          <h2 className="section-title">{t("home.howTitle")}</h2>
          <p className="section-desc">{t("home.howDesc")}</p>
        </div>

        <div className="steps-grid">
          {steps.map((s, idx) => (
            <div className="step-card" key={idx}>
              <div className="step-header">
                <span className="step-number">{s.number}</span>
                <div className="step-icon">{s.icon}</div>
              </div>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;