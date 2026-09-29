import "./DietPlan.css";
import { useState, useEffect } from "react";
import { toast } from "react-toastify";
import Navbar from "../../components/Navbar/Navbar";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import { Link } from "react-router-dom";
import { FaUtensils, FaCheckCircle, FaRunning, FaLeaf, FaDrumstickBite, FaBullseye, FaTint, FaWalking, FaAppleAlt, FaHeartbeat, FaBrain, FaExclamationTriangle, FaFire, FaTrophy, FaArrowRight, FaLock, FaClipboardList, FaSpinner } from "react-icons/fa";
import { dietService, predictionService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";
import { getLocalizedWeeklyDietPlan } from "../../utils/dietSchedules";

function DietPlan() {
  const { t, currentLanguage } = useTranslation();
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const dayNames = {
    Monday: t("dietPlan.monday"),
    Tuesday: t("dietPlan.tuesday"),
    Wednesday: t("dietPlan.wednesday"),
    Thursday: t("dietPlan.thursday"),
    Friday: t("dietPlan.friday"),
    Saturday: t("dietPlan.saturday"),
    Sunday: t("dietPlan.sunday"),
  };
  const [activeDay, setActiveDay] = useState("Monday");
  const [dietType, setDietType] = useState("Vegetarian");
  const [loading, setLoading] = useState(true);
  const [hasAssessment, setHasAssessment] = useState(false);
  const [patientStatus, setPatientStatus] = useState(null);

  const todayKey = new Date().toISOString().split("T")[0];

  // Get current logged-in user ID to isolate streak per user
  const getUserId = () => {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      return user.id || user.email || "guest";
    } catch {
      return "guest";
    }
  };
  const userId = getUserId();

  // User-specific localStorage keys
  const streakKey  = `diasense_health_streak_${userId}`;
  const claimedKey = `diasense_streak_claimed_${userId}_${todayKey}`;
  const goalsKey   = `diasense_goals_${userId}_${todayKey}`;

  // Persistent Streak Counter State — user-specific (starts at 0 for new users)
  const [streakCount, setStreakCount] = useState(() => {
    const savedStreak = localStorage.getItem(streakKey);
    return savedStreak ? parseInt(savedStreak, 10) : 0;
  });

  // Has streak/tasks already been completed and claimed today? — user-specific
  const [streakClaimed, setStreakClaimed] = useState(() => {
    return localStorage.getItem(claimedKey) === "true";
  });

  // Persistent Goal State for Today — user-specific
  const [dailyGoals, setDailyGoals] = useState(() => {
    const isClaimedToday = localStorage.getItem(claimedKey) === "true";
    if (isClaimedToday) {
      return { water: true, steps: true, fiber: true, glucose: true };
    }
    const saved = localStorage.getItem(goalsKey);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return { water: false, steps: false, fiber: false, glucose: false };
  });

  // Save Goals to localStorage whenever updated
  useEffect(() => {
    if (!streakClaimed) {
      localStorage.setItem(goalsKey, JSON.stringify(dailyGoals));
    }
  }, [dailyGoals, goalsKey, streakClaimed]);

  useEffect(() => {
    let found = false;

    // 1. Read stored prediction from localStorage
    const stored = localStorage.getItem("latest_prediction");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed && (parsed.prediction || parsed.risk_percentage !== undefined)) {
          setPatientStatus({
            prediction: parsed.prediction || (parsed.risk_percentage >= 50 ? "Diabetic" : "Non-Diabetic"),
            risk_percentage: parsed.risk_percentage ?? 5.5,
            glucose: parsed.glucose ?? parsed.raw_inputs?.glucose ?? 110,
            bmi: parsed.bmi ?? parsed.raw_inputs?.bmi ?? 23.5,
          });
          setHasAssessment(true);
          found = true;
        }
      } catch (e) {}
    }

    // 2. Fetch latest prediction from API
    predictionService
      .getLatest()
      .then((res) => {
        const data = res?.data || res;
        if (data && (data.prediction || data.risk_percentage !== undefined)) {
          setPatientStatus({
            prediction: data.prediction,
            risk_percentage: data.risk_percentage,
            glucose: data.glucose || data.raw_inputs?.glucose || 110,
            bmi: data.bmi || data.raw_inputs?.bmi || 23.5,
          });
          setHasAssessment(true);
        } else if (!found) {
          setHasAssessment(false);
        }
      })
      .catch(() => {
        if (!found) {
          setHasAssessment(false);
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const toggleGoal = (key) => {
    if (streakClaimed) {
      toast.info(t("dietPlan.taskAlreadyCompletedToast"));
      return;
    }
    setDailyGoals((prev) => {
      const updated = { ...prev, [key]: !prev[key] };
      return updated;
    });
  };

  const completedGoalsCount = streakClaimed ? 4 : Object.values(dailyGoals).filter(Boolean).length;
  const goalProgressPercentage = (completedGoalsCount / 4) * 100;
  const isAllGoalsCompleted = completedGoalsCount === 4;

  const handleClaimStreakAndNextDay = () => {
    if (streakClaimed) {
      toast.info(t("dietPlan.streakAlreadyClaimedToast"));
      return;
    }

    const newStreak = streakCount + 1;
    setStreakCount(newStreak);
    localStorage.setItem(streakKey, newStreak.toString());

    setStreakClaimed(true);
    localStorage.setItem(claimedKey, "true");

    // Lock all goals as completed for today
    const completedAll = { water: true, steps: true, fiber: true, glucose: true };
    setDailyGoals(completedAll);
    localStorage.setItem(goalsKey, JSON.stringify(completedAll));

    toast.success(`🔥 ${t("dietPlan.streakUpgradedToast", { count: newStreak })}`);
  };

  const isHighRisk = patientStatus?.prediction === "Diabetic" || (patientStatus?.risk_percentage >= 50.0);
  const isModerateRisk = !isHighRisk && (patientStatus?.risk_percentage >= 25.0);

  // Dynamically build 100% localized 7-day meal plan based on current language
  const activePlanDataset = getLocalizedWeeklyDietPlan(currentLanguage, dietType, isHighRisk);
  const currentPlan = activePlanDataset[activeDay] || activePlanDataset["Monday"];

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="diet-page">
          <div className="diet-loading-container">
            <FaSpinner className="diet-spinner" />
            <p>{t("dietPlan.loading")}</p>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  // If user has NOT completed an assessment, display prominent call-to-action
  if (!hasAssessment || !patientStatus) {
    return (
      <>
        <Navbar />
        <div className="diet-page">
          <div className="diet-container">
            <BackButton />

            <div className="diet-empty-state-card text-center">
              <div className="diet-empty-icon-wrap">
                <FaClipboardList />
              </div>
              <h1>{t("dietPlan.noAssessmentTitle")}</h1>
              <p className="diet-empty-desc">
                {t("dietPlan.noAssessmentDesc")}
              </p>
              <p className="diet-empty-subtext">
                {t("dietPlan.noAssessmentSubtext")}
              </p>

              <Link to="/assessment" className="start-assessment-cta-btn">
                <span>{t("dietPlan.startAssessmentBtn")}</span>
                <FaArrowRight />
              </Link>

              <div className="diet-preview-features-grid">
                <div className="preview-pill-card">
                  <FaCheckCircle className="pill-check" />
                  <div>
                    <h4>{t("dietPlan.featureGiTitle")}</h4>
                    <p>{t("dietPlan.featureGiDesc")}</p>
                  </div>
                </div>
                <div className="preview-pill-card">
                  <FaCheckCircle className="pill-check" />
                  <div>
                    <h4>{t("dietPlan.featureMacroTitle")}</h4>
                    <p>{t("dietPlan.featureMacroDesc")}</p>
                  </div>
                </div>
                <div className="preview-pill-card">
                  <FaCheckCircle className="pill-check" />
                  <div>
                    <h4>{t("dietPlan.featureStreakTitle")}</h4>
                    <p>{t("dietPlan.featureStreakDesc")}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navbar />

      <div className="diet-page">
        <div className="diet-container">
          <BackButton />

          {/* Page Header */}
          <div className="diet-header text-center">
            <div className="header-top-badges">
              <span className="badge-pill"><FaUtensils /> {t("dietPlan.headerBadge")}</span>
              <span className="fire-streak-badge"><FaFire /> 🔥 {streakCount} {t("dietPlan.streakDays")}</span>
            </div>

            <h1>{t("dietPlan.headerTitle")}</h1>
            <p>{t("dietPlan.headerDesc")}</p>

            {/* Assessment-Driven Status Banner */}
            <div className={`diet-patient-status-banner ${isHighRisk ? "high-risk" : isModerateRisk ? "mod-risk" : "low-risk"}`}>
              <div className="status-banner-left">
                {isHighRisk ? <FaExclamationTriangle /> : isModerateRisk ? <FaBrain /> : <FaCheckCircle />}
                <div>
                  <h3>
                    {t("dietPlan.assessmentProfile")} {patientStatus.prediction === "Diabetic" ? t("result.diabetic") : t("result.nonDiabetic")} ({patientStatus.risk_percentage}% {t("dashboard.probability")})
                  </h3>
                  <p>
                    {isHighRisk
                      ? t("dietPlan.strictLowGiDesc")
                      : isModerateRisk
                      ? t("dietPlan.prevGlycemicDesc")
                      : t("dietPlan.optMetabolicDesc")}
                  </p>
                </div>
              </div>
              <div className="status-badge">
                {t("dietPlan.glucoseLabel")} {patientStatus.glucose} mg/dL | {t("dietPlan.bmiLabel")} {patientStatus.bmi}
              </div>
            </div>
          </div>

          {/* Daily Health Goals Widget */}
          <div className="daily-goals-card">
            <div className="goals-header">
              <div>
                <h2><FaBullseye /> {t("dietPlan.streakTitle")}</h2>
                <p>{t("dietPlan.headerDesc")}</p>
              </div>
              <div className="goal-progress-badge">
                {completedGoalsCount} of 4 {t("dietPlan.completed")} ({goalProgressPercentage}%)
              </div>
            </div>

            <div className="goals-progress-bar">
              <div
                className="goals-progress-fill"
                style={{
                  width: `${goalProgressPercentage}%`,
                  background: isAllGoalsCompleted ? "linear-gradient(90deg, #10b981 0%, #059669 100%)" : "linear-gradient(90deg, #0ea5e9 0%, #10b981 100%)"
                }}
              />
            </div>

            {/* 1. Already Claimed For Today */}
            {streakClaimed ? (
              <div className="goals-complete-congratulations claimed-today">
                <div className="congratulations-left">
                  <FaCheckCircle className="trophy-icon claimed-icon" />
                  <div>
                    <h3>✅ {t("dietPlan.streakClaimed")}</h3>
                    <p>{t("dietPlan.streakClaimedDesc")}</p>
                  </div>
                </div>
                <div className="streak-locked-pill">
                  <FaFire /> 🔥 {t("dietPlan.streakClaimedPill", { count: streakCount })}
                </div>
              </div>
            ) : isAllGoalsCompleted ? (
              /* 2. All 4 Goals Just Checked */
              <div className="goals-complete-congratulations">
                <div className="congratulations-left">
                  <FaTrophy className="trophy-icon" />
                  <div>
                    <h3>🎉 {t("dietPlan.streakActive")}</h3>
                    <p>{t("dietPlan.streakDesc")}</p>
                  </div>
                </div>
                <button className="claim-streak-btn" onClick={handleClaimStreakAndNextDay}>
                  <FaFire /> 🔥 {t("dietPlan.claimStreakBtn")} ({streakCount + 1} {t("dietPlan.streakDays")}) <FaArrowRight />
                </button>
              </div>
            ) : null}

            <div className="goals-grid">
              <div
                className={`goal-item-card ${dailyGoals.water ? "completed" : ""} ${streakClaimed ? "locked" : ""}`}
                onClick={() => toggleGoal("water")}
              >
                <div className="goal-icon cyan"><FaTint /></div>
                <div className="goal-info">
                  <h4>{t("dietPlan.habitWater")}</h4>
                  <p>{t("dietPlan.habitWaterDesc")}</p>
                </div>
                <div className="checkbox">{dailyGoals.water ? "✓" : ""}</div>
              </div>

              <div
                className={`goal-item-card ${dailyGoals.steps ? "completed" : ""} ${streakClaimed ? "locked" : ""}`}
                onClick={() => toggleGoal("steps")}
              >
                <div className="goal-icon emerald"><FaWalking /></div>
                <div className="goal-info">
                  <h4>{t("dietPlan.habitSteps")}</h4>
                  <p>{t("dietPlan.habitStepsDesc")}</p>
                </div>
                <div className="checkbox">{dailyGoals.steps ? "✓" : ""}</div>
              </div>

              <div
                className={`goal-item-card ${dailyGoals.fiber ? "completed" : ""} ${streakClaimed ? "locked" : ""}`}
                onClick={() => toggleGoal("fiber")}
              >
                <div className="goal-icon amber"><FaAppleAlt /></div>
                <div className="goal-info">
                  <h4>{t("dietPlan.habitFiber")}</h4>
                  <p>{t("dietPlan.habitFiberDesc")}</p>
                </div>
                <div className="checkbox">{dailyGoals.fiber ? "✓" : ""}</div>
              </div>

              <div
                className={`goal-item-card ${dailyGoals.glucose ? "completed" : ""} ${streakClaimed ? "locked" : ""}`}
                onClick={() => toggleGoal("glucose")}
              >
                <div className="goal-icon indigo"><FaHeartbeat /></div>
                <div className="goal-info">
                  <h4>{t("dietPlan.habitGlucose")}</h4>
                  <p>{t("dietPlan.habitGlucoseDesc")}</p>
                </div>
                <div className="checkbox">{dailyGoals.glucose ? "✓" : ""}</div>
              </div>
            </div>
          </div>

          {/* Controls: Diet Type & Day Selector */}
          <div className="diet-controls">
            <div className="diet-type-toggle">
              <button
                className={`type-btn ${dietType === "Vegetarian" ? "active" : ""}`}
                onClick={() => setDietType("Vegetarian")}
              >
                <FaLeaf /> {t("dietPlan.veg")}
              </button>
              <button
                className={`type-btn ${dietType === "Non-Vegetarian" ? "active" : ""}`}
                onClick={() => setDietType("Non-Vegetarian")}
              >
                <FaDrumstickBite /> {t("dietPlan.nonVeg")}
              </button>
            </div>

            <div className="days-tabs">
              {days.map((day) => (
                <button
                  key={day}
                  className={`day-tab ${activeDay === day ? "active" : ""}`}
                  onClick={() => setActiveDay(day)}
                >
                  {dayNames[day] || day}
                </button>
              ))}
            </div>
          </div>

          {/* Active Day Meal Cards */}
          <div className="meals-container">
            <h2 className="day-title">{dayNames[activeDay] || activeDay} - {t("dietPlan.planSubtitle")} ({dietType === "Vegetarian" ? t("dietPlan.veg") : t("dietPlan.nonVeg")})</h2>

            <div className="meals-grid">
              <div className="meal-card">
                <div className="meal-header">
                  <span className="meal-time-icon">🌅</span>
                  <h3>{t("dietPlan.breakfast")}</h3>
                </div>
                <p className="meal-text">{currentPlan.breakfast}</p>
                <span className="meal-cal-badge">{currentPlan.breakfastCal}</span>
              </div>

              <div className="meal-card">
                <div className="meal-header">
                  <span className="meal-time-icon">☀️</span>
                  <h3>{t("dietPlan.lunch")}</h3>
                </div>
                <p className="meal-text">{currentPlan.lunch}</p>
                <span className="meal-cal-badge">{currentPlan.lunchCal}</span>
              </div>

              <div className="meal-card">
                <div className="meal-header">
                  <span className="meal-time-icon">🌙</span>
                  <h3>{t("dietPlan.dinner")}</h3>
                </div>
                <p className="meal-text">{currentPlan.dinner}</p>
                <span className="meal-cal-badge">{currentPlan.dinnerCal}</span>
              </div>
            </div>
          </div>

          {/* Exercise & Clinical Guidelines Section */}
          <div className="diet-extra-grid">
            <div className="extra-card">
              <h2><FaRunning /> {t("dietPlan.exerciseRoutine")}</h2>
              <ul>
                <li><FaCheckCircle /> {t("dietPlan.exerciseItem1")}</li>
                <li><FaCheckCircle /> {t("dietPlan.exerciseItem2")}</li>
                <li><FaCheckCircle /> {t("dietPlan.exerciseItem3")}</li>
              </ul>
            </div>

            <div className="extra-card highlight">
              <h2>💙 {t("dietPlan.principlesTitle")}</h2>
              <ul>
                <li><FaCheckCircle /> {t("dietPlan.principleItem1")}</li>
                <li><FaCheckCircle /> {t("dietPlan.principleItem2")}</li>
                <li><FaCheckCircle /> {t("dietPlan.principleItem3")}</li>
                <li><FaCheckCircle /> {t("dietPlan.principleItem4")}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}

export default DietPlan;