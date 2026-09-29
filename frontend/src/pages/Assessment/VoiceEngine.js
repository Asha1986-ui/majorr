/**
 * VoiceEngine.js — DiaSense AI Smart Assessment
 * Wraps Web Speech API (SpeechRecognition + SpeechSynthesis)
 * Provides field interpretation and validation helpers.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Browser capability detection
// ─────────────────────────────────────────────────────────────────────────────
export function isSpeechRecognitionSupported() {
  return !!(
    window.SpeechRecognition ||
    window.webkitSpeechRecognition ||
    window.mozSpeechRecognition ||
    window.msSpeechRecognition
  );
}

export function isSpeechSynthesisSupported() {
  return !!window.speechSynthesis;
}

// ─────────────────────────────────────────────────────────────────────────────
// TEXT-TO-SPEECH (Voice Output)
// ─────────────────────────────────────────────────────────────────────────────
let _currentUtterance = null;

export function speak(text, langCode = "en") {
  if (!isSpeechSynthesisSupported()) return Promise.resolve();
  return new Promise((resolve) => {
    window.speechSynthesis.cancel(); // Cancel any previous
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = _voiceLang(langCode);
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.onend = resolve;
    utterance.onerror = resolve; // Never reject — degrade gracefully
    _currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  });
}

export function stopSpeaking() {
  if (isSpeechSynthesisSupported()) {
    window.speechSynthesis.cancel();
  }
}

function _voiceLang(code) {
  const map = {
    en: "en-IN", kn: "kn-IN", hi: "hi-IN",
    ta: "ta-IN", te: "te-IN", ml: "ml-IN",
  };
  return map[code] || "en-IN";
}

// ─────────────────────────────────────────────────────────────────────────────
// SPEECH RECOGNITION (Voice Input)
// ─────────────────────────────────────────────────────────────────────────────
let _recognizer = null;

/**
 * Start listening.
 * @param {object} opts
 * @param {string} opts.lang - Language code (e.g. "en", "hi")
 * @param {(transcript: string) => void} opts.onResult
 * @param {(err: string) => void} opts.onError
 * @param {() => void} [opts.onStart]
 * @param {() => void} [opts.onEnd]
 */
export function startListening({ lang = "en", onResult, onError, onStart, onEnd }) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    onError?.("Voice input is not supported in your browser. Please type your answers instead.");
    return;
  }

  stopListening(); // stop any prior session

  _recognizer = new SR();
  _recognizer.lang = _voiceLang(lang);
  _recognizer.continuous = false;
  _recognizer.interimResults = false;
  _recognizer.maxAlternatives = 1;

  _recognizer.onstart = () => onStart?.();
  _recognizer.onend   = () => onEnd?.();

  _recognizer.onresult = (event) => {
    const transcript = event.results[0][0].transcript.trim();
    onResult?.(transcript);
  };

  _recognizer.onerror = (event) => {
    const errorMap = {
      "not-allowed": "Microphone permission was denied. Please allow microphone access and try again.",
      "no-speech":   "No speech detected. Please try speaking clearly.",
      "network":     "Network error during voice recognition. Please check your connection.",
      "language-not-supported": "Voice input is not available for this language in your browser.",
    };
    onError?.(errorMap[event.error] || `Voice error: ${event.error}. Please try again.`);
  };

  try {
    _recognizer.start();
  } catch (e) {
    onError?.("Could not start microphone. Please ensure microphone permission is granted.");
  }
}

