import "./Assessment.css";
import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import {
  FaUser, FaStethoscope, FaRunning, FaCheckCircle,
  FaBrain, FaInfoCircle, FaCalculator, FaAppleAlt,
  FaMicrophone, FaMicrophoneSlash, FaFileUpload,
  FaFileAlt, FaTimesCircle, FaCheckDouble, FaVolumeUp,
  FaStopCircle, FaEdit, FaExclamationTriangle, FaRobot,
  FaKeyboard, FaCheck, FaTimes
} from "react-icons/fa";

import Navbar from "../../components/Navbar/Navbar";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import { predictionService, smartAssessmentService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";
import {
  isSpeechRecognitionSupported,
  isSpeechSynthesisSupported,
  startListening,
  stopListening,
  speak,
  stopSpeaking,
  interpretTranscript,
  validateField,
  getVoiceQuestion,
  FIELD_DEFINITIONS,
} from "./VoiceEngine";

// ─── Required fields for completeness check ───────────────────────────────────
const REQUIRED_FIELDS = ["age", "gender", "patientGroup", "height", "weight"];
const OPTIONAL_BUT_USEFUL = [
  "fastingGlucose", "hba1c", "bloodPressure", "familyHistory",
  "physicalActivityHours", "dailySugarIntake", "fastFoodFrequency", "sleepHours",
];

// Voice assessment ordered question list (maps to formData keys)
const VOICE_QUESTION_ORDER = [
  "age", "gender", "patientGroup", "height", "weight",
  "fastingGlucose", "hba1c", "bloodPressure", "familyHistory",
  "physicalActivityHours", "dailySugarIntake", "fastFoodFrequency",
  "sleepHours", "monthlyIncome",
];

// Mapping from backend extracted field names → formData keys
const BACKEND_TO_FORM = {
  full_name: "fullName",
  age: "age",
  gender: "gender",
  height: "height",
  weight: "weight",
  bmi: "bmi",
  fasting_glucose: "fastingGlucose",
  hba1c: "hba1c",
  blood_pressure: "bloodPressure",
  family_history: "familyHistory",
  physical_activity_hours: "physicalActivityHours",
  daily_sugar_intake: "dailySugarIntake",
  fast_food_frequency: "fastFoodFrequency",
  sleep_hours: "sleepHours",
  monthly_income: "monthlyIncome",
  patient_group: "patientGroup",
};

function Assessment() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { t, language } = useTranslation();

  const [formData, setFormData] = useState({
    fullName: "",
    age: "42",
    gender: "Male",
    patientGroup: "Urban",
    height: "170",
    weight: "75",
    bmi: "26.0",
    fastingGlucose: "",
    hba1c: "",
    bloodPressure: "",
    familyHistory: "0",
    physicalActivityHours: "3",
    dailySugarIntake: "50",
    fastFoodFrequency: "2",
    sleepHours: "7",
    monthlyIncome: "",
  });

  // Track data source: manual | voice | medical_report
  const [dataSources, setDataSources] = useState({});

  // ── Voice state ──────────────────────────────────────────────────────────
  const [voiceMode, setVoiceMode] = useState(false);         // full voice assessment mode
  const [isListening, setIsListening] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState("");        // status text shown to user
  const [voiceField, setVoiceField] = useState(null);        // which field mic is active for
  const [voiceQueueIdx, setVoiceQueueIdx] = useState(0);     // index in VOICE_QUESTION_ORDER
  const [voiceConfirmation, setVoiceConfirmation] = useState(null);
  // { field, heard, interpreted, displayValue }

  // ── Report upload state ──────────────────────────────────────────────────
  const [reportFile, setReportFile] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [extractedFields, setExtractedFields] = useState(null);   // raw backend result
  const [showExtracted, setShowExtracted] = useState(false);
  const [editableExtracted, setEditableExtracted] = useState({}); // user can edit before confirm
  const [conflicts, setConflicts] = useState([]);                  // { field, manualVal, reportVal }
  const [resolvingConflict, setResolvingConflict] = useState(null);

  // ── Missing data Q&A state ───────────────────────────────────────────────
  const [missingFields, setMissingFields] = useState([]);
  const [missingQA, setMissingQA] = useState(null); // current missing-field dialog
  const [missingTextInput, setMissingTextInput] = useState("");
  const [missingListening, setMissingListening] = useState(false);

  const fileInputRef = useRef(null);

  // ── Auto-calculate BMI ───────────────────────────────────────────────────
  useEffect(() => {
    const h = parseFloat(formData.height);
    const w = parseFloat(formData.weight);
    if (h > 0 && w > 0) {
      const calcBmi = (w / ((h / 100) ** 2)).toFixed(1);
      setFormData((prev) => ({ ...prev, bmi: calcBmi }));
    }
  }, [formData.height, formData.weight]);

  const handleChange = (field, value, source = "manual") => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setDataSources((prev) => ({ ...prev, [field]: source }));
  };

  // ─────────────────────────────────────────────────────────────────────────
  // EXISTING VALIDATION + SUBMISSION (unchanged)
  // ─────────────────────────────────────────────────────────────────────────
  const validateStep = (currentStep) => {
    if (currentStep === 1) {
      if (!formData.age || parseFloat(formData.age) < 1 || parseFloat(formData.age) > 110) {
        toast.error("Please enter a valid age (1–110).");
        return false;
      }
      if (!formData.height || parseFloat(formData.height) < 100) {
        toast.error("Please enter your height in cm (e.g. 165).");
        return false;
      }
      if (!formData.weight || parseFloat(formData.weight) < 20) {
        toast.error("Please enter your weight in kg.");
        return false;
      }
    }
    return true;
  };

  const handleNextStep = () => {
    if (validateStep(step)) {
      if (step === 3) handleAnalysis();
      else setStep((prev) => prev + 1);
    }
  };

  const handleAnalysis = async () => {
    setLoading(true);
    toast.info("🧠 Analysing your health information...");
    try {
      const payload = {
        patient_group:           formData.patientGroup || null,
        age:                     parseFloat(formData.age) || null,
        gender:                  formData.gender || null,
        bmi:                     parseFloat(formData.bmi) || null,
        blood_pressure:          formData.bloodPressure ? parseFloat(formData.bloodPressure) : null,
        physical_activity_hours: formData.physicalActivityHours ? parseFloat(formData.physicalActivityHours) : null,
        daily_sugar_intake:      formData.dailySugarIntake ? parseFloat(formData.dailySugarIntake) : null,
        fast_food_frequency:     formData.fastFoodFrequency ? parseFloat(formData.fastFoodFrequency) : null,
        sleep_hours:             formData.sleepHours ? parseFloat(formData.sleepHours) : null,
        hba1c:                   formData.hba1c ? parseFloat(formData.hba1c) : null,
        fasting_glucose:         formData.fastingGlucose ? parseFloat(formData.fastingGlucose) : null,
        family_history:          parseFloat(formData.familyHistory) || 0,
        monthly_income:          formData.monthlyIncome ? parseFloat(formData.monthlyIncome) : null,
        month:                   new Date().getMonth() + 1,
      };
      const response = await predictionService.createPrediction(payload);
      const resultData = response.data;
      localStorage.setItem("latest_prediction", JSON.stringify(resultData));
      toast.success("✅ Health assessment complete!");
      setTimeout(() => navigate("/result"), 800);
    } catch (err) {
      toast.error(err.message || "Failed to analyse health information. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // FEATURE 2 — VOICE INPUT / OUTPUT
  // ─────────────────────────────────────────────────────────────────────────
  const handleMicField = useCallback((field) => {
    if (!isSpeechRecognitionSupported()) {
      toast.warning("Voice input is not supported in this browser. Please type your answer.");
      return;
    }
    if (isListening) { stopListening(); setIsListening(false); setVoiceField(null); return; }

    setVoiceField(field);
    setIsListening(true);
    setVoiceStatus("Listening…");
    startListening({
      lang: language || "en",
      onStart: () => setVoiceStatus("Listening… speak now"),
      onResult: (transcript) => {
        setIsListening(false);
        setVoiceField(null);
        setVoiceStatus("");
        const interpreted = interpretTranscript(transcript, field);
        if (!interpreted) {
          toast.warning(`Couldn't understand "${transcript}". Please type the value manually.`);
          return;
        }
        const { valid, message } = validateField(field, interpreted.value);
        if (!valid) {
          toast.error(`${message} (heard: "${transcript}")`);
          return;
        }
        // Show confirmation for medical values
        setVoiceConfirmation({
          field, heard: transcript,
          interpreted: interpreted.interpreted,
          displayValue: interpreted.displayValue,
          value: interpreted.value,
        });
      },
      onError: (msg) => {
        setIsListening(false); setVoiceField(null); setVoiceStatus("");
        toast.error(msg);
      },
      onEnd: () => { setIsListening(false); setVoiceField(null); setVoiceStatus(""); },
    });
  }, [isListening, language]);

  const confirmVoiceValue = () => {
    if (!voiceConfirmation) return;
    handleChange(voiceConfirmation.field, voiceConfirmation.value, "voice");
    setVoiceConfirmation(null);
    toast.success(`✅ ${FIELD_DEFINITIONS[voiceConfirmation.field]?.label}: ${voiceConfirmation.displayValue}`);
  };

  const rejectVoiceValue = () => setVoiceConfirmation(null);

  // Full sequential voice assessment mode
  const startVoiceAssessment = useCallback(async () => {
    if (!isSpeechRecognitionSupported()) {
      toast.warning("Voice input is not supported in your browser. Please type your answers.");
      return;
    }
    setVoiceMode(true);
    setVoiceQueueIdx(0);
    await runVoiceQuestion(0);
  }, []);

  const runVoiceQuestion = async (idx) => {
    if (idx >= VOICE_QUESTION_ORDER.length) {
      setVoiceMode(false);
      toast.success("🎉 Voice assessment complete! Please review your answers below.");
      return;
    }
    const field = VOICE_QUESTION_ORDER[idx];
    const question = getVoiceQuestion(field, language || "en");
    setVoiceQueueIdx(idx);
    setVoiceStatus(`Asking: ${question}`);

    if (isSpeechSynthesisSupported()) {
      await speak(question, language || "en");
    }

    setIsListening(true);
    setVoiceField(field);
    setVoiceStatus("Listening…");

    startListening({
      lang: language || "en",
      onStart: () => setVoiceStatus("Listening… speak now"),
      onResult: (transcript) => {
        setIsListening(false);
        setVoiceField(null);
        setVoiceStatus(`Processing: "${transcript}"`);
        const interpreted = interpretTranscript(transcript, field);
        if (!interpreted) {
          setVoiceStatus(`Couldn't understand. Skipping to next question.`);
          setTimeout(() => runVoiceQuestion(idx + 1), 1500);
          return;
        }
        const { valid } = validateField(field, interpreted.value);
        if (valid) {
          handleChange(field, interpreted.value, "voice");
          setVoiceStatus(`✅ ${FIELD_DEFINITIONS[field]?.label}: ${interpreted.displayValue}`);
          setTimeout(() => runVoiceQuestion(idx + 1), 1500);
        } else {
          setVoiceStatus("Invalid value. Moving to next question.");
          setTimeout(() => runVoiceQuestion(idx + 1), 1500);
        }
      },
      onError: () => {
        setIsListening(false);
        setTimeout(() => runVoiceQuestion(idx + 1), 1000);
      },
      onEnd: () => { setIsListening(false); setVoiceField(null); },
    });
  };

  const stopVoiceAssessment = () => {
    stopListening();
    stopSpeaking();
    setVoiceMode(false);
    setIsListening(false);
    setVoiceField(null);
    setVoiceStatus("");
    toast.info("Voice assessment stopped. You can continue typing.");
  };

  // ─────────────────────────────────────────────────────────────────────────
  // FEATURE 3 — MEDICAL REPORT UPLOAD + EXTRACTION
  // ─────────────────────────────────────────────────────────────────────────
  const applyExtractedToForm = useCallback((extractedMap) => {
    setFormData((prev) => {
      const next = { ...prev };
      Object.entries(extractedMap).forEach(([field, info]) => {
        next[field] = String(info.value);
      });
      // Keep height/weight/bmi consistent when BMI is extracted from report
      if (extractedMap.bmi && !extractedMap.weight) {
        const h = parseFloat(next.height) || 170;
        const b = parseFloat(extractedMap.bmi.value);
        if (h > 0 && b > 0) {
          next.weight = String(Math.round(b * ((h / 100) ** 2)));
          next.bmi = b.toFixed(1);
        }
      }
      return next;
    });
    setDataSources((prev) => {
      const next = { ...prev };
      Object.keys(extractedMap).forEach((field) => {
        next[field] = "medical_report";
      });
      if (extractedMap.bmi && !extractedMap.weight) {
        next.weight = "medical_report";
      }
      return next;
    });
  }, []);

  const extractReportFile = async (fileToProcess) => {
    const f = fileToProcess || reportFile;
    if (!f) return;
    setReportLoading(true);
    setShowExtracted(false);
    try {
      const fd = new FormData();
      fd.append("file", f);
      const res = await smartAssessmentService.extractReport(fd);
      const data = res?.data || res;

      if (!data?.success || !data?.extracted_fields || Object.keys(data.extracted_fields).length === 0) {
        toast.warning(data?.message || "Could not extract information from this file. Please enter values manually.");
        setReportLoading(false);
        return;
      }

      // Map backend field names → formData keys, build editable copy
      const editable = {};
      Object.entries(data.extracted_fields).forEach(([backendKey, info]) => {
        const formKey = BACKEND_TO_FORM[backendKey];
        if (formKey) {
          editable[formKey] = {
            value: String(info.value),
            confidence: info.confidence,
            raw: info.raw,
          };
        }
      });

      setExtractedFields(editable);
      setEditableExtracted({ ...editable });
      setShowExtracted(true);

      // Immediately populate the assessment form with extracted values
      applyExtractedToForm(editable);
      toast.success(`📋 Extracted & applied ${Object.keys(editable).length} fields from your report!`);
    } catch (err) {
      toast.error(err?.message || "Could not process this file. Please try another PDF or image.");
    } finally {
      setReportLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const f = e.target.files?.[0];
    if (e.target) e.target.value = ""; // allow re-selecting the same file
    if (!f) return;
    const allowed = ["application/pdf", "image/jpeg", "image/jpg", "image/png"];
    const allowedExt = [".pdf", ".jpg", ".jpeg", ".png"];
    const ext = f.name.includes(".") ? f.name.slice(f.name.lastIndexOf(".")).toLowerCase() : "";
    if (!allowed.includes(f.type) && !allowedExt.includes(ext)) {
      toast.error("Please upload a PDF, JPG, or PNG file.");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      toast.error("File too large. Maximum 10 MB allowed.");
      return;
    }
    setReportFile(f);
    setExtractedFields(null);
    setShowExtracted(false);
    setConflicts([]);
    // Automatically start extraction as soon as file is uploaded
    extractReportFile(f);
  };

  const handleExtractReport = () => {
    extractReportFile(reportFile);
  };

  const handleConfirmExtracted = () => {
    // Check for conflicts with existing manual values
    const newConflicts = [];
    const toApply = {};

    Object.entries(editableExtracted).forEach(([field, info]) => {
      const existing = formData[field];
      const isFilledByUser = existing && dataSources[field] === "manual" && existing !== "";
      if (isFilledByUser && existing !== info.value && field !== "bmi") {
        newConflicts.push({ field, manualVal: existing, reportVal: info.value });
      } else {
        toApply[field] = info;
      }
    });

    // Apply non-conflicting values immediately
    applyExtractedToForm(toApply);
    setConflicts(newConflicts);

    if (newConflicts.length > 0) {
      setResolvingConflict(newConflicts[0]);
    } else {
      setShowExtracted(false);
      toast.success("✅ Report values confirmed and applied to your assessment.");
      detectMissingFields();
    }
  };

  const resolveConflict = (useReport) => {
    if (!resolvingConflict) return;
    if (useReport) {
      const info = editableExtracted[resolvingConflict.field];
      if (info) applyExtractedToForm({ [resolvingConflict.field]: info });
    }
    const remaining = conflicts.filter(c => c.field !== resolvingConflict.field);
    setConflicts(remaining);
    if (remaining.length > 0) {
      setResolvingConflict(remaining[0]);
    } else {
      setResolvingConflict(null);
      setShowExtracted(false);
      toast.success("✅ Report values applied.");
      detectMissingFields();
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // FEATURE 4 — MISSING DATA DETECTION + Q&A
  // ─────────────────────────────────────────────────────────────────────────
  const detectMissingFields = useCallback(() => {
    const missing = OPTIONAL_BUT_USEFUL.filter(f => {
      const val = formData[f];
      if (!val || val === "") return true;
      // family history has a default "0" which is valid
      return false;
    });
    setMissingFields(missing);
    if (missing.length > 0) {
      setTimeout(() => startMissingQA(missing, 0), 500);
    }
    return missing;
  }, [formData]);

  const startMissingQA = (fields, idx) => {
    if (idx >= fields.length) {
      setMissingQA(null);
      toast.success("✅ All information collected. You can now run the health screening.");
      return;
    }
    const field = fields[idx];
    const def = FIELD_DEFINITIONS[field];
    if (!def) { startMissingQA(fields, idx + 1); return; }
    setMissingQA({ field, def, fields, idx });
    setMissingTextInput("");
    if (isSpeechSynthesisSupported()) {
      speak(`I still need some information. ${def.question}`, language || "en");
    }
  };

  const submitMissingAnswer = (value) => {
    if (!missingQA) return;
    const { field, def, fields, idx } = missingQA;

    if (!value || value.trim() === "") {
      if (def.optional) { startMissingQA(fields, idx + 1); return; }
      toast.warning("Please provide a value or skip this field.");
      return;
    }

    const { valid, message } = validateField(field, value);
    if (!valid) {
      toast.error(message);
      return;
    }
    handleChange(field, value, "manual");
    toast.success(`✅ ${def.label} saved.`);
    startMissingQA(fields, idx + 1);
  };

  const skipMissingField = () => {
    if (!missingQA) return;
    startMissingQA(missingQA.fields, missingQA.idx + 1);
  };

  const handleMissingVoice = () => {
    if (!missingQA || !isSpeechRecognitionSupported()) {
      toast.warning("Voice input not available. Please type your answer.");
      return;
    }
    setMissingListening(true);
    startListening({
      lang: language || "en",
      onResult: (transcript) => {
        setMissingListening(false);
        const interpreted = interpretTranscript(transcript, missingQA.field);
        if (interpreted) {
          setMissingTextInput(interpreted.value);
        } else {
          // Try raw numeric extraction
          const numMatch = transcript.match(/(\d+(?:\.\d+)?)/);
          if (numMatch) setMissingTextInput(numMatch[1]);
          else toast.warning(`Couldn't understand "${transcript}". Please type the value.`);
        }
      },
      onError: (msg) => { setMissingListening(false); toast.error(msg); },
      onEnd: () => setMissingListening(false),
    });
  };

  // Source badge helper
  const sourceBadge = (field) => {
    const s = dataSources[field];
    if (!s) return null;
    const badges = {
      voice: { icon: "🎤", label: "Voice", cls: "src-voice" },
      medical_report: { icon: "📄", label: "Report", cls: "src-report" },
    };
    const b = badges[s];
    if (!b) return null;
    return <span className={`source-badge ${b.cls}`}>{b.icon} {b.label}</span>;
  };

  // Mic button helper
  const MicBtn = ({ field }) => (
    <button
      type="button"
      className={`mic-btn-inline ${isListening && voiceField === field ? "listening" : ""}`}
      onClick={() => handleMicField(field)}
      title={isListening && voiceField === field ? "Stop listening" : "Speak your answer"}
      aria-label={isListening && voiceField === field ? "Stop voice input" : "Start voice input"}
    >
      {isListening && voiceField === field ? <FaMicrophoneSlash /> : <FaMicrophone />}
    </button>
  );

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────────
  return (
    <>
      <Navbar />
      <div className="assessment-page">
        <div className="assessment-container">
          <BackButton />

          {/* Page Header */}
          <div className="assessment-header text-center">
            <span className="badge-pill">🩺 Health Risk Screening</span>
            <h1>{t("assessment.headerTitle") || "Health Risk Screening"}</h1>
            <p className="assessment-disclaimer">
              ⚕️ This is a <strong>health awareness screening</strong> tool — not a medical diagnosis.
              Results are model-estimated risk patterns. Always consult a healthcare professional.
            </p>
          </div>

          {/* ── SMART TOOLBAR (Features 2 & 3) ── */}
          <div className="smart-toolbar">
            {/* Voice Assessment Card */}
            <div className="smart-card voice-card">
              <div className="smart-card-icon">🎤</div>
              <div className="smart-card-body">
                <h3>Voice Assessment</h3>
                <p>Speak your answers instead of typing</p>
                {voiceMode ? (
                  <div className="voice-active-state">
                    <div className="voice-status-bar">
                      {isListening && <span className="pulse-dot" />}
                      <span>{voiceStatus || "Voice mode active"}</span>
                    </div>
                    <button className="smart-btn stop-btn" onClick={stopVoiceAssessment}>
                      <FaStopCircle /> Stop Voice Mode
                    </button>
                  </div>
                ) : (
                  <button
                    className="smart-btn primary"
                    onClick={startVoiceAssessment}
                    disabled={!isSpeechRecognitionSupported()}
                  >
                    <FaMicrophone />
                    {isSpeechRecognitionSupported() ? "Start Voice Assessment" : "Not Supported in Browser"}
                  </button>
                )}
              </div>
            </div>

            {/* Report Upload Card */}
            <div
              className="smart-card report-card"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                if (e.dataTransfer?.files?.[0]) {
                  handleFileSelect({ target: { files: e.dataTransfer.files } });
                }
              }}
            >
              <div className="smart-card-icon">📄</div>
              <div className="smart-card-body">
                <h3>Upload Medical Report</h3>
                <p>PDF, JPG, or PNG — AI automatically extracts & fills your health data</p>
                <div className="report-upload-row">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
                    onChange={handleFileSelect}
                    style={{ display: "none" }}
                    aria-label="Upload medical report"
                  />
                  <button
                    type="button"
                    className="smart-btn secondary"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={reportLoading}
                  >
                    <FaFileUpload /> {reportFile ? "Upload Another File" : "Choose File"}
                  </button>
                  {reportFile && (
                    <>
                      <span className="file-name-pill">
                        <FaFileAlt /> {reportFile.name.length > 20 ? reportFile.name.slice(0, 20) + "…" : reportFile.name}
                        <button
                          type="button"
                          onClick={() => { setReportFile(null); setExtractedFields(null); setShowExtracted(false); }}
                          aria-label="Remove file"
                        >
                          <FaTimesCircle />
                        </button>
                      </span>
                      <button
                        type="button"
                        className="smart-btn primary"
                        onClick={handleExtractReport}
                        disabled={reportLoading}
                      >
                        {reportLoading ? "Extracting…" : "Re-Extract Data"}
                      </button>
                    </>
                  )}
                </div>
                {reportLoading && (
                  <div className="extract-progress">
                    <span className="progress-dot" />
                    <span className="progress-dot" style={{ animationDelay: "0.2s" }} />
                    <span className="progress-dot" style={{ animationDelay: "0.4s" }} />
                    <span>Reading document & extracting health metrics…</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ── EXTRACTED VALUES PANEL ── */}
          {showExtracted && editableExtracted && Object.keys(editableExtracted).length > 0 && (
            <div className="extracted-panel">
              <div className="extracted-header">
                <h3><FaFileAlt /> Information Extracted from Your Report (Applied to Form)</h3>
                <p>These values have been automatically filled into your assessment. You can review or edit any value below.</p>
              </div>
              <div className="extracted-grid">
                {Object.entries(editableExtracted).map(([field, info]) => {
                  const def = FIELD_DEFINITIONS[field];
                  return (
                    <div key={field} className={`extracted-item conf-${(info.confidence || "HIGH").toLowerCase()}`}>
                      <div className="extracted-item-label">
                        <span>{def?.label || field}</span>
                        <span className={`conf-badge conf-${(info.confidence || "HIGH").toLowerCase()}`}>
                          {info.confidence === "HIGH" ? "✓ High confidence" : "⚠ Verify this value"}
                        </span>
                      </div>
                      <input
                        type={def?.type === "select" ? "text" : "text"}
                        value={info.value}
                        onChange={(e) => {
                          const newVal = e.target.value;
                          setEditableExtracted(prev => ({
                            ...prev,
                            [field]: { ...prev[field], value: newVal }
                          }));
                          handleChange(field, newVal, "medical_report");
                        }}
                        className="extracted-input"
                      />
                      {def?.unit && <span className="extracted-unit">{def.unit}</span>}
                    </div>
                  );
                })}
              </div>
              <div className="extracted-actions">
                <button type="button" className="smart-btn primary" onClick={handleConfirmExtracted}>
                  <FaCheckDouble /> Confirm & Check Missing Fields
                </button>
                <button className="smart-btn ghost" onClick={() => setShowExtracted(false)}>
                  Dismiss
                </button>
              </div>
            </div>
          )}

          {/* ── CONFLICT RESOLUTION DIALOG ── */}
          {resolvingConflict && (
            <div className="conflict-overlay">
              <div className="conflict-dialog">
                <FaExclamationTriangle className="conflict-icon" />
                <h3>Different Values Found</h3>
                <p>
                  You entered a different {FIELD_DEFINITIONS[resolvingConflict.field]?.label || resolvingConflict.field} than
                  what's in your report. Which value would you like to use?
                </p>
                <div className="conflict-values">
                  <div className="conflict-val">
                    <span className="cval-label">Your entered value</span>
                    <span className="cval-num">{resolvingConflict.manualVal}</span>
                  </div>
                  <div className="conflict-val">
                    <span className="cval-label">Report value</span>
                    <span className="cval-num">{resolvingConflict.reportVal}</span>
                  </div>
                </div>
                <div className="conflict-actions">
                  <button className="smart-btn secondary" onClick={() => resolveConflict(false)}>
                    Keep My Value ({resolvingConflict.manualVal})
                  </button>
                  <button className="smart-btn primary" onClick={() => resolveConflict(true)}>
                    Use Report Value ({resolvingConflict.reportVal})
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── VOICE CONFIRMATION DIALOG ── */}
          {voiceConfirmation && (
            <div className="voice-confirm-overlay">
              <div className="voice-confirm-dialog">
                <FaMicrophone className="vc-icon" />
                <p className="vc-heard">I heard: <em>"{voiceConfirmation.heard}"</em></p>
                <p className="vc-interpreted">
                  {FIELD_DEFINITIONS[voiceConfirmation.field]?.label}:{" "}
                  <strong>{voiceConfirmation.displayValue}</strong>
                </p>
                <p className="vc-question">Is that correct?</p>
                <div className="vc-actions">
                  <button className="smart-btn primary" onClick={confirmVoiceValue}>
                    <FaCheck /> Yes, that's correct
                  </button>
                  <button className="smart-btn ghost" onClick={rejectVoiceValue}>
                    <FaTimes /> Try again
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* ── MISSING DATA Q&A PANEL ── */}
          {missingQA && (
            <div className="missing-data-panel">
              <div className="missing-data-header">
                <FaRobot className="missing-icon" />
                <div>
                  <h3>I Need a Bit More Information</h3>
                  <p>
                    Field {missingQA.idx + 1} of {missingQA.fields.length} —{" "}
                    {missingQA.def.optional ? "optional" : "helps improve accuracy"}
                  </p>
                </div>
              </div>
              <p className="missing-question">{missingQA.def.question}</p>

              {/* Voice or Text answer */}
              <div className="missing-answer-row">
                {isSpeechRecognitionSupported() && (
                  <button
                    className={`smart-btn ${missingListening ? "stop-btn" : "voice-btn"}`}
                    onClick={handleMissingVoice}
                    disabled={missingListening}
                  >
                    {missingListening ? <><FaMicrophoneSlash /> Listening…</> : <><FaMicrophone /> Speak</>}
                  </button>
                )}
                <span className="or-divider">or</span>
                <div className="missing-input-row">
                  {missingQA.def.type === "select" ? (
                    <select
                      value={missingTextInput}
                      onChange={e => setMissingTextInput(e.target.value)}
                      className="missing-input"
                    >
                      <option value="">Select…</option>
                      {missingQA.def.options?.map(o => (
                        <option key={o} value={o}>{o}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="number"
                      className="missing-input"
                      placeholder={missingQA.def.placeholder}
                      value={missingTextInput}
                      onChange={e => setMissingTextInput(e.target.value)}
                      min={missingQA.def.min}
                      max={missingQA.def.max}
                      onKeyDown={e => e.key === "Enter" && submitMissingAnswer(missingTextInput)}
                    />
                  )}
                  <button className="smart-btn primary" onClick={() => submitMissingAnswer(missingTextInput)}>
                    Continue →
                  </button>
                  <button className="smart-btn ghost" onClick={skipMissingField}>
                    Skip
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Stepper Progress */}
          <div className="stepper-bar">
            {["Personal & Physical", "Clinical Values", "Lifestyle Habits"].map((label, idx) => (
              <div key={idx} className={`step-item ${step > idx + 1 ? "completed" : ""} ${step === idx + 1 ? "active" : ""}`}>
                <div className="step-circle">{step > idx + 1 ? <FaCheckCircle /> : idx + 1}</div>
                <span>{label}</span>
              </div>
            ))}
          </div>

          {/* Form Card */}
          <div className="assessment-card">

            {/* ── STEP 1: Personal & Physical ── */}
            {step === 1 && (
              <div className="form-step-content">
                <h2><FaUser /> Personal & Physical Information</h2>
                <p className="step-subtitle">Your basic health profile helps calibrate the screening model.</p>

                <div className="input-grid">
                  <div className="input-group">
                    <label>Full Name {sourceBadge("fullName")}</label>
                    <input type="text" placeholder="e.g. Priya Sharma"
                      value={formData.fullName}
                      onChange={(e) => handleChange("fullName", e.target.value)} />
                  </div>

                  <div className="input-group">
                    <label>Age (years) * {sourceBadge("age")}</label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 42" min="1" max="110"
                        value={formData.age}
                        onChange={(e) => handleChange("age", e.target.value)} />
                      <MicBtn field="age" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>Gender {sourceBadge("gender")}</label>
                    <select value={formData.gender} onChange={(e) => handleChange("gender", e.target.value)}>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                    </select>
                  </div>

                  <div className="input-group">
                    <label>Location Type {sourceBadge("patientGroup")}</label>
                    <select value={formData.patientGroup} onChange={(e) => handleChange("patientGroup", e.target.value)}>
                      <option value="Urban">Urban</option>
                      <option value="Semi-Urban">Semi-Urban</option>
                      <option value="Rural">Rural</option>
                    </select>
                  </div>

                  <div className="input-group">
                    <label>Height (cm) * {sourceBadge("height")}</label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 165" min="100" max="230"
                        value={formData.height}
                        onChange={(e) => handleChange("height", e.target.value)} />
                      <MicBtn field="height" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>Weight (kg) * {sourceBadge("weight")}</label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 72" min="20" max="250"
                        value={formData.weight}
                        onChange={(e) => handleChange("weight", e.target.value)} />
                      <MicBtn field="weight" />
                    </div>
                  </div>

                  <div className="input-group bmi-auto-group">
                    <label><FaCalculator /> BMI (auto-calculated)</label>
                    <div className="bmi-display">
                      <span>{formData.bmi || "–"}</span> kg/m²
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── STEP 2: Clinical / Lab Values ── */}
            {step === 2 && (
              <div className="form-step-content">
                <h2><FaStethoscope /> Clinical & Lab Values</h2>
                <p className="step-subtitle">
                  Enter your blood test results if available. All fields are optional — the model
                  will estimate missing values from population data.
                </p>

                <div className="input-grid">
                  <div className="input-group">
                    <label>
                      Fasting Blood Glucose (mg/dL) {sourceBadge("fastingGlucose")}
                      <span className="tooltip-badge" title="Normal: < 100 mg/dL | Pre-diabetic: 100-125 | High: ≥ 126">
                        <FaInfoCircle /> 70–125
                      </span>
                    </label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 108 (leave blank if unknown)"
                        value={formData.fastingGlucose}
                        onChange={(e) => handleChange("fastingGlucose", e.target.value)} />
                      <MicBtn field="fastingGlucose" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>
                      HbA1c (%) {sourceBadge("hba1c")}
                      <span className="tooltip-badge" title="Normal: < 5.7% | Pre-diabetic: 5.7-6.4% | High: ≥ 6.5%">
                        <FaInfoCircle /> 4–6.4 normal
                      </span>
                    </label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 5.8 (leave blank if unknown)" step="0.1"
                        value={formData.hba1c}
                        onChange={(e) => handleChange("hba1c", e.target.value)} />
                      <MicBtn field="hba1c" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>
                      Blood Pressure (mmHg) {sourceBadge("bloodPressure")}
                      <span className="tooltip-badge" title="Systolic blood pressure. Normal: < 120 mmHg">
                        <FaInfoCircle /> systolic
                      </span>
                    </label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 125 (leave blank if unknown)"
                        value={formData.bloodPressure}
                        onChange={(e) => handleChange("bloodPressure", e.target.value)} />
                      <MicBtn field="bloodPressure" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>Family History of Diabetes {sourceBadge("familyHistory")}</label>
                    <select value={formData.familyHistory} onChange={(e) => handleChange("familyHistory", e.target.value)}>
                      <option value="0">No — No family history</option>
                      <option value="1">Yes — Parent/sibling has diabetes</option>
                    </select>
                  </div>

                  <div className="input-group">
                    <label>Monthly Household Income (₹) {sourceBadge("monthlyIncome")}</label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 35000 (optional)"
                        value={formData.monthlyIncome}
                        onChange={(e) => handleChange("monthlyIncome", e.target.value)} />
                      <MicBtn field="monthlyIncome" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── STEP 3: Lifestyle Habits ── */}
            {step === 3 && (
              <div className="form-step-content">
                <h2><FaRunning /> Lifestyle & Daily Habits</h2>
                <p className="step-subtitle">
                  Lifestyle factors are major predictors in this model. Be honest for the most accurate screening.
                </p>

                <div className="input-grid">
                  <div className="input-group">
                    <label>
                      Physical Activity (hours/day) {sourceBadge("physicalActivityHours")}
                      <span className="tooltip-badge" title="WHO recommends ≥ 150 min/week of moderate activity">
                        <FaInfoCircle /> WHO: 2.1+ hrs
                      </span>
                    </label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 3.5" step="0.5" min="0" max="20"
                        value={formData.physicalActivityHours}
                        onChange={(e) => handleChange("physicalActivityHours", e.target.value)} />
                      <MicBtn field="physicalActivityHours" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>
                      Daily Sugar Intake (grams) {sourceBadge("dailySugarIntake")}
                      <span className="tooltip-badge" title="WHO recommends < 25-50g/day">
                        <FaInfoCircle /> WHO: &lt;50g
                      </span>
                    </label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 55" min="0" max="200"
                        value={formData.dailySugarIntake}
                        onChange={(e) => handleChange("dailySugarIntake", e.target.value)} />
                      <MicBtn field="dailySugarIntake" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>
                      <FaAppleAlt /> Fast Food / Junk Food (meals/week) {sourceBadge("fastFoodFrequency")}
                      <span className="tooltip-badge" title="Number of fast food or processed food meals per week">
                        <FaInfoCircle /> meals/week
                      </span>
                    </label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 2" min="0" max="21"
                        value={formData.fastFoodFrequency}
                        onChange={(e) => handleChange("fastFoodFrequency", e.target.value)} />
                      <MicBtn field="fastFoodFrequency" />
                    </div>
                  </div>

                  <div className="input-group">
                    <label>Sleep (hours/night) {sourceBadge("sleepHours")}</label>
                    <div className="input-mic-row">
                      <input type="number" placeholder="e.g. 7" step="0.5" min="2" max="14"
                        value={formData.sleepHours}
                        onChange={(e) => handleChange("sleepHours", e.target.value)} />
                      <MicBtn field="sleepHours" />
                    </div>
                  </div>
                </div>

                {/* Missing Data Detection trigger */}
                <div className="missing-check-banner">
                  <FaRobot />
                  <div>
                    <strong>AI Missing Data Check</strong>
                    <p>Click below to let AI detect and ask for any missing information before running the screening.</p>
                  </div>
                  <button className="smart-btn secondary small" onClick={detectMissingFields}>
                    Check Missing Data
                  </button>
                </div>

                {/* Summary Preview */}
                <div className="summary-preview">
                  <h4>📋 Your Summary</h4>
                  <div className="summary-chips">
                    <span>Age: {formData.age} yrs</span>
                    <span>BMI: {formData.bmi}</span>
                    <span>Activity: {formData.physicalActivityHours} hrs/day</span>
                    <span>Sugar: {formData.dailySugarIntake}g/day</span>
                    <span>Sleep: {formData.sleepHours} hrs</span>
                    {formData.familyHistory === "1" && <span className="risk-chip">Family History ⚠️</span>}
                    {formData.fastingGlucose && <span>Glucose: {formData.fastingGlucose} mg/dL</span>}
                    {formData.hba1c && <span>HbA1c: {formData.hba1c}%</span>}
                    {Object.values(dataSources).includes("voice") && <span className="src-chip-voice">🎤 Voice used</span>}
                    {Object.values(dataSources).includes("medical_report") && <span className="src-chip-report">📄 Report used</span>}
                  </div>
                </div>
              </div>
            )}

            {/* Stepper Navigation Buttons */}
            <div className="stepper-actions">
              {step > 1 && (
                <button className="btn-step secondary" onClick={() => setStep(step - 1)}>
                  ← Previous
                </button>
              )}
              {step < 3 && (
                <button className="btn-step primary" onClick={handleNextStep}>
                  Next →
                </button>
              )}
              {step === 3 && (
                <button className="btn-step primary predict-btn" onClick={handleNextStep} disabled={loading}>
                  <FaBrain /> {loading ? "Analysing..." : "Run Health Screening →"}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="ai-loading-overlay">
          <div className="loading-card">
            <FaBrain className="spinner-brain" />
            <h3>Analysing your health profile...</h3>
            <p>Running India Diabetes Risk Model v2</p>
            <small>⚕️ This is a screening tool, not a diagnosis.</small>
          </div>
        </div>
      )}

      <Footer />
    </>
  );
}

export default Assessment;