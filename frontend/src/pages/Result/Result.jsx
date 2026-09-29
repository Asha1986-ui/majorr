import "./Result.css";
import { useEffect, useState } from "react";
import { FaFilePdf, FaFileDownload, FaPrint, FaHeartbeat, FaStethoscope, FaChartLine, FaCheckCircle, FaExclamationTriangle, FaBrain } from "react-icons/fa";
import RiskGauge from "../../components/RiskGauge/RiskGauge";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import Navbar from "../../components/Navbar/Navbar";
import { predictionService, dietService, authService, reportService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";
import { getLocalizedWeeklyDietPlan } from "../../utils/dietSchedules";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

function Result() {
  const { t, currentLanguage } = useTranslation();
  const [userProfile, setUserProfile] = useState(null);
  const [userName, setUserName] = useState("Patient");

  const trendData = [
    { month: t("result.assess1"), risk: 45 },
    { month: t("result.assess2"), risk: 52 },
    { month: t("result.assess3"), risk: 65 },
    { month: t("result.currentAssess"), risk: 78 },
  ];

  const [predictionData, setPredictionData] = useState({
    id: 1,
    prediction: "Non-Diabetic",
    risk_percentage: 24.5,
    confidence: 95.0,
    health_score: 76,
    recommendation: "",
    contributing_factors: []
  });

  const [dietPlan, setDietPlan] = useState(null);

  useEffect(() => {
    // 1. Fetch user profile
    const token = localStorage.getItem("access_token");
    if (token) {
      authService
        .getProfile()
        .then((res) => {
          if (res.data) {
            setUserProfile(res.data);
            setUserName(res.data.full_name || "Patient");
          }
        })
        .catch(() => {});
    }

    // 2. Read stored prediction or fetch latest from API
    const stored = localStorage.getItem("latest_prediction");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.prediction) {
          setPredictionData({
            id: parsed.id || 1,
            prediction: parsed.prediction,
            risk_percentage: parsed.risk_percentage || 25.0,
            confidence: parsed.confidence || 95.0,
            health_score: Math.max(20, Math.round(100 - (parsed.risk_percentage || 25))),
            recommendation: parsed.recommendation || "",
            contributing_factors: parsed.contributing_factors || []
          });
        }
      } catch (e) {}
    }

    // 3. Fetch latest prediction & diet plan from API with current language
    async function fetchLatestData() {
      try {
        const res = await predictionService.getLatest();
        if (res.data) {
          const d = res.data;
          setPredictionData({
            id: d.id || 1,
            prediction: d.prediction,
            risk_percentage: d.risk_percentage,
            confidence: d.confidence,
            health_score: Math.max(20, Math.round(100 - d.risk_percentage)),
            recommendation: d.recommendation,
            contributing_factors: d.contributing_factors || []
          });
        }

        const dietRes = await dietService.getLatestDiet();
        if (dietRes.data) {
          setDietPlan({
            breakfast: dietRes.data.breakfast,
            lunch: dietRes.data.lunch,
            dinner: dietRes.data.dinner,
            exercise: dietRes.data.exercise,
          });
        }
      } catch (e) {
        // Fallback to local state
      }
    }
    fetchLatestData();
  }, [currentLanguage]);

  const handleDownloadPDF = () => {
    if (predictionData.id) {
      const pdfUrl = reportService.getPdfUrl(predictionData.id);
      window.open(pdfUrl, "_blank");
    } else {
      window.print();
    }
  };

  const getImpactLabel = (impact) => {
    if (!impact) return "";
    const lower = impact.toLowerCase();
    if (lower.includes("optimal") || lower.includes("ಸಾಮಾನ್ಯ") || lower.includes("सामान्य") || lower.includes("இயல்பு")) return t("result.optimal");
    if (lower.includes("high") || lower.includes("ಹೆಚ್ಚಿನ") || lower.includes("उच्च") || lower.includes("அதிக") || lower.includes("అధిక") || lower.includes("ഉയർന്ന")) return t("result.highRisk");
    if (lower.includes("moderate") || lower.includes("ಮಧ್ಯಮ") || lower.includes("मध्यम") || lower.includes("மிதமான") || lower.includes("మితమైన") || lower.includes("മിതമായ")) return t("result.moderateRisk");
    return impact;
  };

  const isHighRisk = predictionData.prediction === "Diabetic" || (predictionData.risk_percentage >= 50.0);
  const fallbackSchedule = getLocalizedWeeklyDietPlan(currentLanguage, "Vegetarian", isHighRisk).Monday;

  const currentBreakfast = dietPlan?.breakfast || fallbackSchedule.breakfast;
  const currentLunch = dietPlan?.lunch || fallbackSchedule.lunch;
  const currentDinner = dietPlan?.dinner || fallbackSchedule.dinner;
  const currentExercise = dietPlan?.exercise || (isHighRisk ? t("dietPlan.exerciseItem1") : t("dietPlan.exerciseItem2"));
  const currentRecommendation = predictionData.recommendation || (isHighRisk ? t("result.descGlucoseHigh") : t("result.descGlucoseOpt"));

  return (
    <>
      <Navbar />

      <div className="result-page">
        <div className="result-container">
          <BackButton />

          {/* Clinical Report Header */}
          <header className="report-header-card">
            <div className="header-left">
              <div className="report-badge">
                <FaStethoscope /> {t("result.headerBadge")}
              </div>
              <h1>{t("result.headerTitle")}</h1>
              <p>{t("result.assessmentId")}: <strong>REP-{predictionData.id ? String(predictionData.id).padStart(5, '0') : "00001"}</strong> | {t("result.patient")}: <strong>{userName}</strong></p>
            </div>

            <div className="header-actions">
              <button className="btn-action secondary no-print" onClick={() => window.print()}>
                <FaPrint /> {t("result.printReport")}
              </button>
              <button className="btn-action primary no-print" onClick={handleDownloadPDF}>
                <FaFileDownload /> {t("result.downloadPdf")}
              </button>
            </div>
          </header>

          {/* Top Metric Cards Section */}
          <div className="report-score-grid">
            <RiskGauge
              riskPercentage={predictionData.risk_percentage}
              riskLevel={predictionData.prediction === "Diabetic" ? t("result.diabetic") : t("result.nonDiabetic")}
              confidence={predictionData.confidence}
            />

            <div className="score-summary-card">
              <div className="card-top">
                <span>{t("result.healthScore")}</span>
                <span className="health-score-val">{predictionData.health_score} / 100</span>
              </div>
              <div className="score-progress-bar">
                <div
                  className="score-progress-fill"
                  style={{
                    width: `${predictionData.health_score}%`,
                    background: predictionData.health_score >= 70 ? "#10b981" : "#f59e0b"
                  }}
                />
              </div>
              <div className="ai-insight-box">
                <h4><FaBrain /> {t("result.aiSummaryTitle")}</h4>
                <p>{currentRecommendation}</p>
              </div>
            </div>
          </div>

          {/* Explainability Matrix */}
          {predictionData.contributing_factors && predictionData.contributing_factors.length > 0 && (
            <div className="content-card">
              <h2><FaStethoscope /> {t("result.factorsTitle")}</h2>
              <p className="card-subtitle">{t("result.factorsDesc")}</p>

              <div className="explainability-grid">
                {predictionData.contributing_factors.map((item, idx) => (
                  <div className="factor-item-card" key={idx}>
                    <div className="factor-header">
                      <span className="factor-name">{item.factor}</span>
                      <span className={`impact-tag ${String(item.impact).toLowerCase().replace(/\s+/g, '-')}`}>
                        {item.impact === "High Risk" && <FaExclamationTriangle />}
                        {item.impact === "Optimal" && <FaCheckCircle />}
                        {getImpactLabel(item.impact)}
                      </span>
                    </div>
                    <div className="factor-value">{t("result.measuredValue")}: <strong>{item.value}</strong></div>
                    <p className="factor-desc">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Health Risk Trajectory Graph */}
          <div className="content-card">
            <h2><FaChartLine /> {t("result.trajectoryTitle")}</h2>
            <p className="card-subtitle">{t("result.trajectoryDesc")}</p>

            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="month" stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1e293b", borderColor: "rgba(255,255,255,0.1)", borderRadius: "12px", color: "#f8fafc" }}
                  />
                  <Line type="monotone" dataKey="risk" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 6, fill: "#0ea5e9" }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recommended Diet & Exercise Guidance */}
          <div className="content-card">
            <h2>🥗 {t("result.recommendationsTitle")}</h2>

            <div className="plan-cards-grid">
              <div className="plan-block">
                <div className="plan-header">
                  <span className="plan-icon">🌅</span>
                  <h3>{t("result.breakfastGuidance")}</h3>
                </div>
                <p>{currentBreakfast}</p>
              </div>

              <div className="plan-block">
                <div className="plan-header">
                  <span className="plan-icon">☀️</span>
                  <h3>{t("result.lunchGuidance")}</h3>
                </div>
                <p>{currentLunch}</p>
              </div>

              <div className="plan-block">
                <div className="plan-header">
                  <span className="plan-icon">🌙</span>
                  <h3>{t("result.dinnerGuidance")}</h3>
                </div>
                <p>{currentDinner}</p>
              </div>

              <div className="plan-block highlight">
                <div className="plan-header">
                  <span className="plan-icon">🏃</span>
                  <h3>{t("result.exerciseGuidance")}</h3>
                </div>
                <p>{currentExercise}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}

export default Result;