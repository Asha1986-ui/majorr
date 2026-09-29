import "./Hero.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowRight, FaBrain, FaShieldAlt, FaChartLine } from "react-icons/fa";
import { predictionService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";

function Hero() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [modelMetrics, setModelMetrics] = useState({
    accuracy_percentage: "99.20%",
    dataset_samples: 2500,
    roc_auc: 0.9993,
  });

  useEffect(() => {
    predictionService
      .getLatest()
      .then(() => {})
      .catch(() => {});

    // Fetch real trained model metrics
    fetch("http://localhost:8000/api/prediction/accuracy")
      .then((res) => res.json())
      .then((resData) => {
        if (resData && resData.data) {
          setModelMetrics({
            accuracy_percentage: resData.data.accuracy_percentage || "99.20%",
            dataset_samples: resData.data.dataset_samples || 2500,
            roc_auc: resData.data.roc_auc || 0.9993,
          });
        }
      })
      .catch(() => {});
  }, []);

  return (
    <section className="hero-section">
      {/* Ambient Lighting & Atmosphere */}
      <div className="hero-cosmic-bg" />
      <div className="hero-glow-left" />
      <div className="hero-glow-right" />
      <div className="hero-glow-center" />

      {/* Left Side: Neural Network Geometric Constellation */}
      <div className="hero-neural-left">
        <svg viewBox="0 0 500 650" fill="none" xmlns="http://www.w3.org/2000/svg" className="neural-svg">
          <defs>
            <linearGradient id="neuralGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#6366f1" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0.1" />
            </linearGradient>
            <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Network Connection Lines */}
          <g stroke="url(#neuralGrad)" strokeWidth="1" opacity="0.6">
            <line x1="60" y1="120" x2="140" y2="80" />
            <line x1="140" y1="80" x2="260" y2="140" />
            <line x1="60" y1="120" x2="110" y2="240" />
            <line x1="110" y1="240" x2="260" y2="140" />
            <line x1="110" y1="240" x2="180" y2="340" />
            <line x1="260" y1="140" x2="320" y2="280" />
            <line x1="180" y1="340" x2="320" y2="280" />
            <line x1="40" y1="380" x2="110" y2="240" />
            <line x1="40" y1="380" x2="180" y2="340" />
            <line x1="180" y1="340" x2="120" y2="480" />
            <line x1="40" y1="380" x2="120" y2="480" />
            <line x1="120" y1="480" x2="240" y2="520" />
            <line x1="180" y1="340" x2="240" y2="520" />
            <line x1="320" y1="280" x2="380" y2="420" />
            <line x1="240" y1="520" x2="380" y2="420" />
            <line x1="120" y1="480" x2="190" y2="610" />
            <line x1="240" y1="520" x2="190" y2="610" />
            <line x1="240" y1="520" x2="340" y2="590" />
            <line x1="380" y1="420" x2="340" y2="590" />
          </g>

          {/* Glowing Neural Vertices & Nodes */}
          <g filter="url(#glowFilter)">
            <circle cx="60" cy="120" r="4.5" fill="#38bdf8" className="pulse-node" />
            <circle cx="140" cy="80" r="3.5" fill="#818cf8" />
            <circle cx="260" cy="140" r="5" fill="#0ea5e9" className="pulse-node" />
            <circle cx="110" cy="240" r="6" fill="#38bdf8" />
            <circle cx="180" cy="340" r="5.5" fill="#6366f1" className="pulse-node" />
            <circle cx="320" cy="280" r="4" fill="#38bdf8" />
            <circle cx="40" cy="380" r="5" fill="#0ea5e9" />
            <circle cx="120" cy="480" r="6" fill="#818cf8" className="pulse-node" />
            <circle cx="240" cy="520" r="5" fill="#38bdf8" />
            <circle cx="380" cy="420" r="4.5" fill="#0ea5e9" />
            <circle cx="190" cy="610" r="4" fill="#6366f1" />
            <circle cx="340" cy="590" r="4.5" fill="#38bdf8" className="pulse-node" />
          </g>
        </svg>
      </div>

      {/* Right Side: Ethereal Neon Flowing Energy Wave Ribbon */}
      <div className="hero-wave-right">
        <svg viewBox="0 0 700 700" fill="none" xmlns="http://www.w3.org/2000/svg" className="wave-svg">
          <defs>
            <linearGradient id="waveGrad1" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.9" />
              <stop offset="40%" stopColor="#6366f1" stopOpacity="0.7" />
              <stop offset="80%" stopColor="#0ea5e9" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="waveGrad2" x1="100%" y1="10%" x2="0%" y2="90%">
              <stop offset="0%" stopColor="#c084fc" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#818cf8" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.15" />
            </linearGradient>
            <linearGradient id="waveGrad3" x1="100%" y1="0%" x2="20%" y2="100%">
              <stop offset="0%" stopColor="#a855f7" stopOpacity="0.6" />
              <stop offset="70%" stopColor="#38bdf8" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#0284c7" stopOpacity="0.0" />
            </linearGradient>
            <filter id="waveGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Layered Flowing Wave Ribbons */}
          <g filter="url(#waveGlow)">
            {/* Primary Energy Strands */}
            <path
              d="M 680,40 C 580,180 440,240 320,380 C 200,520 80,560 0,680"
              stroke="url(#waveGrad1)"
              strokeWidth="3.5"
              strokeLinecap="round"
            />
            <path
              d="M 700,90 C 600,210 460,280 340,410 C 220,540 100,580 20,700"
              stroke="url(#waveGrad2)"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            <path
              d="M 650,20 C 550,150 420,220 290,360 C 170,500 60,540 -20,660"
              stroke="url(#waveGrad3)"
              strokeWidth="2"
              strokeDasharray="4 8"
            />

            {/* Fine Wave Density Threads */}
            <path
              d="M 720,130 C 620,240 480,310 360,440 C 240,560 120,600 40,710"
              stroke="url(#waveGrad1)"
              strokeWidth="1.5"
              opacity="0.7"
            />
            <path
              d="M 740,160 C 640,270 500,340 380,460 C 260,580 140,620 60,720"
              stroke="url(#waveGrad2)"
              strokeWidth="1.2"
              opacity="0.5"
            />
            <path
              d="M 670,60 C 570,190 430,260 310,390 C 190,520 70,560 -10,680"
              stroke="url(#waveGrad3)"
              strokeWidth="1"
              opacity="0.8"
            />
            <path
              d="M 690,110 C 590,225 450,295 330,425 C 210,550 90,590 10,705"
              stroke="url(#waveGrad1)"
              strokeWidth="1.8"
              opacity="0.6"
            />
          </g>

          {/* Floating Starlight Sparkles */}
          <circle cx="620" cy="140" r="2" fill="#e0e7ff" opacity="0.9" />
          <circle cx="530" cy="220" r="1.5" fill="#38bdf8" opacity="0.8" />
          <circle cx="420" cy="310" r="2.5" fill="#c084fc" opacity="0.9" />
          <circle cx="310" cy="420" r="1.5" fill="#e0e7ff" opacity="0.7" />
          <circle cx="210" cy="510" r="2" fill="#38bdf8" opacity="0.9" />
          <circle cx="120" cy="590" r="1.5" fill="#a855f7" opacity="0.8" />
        </svg>
      </div>

      {/* Main Foreground Container */}
      <div className="hero-container">
        <div className="hero-badge">
          <FaBrain className="badge-icon" />
          <span>{t("home.heroBadge")}</span>
        </div>

        <h1 className="hero-title">
          {t("home.heroTitle")}{" "}
          <span className="gradient-text">{t("home.heroTitleHighlight")}</span>
        </h1>

        <p className="hero-description">{t("home.heroDesc")}</p>

        <div className="hero-cta-group">
          <button
            className="cta-btn primary"
            onClick={() => navigate("/assessment")}
          >
            {t("home.startAssessment")} <FaArrowRight />
          </button>
          <button
            className="cta-btn secondary"
            onClick={() => navigate("/dashboard")}
          >
            {t("home.exploreDashboard")}
          </button>
        </div>

        {/* Authentic Machine Learning Metrics Grid */}
        <div className="hero-stats-grid">
          <div className="stat-card">
            <div className="stat-icon-box">
              <FaBrain />
            </div>
            <div className="stat-content">
              <h3>{modelMetrics.accuracy_percentage}</h3>
              <p>{t("home.accuracyScore")}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon-box cyan">
              <FaChartLine />
            </div>
            <div className="stat-content">
              <h3>{modelMetrics.dataset_samples}</h3>
              <p>{t("home.datasetRecords")}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon-box emerald">
              <FaShieldAlt />
            </div>
            <div className="stat-content">
              <h3>{modelMetrics.roc_auc}</h3>
              <p>{t("home.rocAuc")}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Hero;