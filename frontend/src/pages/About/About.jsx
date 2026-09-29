import "./About.css";
import Navbar from "../../components/Navbar/Navbar";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import { FaBrain, FaDatabase, FaShieldAlt } from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function About() {
  const { t } = useTranslation();

  return (
    <>
      <Navbar />

      <div className="about-page">
        <div className="about-container">
          <BackButton />

          {/* Hero */}
          <section className="about-hero text-center">
            <span className="badge-pill">{t("about.badge")}</span>
            <h1>{t("about.title")}</h1>
            <p>{t("about.desc")}</p>
          </section>

          {/* Mission Card */}
          <section className="about-card">
            <h2><FaBrain /> {t("about.missionTitle")}</h2>
            <p>{t("about.missionDesc")}</p>
          </section>

          {/* Tech Stack Specs */}
          <section className="about-grid">
            <div className="spec-card">
              <div className="spec-icon"><FaBrain /></div>
              <h3>{t("about.mlArchTitle")}</h3>
              <p>
                <strong>{t("about.algorithm")}</strong> {t("about.algorithmDesc")}<br />
                <strong>{t("about.dataset")}</strong> {t("about.datasetDesc")}<br />
                <strong>{t("about.modelAccuracy")}</strong> {t("about.modelAccuracyDesc")}<br />
                <strong>{t("about.evaluation")}</strong> {t("about.evaluationDesc")}
              </p>
            </div>

            <div className="spec-card">
              <div className="spec-icon cyan"><FaDatabase /></div>
              <h3>{t("about.techArchTitle")}</h3>
              <p>
                <strong>{t("about.backend")}</strong> {t("about.backendDesc")}<br />
                <strong>{t("about.frontend")}</strong> {t("about.frontendDesc")}<br />
                <strong>{t("about.multilingual")}</strong> {t("about.multilingualDesc")}<br />
                <strong>{t("about.database")}</strong> {t("about.databaseDesc")}
              </p>
            </div>

            <div className="spec-card">
              <div className="spec-icon emerald"><FaShieldAlt /></div>
              <h3>{t("about.securityTitle")}</h3>
              <p>
                <strong>{t("about.auth")}</strong> {t("about.authDesc")}<br />
                <strong>{t("about.hashing")}</strong> {t("about.hashingDesc")}<br />
                <strong>{t("about.authorization")}</strong> {t("about.authorizationDesc")}<br />
                <strong>{t("about.validation")}</strong> {t("about.validationDesc")}
              </p>
            </div>
          </section>
        </div>
      </div>

      <Footer />
    </>
  );
}

export default About;