import "./FoodAnalyzer.css";
import { useState } from "react";
import { toast } from "react-toastify";
import Navbar from "../../components/Navbar/Navbar";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import {
  FaCamera,
  FaSearch,
  FaUtensils,
  FaCheckCircle,
  FaExclamationTriangle,
  FaCloudUploadAlt,
  FaFire,
  FaBreadSlice,
  FaDrumstickBite,
  FaAppleAlt,
  FaChartPie,
  FaLightbulb,
  FaSpinner
} from "react-icons/fa";
import { foodService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";

const SAMPLE_DISH_KEYS = [
  "dishOatsDosa",
  "dishPalakPaneer",
  "dishMoongKhichdi",
  "dishChickenTikka",
  "dishBrownRiceRajma",
  "dishGulabJamun",
  "dishMasalaDosa",
];

function FoodAnalyzer() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState("image"); // "image" or "text"
  const [textQuery, setTextQuery] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        toast.error(t("foodAnalyzer.invalidImageToast"));
        return;
      }
      setSelectedFile(file);
      setImagePreview(URL.createObjectURL(file));
      setAnalysisResult(null);
    }
  };

  const handleImageSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      toast.error(t("foodAnalyzer.selectImageToast"));
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await foodService.analyzeImage(formData);
      if (res && res.data) {
        setAnalysisResult(res.data);
        toast.success(`✅ ${t("foodAnalyzer.imageSuccess")}`);
      }
    } catch (err) {
      toast.error(err.message || "Failed to analyze food image.");
    } finally {
      setLoading(false);
    }
  };

  const handleTextSubmit = async (queryToUse) => {
    const query = queryToUse || textQuery;
    if (!query.trim()) {
      toast.error(t("foodAnalyzer.enterMealToast"));
      return;
    }

    setLoading(true);
    try {
      const res = await foodService.analyzeText(query);
      if (res && res.data) {
        setAnalysisResult(res.data);
        toast.success(`✅ ${t("foodAnalyzer.textSuccess")}`);
      }
    } catch (err) {
      toast.error(err.message || "Failed to calculate meal nutrition.");
    } finally {
      setLoading(false);
    }
  };

  const getSuitabilityBadge = (suitability, color) => {
    let localizedLabel = suitability;
    if (color === "emerald" || suitability?.toLowerCase().includes("friendly") || suitability?.toLowerCase().includes("ಸ್ನೇಹಿ")) {
      localizedLabel = t("foodAnalyzer.suitDiabeticFriendly");
      return (
        <div className="suitability-pill emerald">
          <FaCheckCircle /> 🟢 {localizedLabel} ({t("foodAnalyzer.lowGi")})
        </div>
      );
    } else if (color === "amber" || suitability?.toLowerCase().includes("moderate") || suitability?.toLowerCase().includes("ಮಧ್ಯಮ")) {
      localizedLabel = t("foodAnalyzer.suitModeratePortion");
      return (
        <div className="suitability-pill amber">
          <FaExclamationTriangle /> 🟡 {localizedLabel} ({t("foodAnalyzer.modGi")})
        </div>
      );
    }
    localizedLabel = t("foodAnalyzer.suitHighRiskLimit");
    return (
      <div className="suitability-pill red">
        <FaExclamationTriangle /> 🔴 {localizedLabel} ({t("foodAnalyzer.highGi")})
      </div>
    );
  };

  return (
    <>
      <Navbar />

      <div className="food-analyzer-page">
        <div className="food-analyzer-container">
          <BackButton />

          {/* Page Header */}
          <div className="food-header text-center">
            <span className="badge-pill"><FaUtensils /> {t("foodAnalyzer.headerBadge")}</span>
            <h1>{t("foodAnalyzer.headerTitle")}</h1>
            <p>{t("foodAnalyzer.headerDesc")}</p>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="analyzer-tabs">
            <button
              className={`tab-btn ${activeTab === "image" ? "active" : ""}`}
              onClick={() => setActiveTab("image")}
            >
              <FaCamera /> 📸 {t("foodAnalyzer.tabImage")}
            </button>
            <button
              className={`tab-btn ${activeTab === "text" ? "active" : ""}`}
              onClick={() => setActiveTab("text")}
            >
              <FaSearch /> 🔍 {t("foodAnalyzer.tabText")}
            </button>
          </div>

          {/* Mode 1: AI Food Image Upload */}
          {activeTab === "image" && (
            <div className="analyzer-card">
              <h2>📸 {t("foodAnalyzer.uploadTitle")}</h2>
              <p className="card-subtext">{t("foodAnalyzer.uploadSubtext")}</p>

              <form onSubmit={handleImageSubmit} className="image-upload-form">
                <div className="upload-dropzone">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    id="food-image-input"
                    className="file-input-hidden"
                  />
                  <label htmlFor="food-image-input" className="dropzone-label">
                    {imagePreview ? (
                      <div className="preview-box">
                        <img src={imagePreview} alt="Food Preview" className="uploaded-preview-img" />
                        <span className="change-img-text">{t("foodAnalyzer.clickChange")}</span>
                      </div>
                    ) : (
                      <div className="dropzone-prompt">
                        <FaCloudUploadAlt className="upload-icon" />
                        <h3>{t("foodAnalyzer.dropPrompt")}</h3>
                        <p>{t("foodAnalyzer.dropDesc")}</p>
                      </div>
                    )}
                  </label>
                </div>

                <button type="submit" className="analyze-btn" disabled={loading || !selectedFile}>
                  {loading ? (
                    <>
                      <FaSpinner className="spin-icon" /> {t("foodAnalyzer.scanningBtn")}
                    </>
                  ) : (
                    <>
                      <FaCamera /> {t("foodAnalyzer.analyzeBtn")}
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Mode 2: Meal Text Search */}
          {activeTab === "text" && (
            <div className="analyzer-card">
              <h2>🔍 {t("foodAnalyzer.textTitle")}</h2>
              <p className="card-subtext">{t("foodAnalyzer.textSubtext")}</p>

              <div className="text-search-box">
                <input
                  type="text"
                  placeholder={t("foodAnalyzer.textPlaceholder")}
                  value={textQuery}
                  onChange={(e) => setTextQuery(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleTextSubmit()}
                />
                <button className="search-btn" onClick={() => handleTextSubmit()} disabled={loading}>
                  {loading ? <FaSpinner className="spin-icon" /> : <><FaSearch /> {t("common.search")}</>}
                </button>
              </div>

              {/* Sample Quick Chips */}
              <div className="sample-chips-bar">
                <span className="chips-title"><FaLightbulb /> {t("foodAnalyzer.tryQuick")}</span>
                <div className="chips-wrapper">
                  {SAMPLE_DISH_KEYS.map((dishKey, idx) => {
                    const localizedDish = t(`foodAnalyzer.${dishKey}`);
                    return (
                      <button
                        key={idx}
                        className="sample-chip-btn"
                        onClick={() => {
                          setTextQuery(localizedDish);
                          handleTextSubmit(localizedDish);
                        }}
                        disabled={loading}
                      >
                        {localizedDish}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Analysis Results Display */}
          {analysisResult && (
            <div className="food-result-card">
              <div className="result-header-row">
                <div>
                  <span className="dish-eyebrow">{t("foodAnalyzer.identifiedDish")}</span>
                  <h2>{analysisResult.dish_name}</h2>
                </div>
                {getSuitabilityBadge(analysisResult.overall_suitability, analysisResult.suitability_color)}
              </div>

              {/* 4 Essential Metrics Summary */}
              <div className="nutrition-stats-grid">
                <div className="nutri-stat-box cal">
                  <FaFire className="stat-icon" />
                  <span className="stat-value">{analysisResult.total_calories_kcal}</span>
                  <span className="stat-label">{t("foodAnalyzer.calories")} (kcal)</span>
                </div>
                <div className="nutri-stat-box carbs">
                  <FaBreadSlice className="stat-icon" />
                  <span className="stat-value">{analysisResult.total_carbohydrates_g}g</span>
                  <span className="stat-label">{t("foodAnalyzer.totalCarbs")}</span>
                </div>
                <div className="nutri-stat-box protein">
                  <FaDrumstickBite className="stat-icon" />
                  <span className="stat-value">{analysisResult.total_protein_g}g</span>
                  <span className="stat-label">{t("foodAnalyzer.protein")}</span>
                </div>
                <div className="nutri-stat-box gi">
                  <FaChartPie className="stat-icon" />
                  <span className="stat-value">{analysisResult.average_glycemic_index}</span>
                  <span className="stat-label">{t("foodAnalyzer.glycemicIndex")} (GI)</span>
                </div>
              </div>

              {/* Additional Nutritional Details (Fats, Fiber, Net Carbs, Portion) */}
              <div className="secondary-metrics-row">
                <div className="sec-metric-item">
                  <span className="sec-label">{t("foodAnalyzer.netCarbs")}:</span>
                  <span className="sec-val">{analysisResult.total_net_carbs_g}g</span>
                </div>
                <div className="sec-metric-item">
                  <span className="sec-label">{t("foodAnalyzer.fiber")}:</span>
                  <span className="sec-val">{analysisResult.total_fiber_g}g</span>
                </div>
                <div className="sec-metric-item">
                  <span className="sec-label">{t("foodAnalyzer.healthyFats")}:</span>
                  <span className="sec-val">{analysisResult.total_fats_g}g</span>
                </div>
                <div className="sec-metric-item">
                  <span className="sec-label">{t("foodAnalyzer.portionSize")}:</span>
                  <span className="sec-val">{analysisResult.suggested_portion}</span>
                </div>
              </div>

              {/* Clinical AI Recommendation Box */}
              {analysisResult.clinical_recommendation && (
                <div className="clinical-recommendation-box">
                  <h4><FaLightbulb /> {t("foodAnalyzer.clinicalAdviceTitle")}</h4>
                  <p>{analysisResult.clinical_recommendation}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <Footer />
    </>
  );
}

export default FoodAnalyzer;