export function stopListening() {
  if (_recognizer) {
    try { _recognizer.stop(); } catch (_) {}
    _recognizer = null;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// FIELD INTERPRETATION
// Converts free-form speech transcript → structured field value
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Field definitions — used by the missing-data engine.
 */
export const FIELD_DEFINITIONS = {
  fullName: {
    label: "Full Name",
    question: "What is your full name?",
    type: "text",
    placeholder: "e.g. Priya Sharma",
  },
  age: {
    label: "Age",
    question: "What is your age?",
    type: "number",
    unit: "years",
    min: 1, max: 110,
    placeholder: "e.g. 42",
    invalidMsg: "Please enter a valid age between 1 and 110.",
  },
  gender: {
    label: "Gender",
    question: "What is your gender? Male or Female?",
    type: "select",
    options: ["Male", "Female"],
    placeholder: "Male or Female",
  },
  patientGroup: {
    label: "Location Type",
    question: "Do you live in an Urban, Rural, or Semi-Urban area?",
    type: "select",
    options: ["Urban", "Rural", "Semi-Urban"],
    placeholder: "Urban / Rural / Semi-Urban",
  },
  height: {
    label: "Height",
    question: "What is your height in centimeters?",
    type: "number",
    unit: "cm",
    min: 100, max: 230,
    placeholder: "e.g. 165",
    invalidMsg: "Height should be between 100 and 230 cm.",
  },
  weight: {
    label: "Weight",
    question: "What is your weight in kilograms?",
    type: "number",
    unit: "kg",
    min: 20, max: 250,
    placeholder: "e.g. 70",
    invalidMsg: "Weight should be between 20 and 250 kg.",
  },
  bmi: {
    label: "BMI",
    question: "What is your BMI?",
    type: "number",
    unit: "kg/m²",
    min: 10, max: 70,
    placeholder: "e.g. 24.5",
    invalidMsg: "BMI should be between 10 and 70.",
  },
  fastingGlucose: {
    label: "Fasting Blood Glucose",
    question: "What is your fasting blood glucose level in mg/dL?",
    type: "number",
    unit: "mg/dL",
    min: 50, max: 450,
    placeholder: "e.g. 108",
    invalidMsg: "Fasting glucose should be between 50 and 450 mg/dL.",
  },
  hba1c: {
    label: "HbA1c",
    question: "What is your HbA1c percentage?",
    type: "number",
    unit: "%",
    min: 3, max: 20,
    placeholder: "e.g. 5.8",
    invalidMsg: "HbA1c should be between 3 and 20 percent.",
  },
  bloodPressure: {
    label: "Blood Pressure (systolic)",
    question: "What is your systolic blood pressure in mmHg?",
    type: "number",
    unit: "mmHg",
    min: 60, max: 220,
    placeholder: "e.g. 125",
    invalidMsg: "Blood pressure should be between 60 and 220 mmHg.",
  },
  familyHistory: {
    label: "Family History of Diabetes",
    question: "Do you have a family history of diabetes? Yes or No?",
    type: "select",
    options: ["0", "1"],
    placeholder: "Yes or No",
  },
  physicalActivityHours: {
    label: "Physical Activity",
    question: "How many hours per day do you spend on physical activity?",
    type: "number",
    unit: "hours/day",
    min: 0, max: 20,
    placeholder: "e.g. 1.5",
    invalidMsg: "Physical activity should be between 0 and 20 hours.",
  },
  dailySugarIntake: {
    label: "Daily Sugar Intake",
    question: "How many grams of sugar do you consume daily?",
    type: "number",
    unit: "grams",
    min: 0, max: 200,
    placeholder: "e.g. 50",
    invalidMsg: "Daily sugar intake should be between 0 and 200 grams.",
  },
  fastFoodFrequency: {
    label: "Fast Food Frequency",
    question: "How many fast food meals do you eat per week?",
    type: "number",
    unit: "meals/week",
    min: 0, max: 15,
    placeholder: "e.g. 2",
    invalidMsg: "Fast food frequency should be between 0 and 15 meals per week.",
  },
  sleepHours: {
    label: "Sleep Hours",
    question: "How many hours do you sleep each night?",
    type: "number",
    unit: "hours",
    min: 2, max: 14,
    placeholder: "e.g. 7",
    invalidMsg: "Sleep hours should be between 2 and 14.",
  },
  monthlyIncome: {
    label: "Monthly Income",
    question: "What is your monthly household income in rupees? (optional)",
    type: "number",
    unit: "₹",
    min: 0, max: 200000,
    placeholder: "e.g. 30000",
    optional: true,
    invalidMsg: "Please enter a valid income amount.",
  },
};

/**
 * Interpret a speech transcript for a specific field.
 * Returns { value, displayValue, interpreted } or null if not understood.
 */
export function interpretTranscript(transcript, field) {
  const def = FIELD_DEFINITIONS[field];
  if (!def) return null;
  const lower = transcript.toLowerCase().trim();

  // ── Number fields ──────────────────────────────────────────────────────────
  if (def.type === "number") {
    // Convert words to numbers first
    const text = _wordsToNumbers(lower);
    // Extract numeric value
    const match = text.match(/(\d+(?:\.\d+)?)/);
    if (!match) return null;
    const value = parseFloat(match[1]);
    if (isNaN(value)) return null;
    return { value: String(value), displayValue: `${value} ${def.unit || ""}`.trim(), interpreted: value };
  }

  // ── Gender ────────────────────────────────────────────────────────────────
  if (field === "gender") {
    if (/\bmale\b/i.test(lower) && !/fe?male/.test(lower)) return { value: "Male", displayValue: "Male", interpreted: "Male" };
    if (/\bfemale\b/i.test(lower)) return { value: "Female", displayValue: "Female", interpreted: "Female" };
    return null;
  }

  // ── Family History ────────────────────────────────────────────────────────
  if (field === "familyHistory") {
    const YES = /\b(yes|yeah|positive|present|have|has|father|mother|parent|sibling|brother|sister)\b/;
    const NO  = /\b(no|nope|negative|absent|none|never|nobody)\b/;
    if (YES.test(lower)) return { value: "1", displayValue: "Yes — Family history present", interpreted: 1 };
    if (NO.test(lower))  return { value: "0", displayValue: "No — No family history", interpreted: 0 };
    return null;
  }

  // ── Patient Group ─────────────────────────────────────────────────────────
  if (field === "patientGroup") {
    if (/\burban\b/.test(lower))       return { value: "Urban", displayValue: "Urban", interpreted: "Urban" };
    if (/\brural\b/.test(lower))       return { value: "Rural", displayValue: "Rural", interpreted: "Rural" };
    if (/\bsemi[\s-]?urban\b/.test(lower)) return { value: "Semi-Urban", displayValue: "Semi-Urban", interpreted: "Semi-Urban" };
    return null;
  }

  return null;
}

/**
 * Validate a field value against its definition ranges.
 * Returns { valid: boolean, message: string }
 */
export function validateField(field, value) {
  const def = FIELD_DEFINITIONS[field];
  if (!def) return { valid: true, message: "" };

  if (def.type === "number") {
    const num = parseFloat(value);
    if (isNaN(num)) return { valid: false, message: def.invalidMsg || "Please enter a valid number." };
    if (num < def.min || num > def.max) {
      return {
        valid: false,
        message: def.invalidMsg || `Value must be between ${def.min} and ${def.max}.`,
      };
    }
  }
  return { valid: true, message: "" };
}

// ─────────────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────────────

const _WORD_NUM = {
  zero:0, one:1, two:2, three:3, four:4, five:5, six:6, seven:7, eight:8, nine:9,
  ten:10, eleven:11, twelve:12, thirteen:13, fourteen:14, fifteen:15,
  sixteen:16, seventeen:17, eighteen:18, nineteen:19, twenty:20,
  thirty:30, forty:40, fifty:50, sixty:60, seventy:70, eighty:80, ninety:90,
  hundred:100,
};

function _wordsToNumbers(text) {
  let result = text;
  // Replace "twenty five" → 25, etc.
  result = result.replace(/\b([a-z]+)\s+([a-z]+)\b/g, (match, a, b) => {
    const va = _WORD_NUM[a], vb = _WORD_NUM[b];
    if (va && vb && va >= 20 && vb < 10) return String(va + vb);
    return match;
  });
  // Replace single words
  result = result.replace(/\b([a-z]+)\b/g, (word) => {
    return _WORD_NUM[word] !== undefined ? String(_WORD_NUM[word]) : word;
  });
  // Handle "point" → decimal
  result = result.replace(/(\d+)\s+point\s+(\d+)/g, "$1.$2");
  return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// VOICE QUESTIONS — question text for each field
// ─────────────────────────────────────────────────────────────────────────────
export function getVoiceQuestion(field, langCode = "en") {
  const def = FIELD_DEFINITIONS[field];
  return def?.question || `Please provide your ${field}.`;
}
