import "./RiskGauge.css";
import { motion } from "framer-motion";
import { useTranslation } from "../../context/LanguageContext";

function RiskGauge({ riskPercentage = 50, riskLevel = "", confidence = 95 }) {
  const { t } = useTranslation();
  const risk = Math.min(100, Math.max(0, Math.round(riskPercentage)));

  // Color mapping based on risk level
  const getRiskTheme = (val) => {
    if (val >= 60) return { main: "#f43f5e", bg: "rgba(244, 63, 94, 0.15)", defaultLabel: t("result.highRisk"), statusClass: "high" };
    if (val >= 35) return { main: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)", defaultLabel: t("result.moderateRisk"), statusClass: "moderate" };
    return { main: "#10b981", bg: "rgba(16, 185, 129, 0.15)", defaultLabel: t("result.lowRisk"), statusClass: "low" };
  };

  const theme = getRiskTheme(risk);

  return (
    <div className="risk-gauge-card">
      <div className="gauge-header">
        <h3>{t("result.riskLevel")}</h3>
        <span className={`risk-badge ${theme.statusClass}`}>{riskLevel || theme.defaultLabel}</span>
      </div>

      <div className="circle-wrapper">
        <motion.div
          className="risk-circle"
          initial={{ background: `conic-gradient(#1e293b 0deg, #1e293b 360deg)` }}
          animate={{
            background: `conic-gradient(${theme.main} ${risk * 3.6}deg, #1e293b 0deg)`,
          }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        >
          <div className="risk-value-inner">
            <span className="risk-number">{risk}%</span>
            <span className="risk-sub">{t("dashboard.probability")}</span>
          </div>
        </motion.div>
      </div>

      <div className="confidence-section">
        <div className="confidence-label">
          <span>{t("dashboard.aiConfidence")}</span>
          <strong>{confidence}%</strong>
        </div>
        <div className="confidence-bar-track">
          <motion.div
            className="confidence-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: `${confidence}%` }}
            transition={{ duration: 1.0, delay: 0.2 }}
          />
        </div>
      </div>

      <p className="gauge-footer-tip">
        {risk >= 50
          ? t("result.highRiskTip")
          : t("result.lowRiskTip")}
      </p>
    </div>
  );
}

export default RiskGauge;