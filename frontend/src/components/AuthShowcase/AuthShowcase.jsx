import React from "react";
import "./AuthShowcase.css";
import { 
  FaHeartbeat, 
  FaBrain, 
  FaChartLine, 
  FaShieldAlt, 
  FaUsers, 
  FaTint, 
  FaDna
} from "react-icons/fa";
import { useTranslation } from "../../context/LanguageContext";

function AuthShowcase() {
  const { t } = useTranslation();

  return (
    <div className="auth-showcase-panel">
      {/* Dynamic Background Mesh Gradients */}
      <div className="showcase-mesh-glow-1" />
      <div className="showcase-mesh-glow-2" />
      <div className="showcase-mesh-glow-3" />

      {/* Top Header Branding */}
      <div className="showcase-top-brand">
        <div className="brand-icon-capsule">
          <FaHeartbeat className="brand-pulse-icon" />
        </div>
        <div className="brand-text-block">
          <h3>DiaSense AI</h3>
          <span>{t("home.heroBadge")}</span>
        </div>
      </div>

      {/* Hero Headings */}
      <div className="showcase-hero-heading">
        <h2>
          {t("auth.showcaseHeading")}
        </h2>
        <p>
          {t("home.heroDesc")}
        </p>
      </div>

      {/* Main Interactive Visual Centerpiece */}
      <div className="showcase-visual-container">
        {/* Left Side: 3 Feature Capsules */}
        <div className="showcase-feature-list">
          <div className="feature-pill-card">
            <div className="pill-icon-circle cyan">
              <FaBrain />
            </div>
            <div className="pill-text">
              <h4>{t("home.feat1Title")}</h4>
              <p>{t("auth.showcaseP1")}</p>
            </div>
          </div>

          <div className="feature-pill-card">
            <div className="pill-icon-circle blue">
              <FaChartLine />
            </div>
            <div className="pill-text">
              <h4>{t("home.feat2Title")}</h4>
              <p>{t("auth.showcaseP2")}</p>
            </div>
          </div>

          <div className="feature-pill-card">
            <div className="pill-icon-circle indigo">
              <FaShieldAlt />
            </div>
            <div className="pill-text">
              <h4>{t("home.feat6Title")}</h4>
              <p>{t("auth.showcaseP3")}</p>
            </div>
          </div>
        </div>

        {/* Right Side: Designed Medical Device & Telemetry Visual */}
        <div className="medical-visual-display">
          {/* Radar Target Circles */}
          <div className="radar-circle radar-outer" />
          <div className="radar-circle radar-middle" />
          <div className="radar-circle radar-inner" />

          {/* Glowing Pancreas & Organ Cell Hologram */}
          <div className="pancreas-hologram-card">
            <div className="hologram-bubble">
              <FaDna className="organ-holo-icon" />
              <span className="organ-tag">{t("auth.betaCellsActive")}</span>
            </div>
            <div className="hologram-glow-orbit" />
          </div>

          {/* Designed Glucometer Device */}
          <div className="glucometer-device-mockup">
            <div className="glucometer-case">
              <div className="glucometer-screen">
                <div className="screen-header">
                  <span className="blood-icon"><FaTint /></span>
                  <span className="screen-tag">{t("dietPlan.glucoseLabel").toUpperCase().replace(":", "")}</span>
                </div>
                <div className="screen-reading">
                  <span className="reading-value">105</span>
                  <span className="reading-unit">mg/dL</span>
                </div>
                <div className="screen-status-bar">
                  <span className="status-dot green" />
                  <span className="status-label">{t("result.optimal")}</span>
                </div>
              </div>

              {/* Device Controls */}
              <div className="device-controls">
                <button type="button" className="dev-btn btn-up" tabIndex={-1}>▲</button>
                <button type="button" className="dev-btn btn-down" tabIndex={-1}>▼</button>
              </div>

              {/* Test Strip */}
              <div className="device-test-strip">
                <div className="strip-sensor-pad" />
              </div>
            </div>
          </div>

          {/* Real-Time Live ECG Pulse Wave SVG */}
          <div className="ecg-waveform-card">
            <svg className="ecg-svg" viewBox="0 0 200 45" preserveAspectRatio="none">
              <defs>
                <linearGradient id="ecgGlow" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="rgba(14, 165, 233, 0.2)" />
                  <stop offset="50%" stopColor="#38bdf8" />
                  <stop offset="100%" stopColor="#818cf8" />
                </linearGradient>
              </defs>
              <path
                d="M 0 25 L 30 25 L 35 22 L 40 25 L 55 25 L 60 10 L 65 38 L 70 5 L 75 28 L 80 25 L 110 25 L 115 12 L 120 35 L 125 7 L 130 25 L 160 25 L 165 20 L 170 25 L 200 25"
                fill="none"
                stroke="url(#ecgGlow)"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="ecg-telemetry-badge">
              <span className="live-pulse-dot" /> 72 BPM • {t("auth.normalRhythm")}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Social Proof Pill Card */}
      <div className="showcase-bottom-card">
        <div className="users-icon-circle">
          <FaUsers />
        </div>
        <span>{t("common.appName")} {t("auth.healthcareIntelPlatform")}</span>
      </div>

      {/* Footer Copyright */}
      <div className="showcase-footer-note">
        © {new Date().getFullYear()} DiaSense AI. {t("common.allRightsReserved")}
      </div>
    </div>
  );
}

export default AuthShowcase;
