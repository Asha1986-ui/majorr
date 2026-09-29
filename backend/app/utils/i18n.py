"""
DiaSense AI Internationalization (i18n) Engine.
Provides complete medical translations for clinical predictions, contributing factors,
recommendations, tailored diet plans, and food nutrition analysis across 6 languages:
- en: English
- kn: Kannada (ಕನ್ನಡ)
- hi: Hindi (हिन्दी)
- ta: Tamil (தமிழ்)
- te: Telugu (తెలుగు)
- ml: Malayalam (മലയാളം)
"""

from typing import Dict, Any, List

SUPPORTED_LANGUAGES = ["en", "kn", "hi", "ta", "te", "ml"]

LANGUAGE_NAMES = {
    "en": "English",
    "kn": "Kannada",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
}

def normalize_lang(lang: str) -> str:
    if not lang:
        return "en"
    clean = lang.lower().split(",")[0].split(";")[0].strip()
    if clean.startswith("kn") or clean == "kannada":
        return "kn"
    if clean.startswith("hi") or clean == "hindi":
        return "hi"
    if clean.startswith("ta") or clean == "tamil":
        return "ta"
    if clean.startswith("te") or clean == "telugu":
        return "te"
    if clean.startswith("ml") or clean == "malayalam":
        return "ml"
    return "en"


FACTOR_NAMES: Dict[str, Dict[str, str]] = {
    "Blood Glucose": {
        "en": "Blood Glucose",
        "kn": "ರಕ್ತದಲ್ಲಿನ ಗ್ಲೂಕೋಸ್",
        "hi": "रक्त शर्करा (ग्लूकोज)",
        "ta": "இரத்த குளுக்கோஸ்",
        "te": "రక్తంలో గ్లూకోజ్",
        "ml": "രക്തത്തിലെ ഗ്ലൂക്കോസ്",
    },
    "BMI (Body Mass Index)": {
        "en": "BMI (Body Mass Index)",
        "kn": "ಬಿಎಂಐ (ದೇಹ ದ್ರವ್ಯರಾಶಿ ಸೂಚ್ಯಂಕ)",
        "hi": "बीएमआई (बॉडी मास इंडेक्स)",
        "ta": "பிஎம்ஐ (உடல் நிறை குறியீடு)",
        "te": "బిఎమ్ఐ (బాడీ మాస్ ఇండెక్స్)",
        "ml": "ബിഎംഐ (ബോഡി മാസ് ഇൻഡക്സ്)",
    },
    "Age Category": {
        "en": "Age Category",
        "kn": "ವಯಸ್ಸಿನ ವರ್ಗ",
        "hi": "आयु वर्ग",
        "ta": "வயது பிரிவு",
        "te": "వయస్సు వర్గం",
        "ml": "പ്രായ വിഭാഗം",
    },
    "Diabetes Pedigree Score": {
        "en": "Diabetes Pedigree Score",
        "kn": "ಮಧುಮೇಹ ವಂಶಾವಳಿ ಸ್ಕೋರ್",
        "hi": "मधुमेह वंशावली स्कोर",
        "ta": "நீரிழிவு பரம்பரை ஸ்கோர்",
        "te": "డయాబెటిస్ పెడిగ్రీ స్కోరు",
        "ml": "പ്രമേഹ പെഡിഗ്രി സ്കോർ",
    },
    "Diastolic Blood Pressure": {
        "en": "Diastolic Blood Pressure",
        "kn": "ಡಯಾಸ್ಟೊಲಿಕ್ ರಕ್ತದೊತ್ತಡ",
        "hi": "डायस्टोलिक रक्तचाप",
        "ta": "டயஸ்டோலிக் இரத்த அழுத்தம்",
        "te": "డయాస్టోలిక్ రక్తపోటు",
        "ml": "ഡയസ്റ്റോളിക് രക്തസമ്മർദ്ദം",
    },
}

IMPACT_LABELS: Dict[str, Dict[str, str]] = {
    "High Risk": {
        "en": "High Risk",
        "kn": "ಹೆಚ್ಚಿನ ಅಪಾಯ",
        "hi": "उच्च जोखिम",
        "ta": "அதிக ஆபத்து",
        "te": "అధిక ప్రమాదం",
        "ml": "ഉയർന്ന അപകടസാധ്യത",
    },
    "Moderate Risk": {
        "en": "Moderate Risk",
        "kn": "ಮಧ್ಯಮ ಅಪಾಯ",
        "hi": "मध्यम जोखिम",
        "ta": "மிதமான ஆபத்து",
        "te": "మితమైన ప్రమాదం",
        "ml": "മിതമായ അപകടസാധ്യത",
    },
    "Optimal": {
        "en": "Optimal",
        "kn": "ಸೂಕ್ತ / ಸಾಮಾನ್ಯ",
        "hi": "उत्कृष्ट / सामान्य",
        "ta": "உகந்தது / இயல்பானது",
        "te": "ఆదర్శవంతమైనది / సాధారణం",
        "ml": "അനുയോജ്യം / സാധാരണ നില",
    },
}

FACTOR_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "glucose_high": {
        "en": "Glucose level indicates elevated or impaired fasting glycemic control.",
        "kn": "ಗ್ಲೂಕೋಸ್ ಮಟ್ಟವು ಅಧಿಕ ಅಥವಾ ದುರ್ಬಲಗೊಂಡ ಉಪವಾಸದ ಗ್ಲೈಸೆಮಿಕ್ ನಿಯಂತ್ರಣವನ್ನು ಸೂಚಿಸುತ್ತದೆ.",
        "hi": "ग्लूकोज का स्तर उपवास के समय बढ़े हुए या असंतुलित शर्करा नियंत्रण को दर्शाता है।",
        "ta": "குளுக்கோஸ் அளவு உயர்ந்த அல்லது பலவீனமான இரத்த சர்க்கரை கட்டுப்பாட்டைக் குறிக்கிறது.",
        "te": "గ్లూకోజ్ స్థాయి పెరిగిన లేదా లోపభూయిష్ట ఉపవాస గ్లైసెమిక్ నియంత్రణను సూచిస్తుంది.",
        "ml": "ഗ്ലൂക്കോസ് നില ഉയർന്നതോ അസന്തുലിതമായതോ ആയ ഉപവാസ പഞ്ചസാര നിയന്ത്രണത്തെ സൂചിപ്പിക്കുന്നു.",
    },
    "glucose_mod": {
        "en": "Glucose level falls in pre-diabetic monitoring range (100–139 mg/dL).",
        "kn": "ಗ್ಲೂಕೋಸ್ ಮಟ್ಟವು ಪೂರ್ವ-ಮಧುಮೇಹ ಮೇಲ್ವಿಚಾರಣಾ ವ್ಯಾಪ್ತಿಯಲ್ಲಿದೆ (100–139 mg/dL).",
        "hi": "ग्लूकोज का स्तर प्रीडायबिटिक निगरानी सीमा (100–139 mg/dL) में आता है।",
        "ta": "குளுக்கோஸ் அளவு நீரிழிவுக்கு முந்தைய கண்காணிப்பு வரம்பில் உள்ளது (100–139 mg/dL).",
        "te": "గ్లూకోజ్ స్థాయి ప్రీ-డయాబెటిక్ పర్యవేక్షణ పరిధిలో ఉంది (100–139 mg/dL).",
        "ml": "ഗ്ലൂക്കോസ് നില പ്രീ-ഡയബറ്റിക് നിരീക്ഷണ പരിധിയിലാണ് (100–139 mg/dL).",
    },
    "glucose_opt": {
        "en": "Fasting blood glucose level within healthy normal range (<100 mg/dL).",
        "kn": "ಉಪವಾಸದ ರಕ್ತದ ಗ್ಲೂಕೋಸ್ ಮಟ್ಟವು ಆರೋಗ್ಯಕರ ಸಾಮಾನ್ಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿದೆ (<100 mg/dL).",
        "hi": "उपवास रक्त शर्करा स्तर स्वस्थ सामान्य सीमा (<100 mg/dL) के भीतर है।",
        "ta": "வெறும் வயிற்று இரத்த குளுக்கோஸ் அளவு ஆரோக்கியமான இயல்பு வரம்பில் உள்ளது (<100 mg/dL).",
        "te": "ఫాస్టింగ్ రక్తంలో గ్లూకోజ్ స్థాయి ఆరోగ్యకరమైన సాధారణ పరిధిలో ఉంది (<100 mg/dL).",
        "ml": "ഫാസ്റ്റിംഗ് രക്തത്തിലെ ഗ്ലൂക്കോസ് നില സാധാരണ ആരോഗ്യകരമായ പരിധിയിലാണ് (<100 mg/dL).",
    },
    "bmi_high": {
        "en": "BMI is classified as obese (>=30), increasing insulin resistance.",
        "kn": "ಬಿಎಂಐ ಬೊಜ್ಜು (>=30) ಎಂದು ವರ್ಗೀಕರಿಸಲಾಗಿದೆ, ಇದು ಇನ್ಸುಲಿನ್ ಪ್ರತಿರೋಧವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.",
        "hi": "बीएमआई मोटापे (>=30) के रूप में वर्गीकृत है, जिससे इंसुलिन प्रतिरोध बढ़ता है।",
        "ta": "பிஎம்ஐ உடல் பருமன் (>=30) என வகைப்படுத்தப்பட்டுள்ளது, இது இன்சுலின் எதிர்ப்பை அதிகரிக்கிறது.",
        "te": "బిఎమ్ఐ ఊబకాయం (>=30) గా వర్గీకరించబడింది, ఇది ఇన్సులిన్ నిరోధకతను పెంచుతుంది.",
        "ml": "ബിഎംഐ പൊണ്ണത്തടി (>=30) എന്ന് വർഗ്ഗീകരിച്ചിരിക്കുന്നു, ഇത് ഇൻസുലിൻ പ്രതിരോധം വർദ്ധിപ്പിക്കുന്നു.",
    },
    "bmi_mod": {
        "en": "BMI falls in overweight category (25–29.9).",
        "kn": "ಬಿಎಂಐ ಅಧಿಕ ತೂಕದ ವರ್ಗದಲ್ಲಿದೆ (25–29.9).",
        "hi": "बीएमआई अधिक वजन वाली श्रेणी (25–29.9) में आता है।",
        "ta": "பிஎம்ஐ அதிக எடை பிரிவில் வருகிறது (25–29.9).",
        "te": "బిఎమ్ఐ అధిక బరువు విభాగంలో ఉంది (25–29.9).",
        "ml": "ബിഎംഐ അമിതഭാരമുള്ള വിഭാഗത്തിലാണ് (25–29.9).",
    },
    "bmi_opt": {
        "en": "BMI is within normal healthy range (18.5–24.9).",
        "kn": "ಬಿಎಂಐ ಸಾಮಾನ್ಯ ಆರೋಗ್ಯಕರ ವ್ಯಾಪ್ತಿಯಲ್ಲಿದೆ (18.5–24.9).",
        "hi": "बीएमआई सामान्य स्वस्थ सीमा (18.5–24.9) के भीतर है।",
        "ta": "பிஎம்ஐ இயல்பான ஆரோக்கியமான வரம்பில் உள்ளது (18.5–24.9).",
        "te": "బిఎమ్ఐ సాధారణ ఆరోగ్యకరమైన పరిధిలో ఉంది (18.5–24.9).",
        "ml": "ബിഎംഐ സാധാരണ ആരോഗ്യകരമായ പരിധിയിലാണ് (18.5–24.9).",
    },
    "age_mod": {
        "en": "Age 45+ is an established clinical demographic risk factor.",
        "kn": "45+ ವಯಸ್ಸು ಸ್ಥಾಪಿತ ಕ್ಲಿನಿಕಲ್ ಜನಸಂಖ್ಯಾ ಅಪಾಯದ ಅಂಶವಾಗಿದೆ.",
        "hi": "45+ की आयु एक स्थापित नैदानिक जनसांख्यिकीय जोखिम कारक है।",
        "ta": "45+ வயது என்பது நிறுவப்பட்ட மருத்துவ மக்கள்தொகை ஆபத்துக் காரணியாகும்.",
        "te": "45+ వయస్సు అనేది ఒక స్థిరపడిన క్లినికల్ జనాభా ప్రమాద కారకం.",
        "ml": "45+ പ്രായം സ്ഥാപിതമായ ക്ലിനിക്കൽ ഡെമോഗ്രാഫിക് അപകടസാധ്യത ഘടകമാണ്.",
    },
    "dpf_high": {
        "en": "Strong genetic/family history predisposition score.",
        "kn": "ಬಲವಾದ ಆನುವಂಶಿಕ/ಕುಟುಂಬ ಇತಿಹಾಸದ ಪೂರ್ವಭಾವಿ ಸ್ಕೋರ್.",
        "hi": "मजबूत आनुवंशिक/पारिवारिक इतिहास की संभावना का स्कोर।",
        "ta": "வலுவான மரபணு/குடும்ப வரலாற்று ஆபத்து ஸ்கோர்.",
        "te": "బలమైన జన్యు/కుటుంబ చరిత్ర ప్రమాద స్కోరు.",
        "ml": "ശക്തമായ ജനിതക/കുടുംബ ചരിത്ര സാധ്യത സ്കോർ.",
    },
    "bp_mod": {
        "en": "Diastolic pressure elevated above 90 mmHg standard cutoff.",
        "kn": "ಡಯಾಸ್ಟೊಲಿಕ್ ಒತ್ತಡವು 90 mmHg ಪ್ರಮಾಣಿತ ಕಟ್‌ಆಫ್‌ಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ.",
        "hi": "डायस्टोलिक दबाव 90 mmHg मानक सीमा से अधिक है।",
        "ta": "டயஸ்டோலிக் அழுத்தம் 90 mmHg நிலையான வரம்பிற்கு மேல் உயர்ந்துள்ளது.",
        "te": "డయాస్టోలిక్ పీడనం 90 mmHg ప్రామాణిక పరిమితి కంటే ఎక్కువగా ఉంది.",
        "ml": "ഡയസ്റ്റോളിക് മർദ്ദം 90 mmHg സാധാരണ പരിധിക്ക് മുകളിലാണ്.",
    },
}

RECOMMENDATIONS: Dict[str, Dict[str, str]] = {
    "Diabetic": {
        "en": "Based on your physiological markers, your risk score suggests elevated vulnerability to Type-2 Diabetes. We strongly advise scheduling a comprehensive clinical consultation, adopting a low-glycemic Indian diet, and engaging in regular 150-minute weekly aerobic activity.",
        "kn": "ನಿಮ್ಮ ಶಾರೀರಿಕ ಗುರುತುಗಳ ಆಧಾರದ ಮೇಲೆ, ನಿಮ್ಮ ಅಪಾಯದ ಸ್ಕೋರ್ ಟೈಪ್-2 ಮಧುಮೇಹಕ್ಕೆ ಹೆಚ್ಚಿನ ಒಳಗಾಗುವಿಕೆಯನ್ನು ಸೂಚಿಸುತ್ತದೆ. ಸಮಗ್ರ ಕ್ಲಿನಿಕಲ್ ಸಮಾಲೋಚನೆಯನ್ನು ನಿಗದಿಪಡಿಸಲು, ಕಡಿಮೆ-ಗ್ಲೈಸೆಮಿಕ್ ಭಾರತೀಯ ಆಹಾರವನ್ನು ಅಳವಡಿಸಿಕೊಳ್ಳಲು ಮತ್ತು ವಾರಕ್ಕೆ 150 ನಿಮಿಷಗಳ ಏರೋಬಿಕ್ ವ್ಯಾಯಾಮದಲ್ಲಿ ತೊಡಗಿಸಿಕೊಳ್ಳಲು ನಾವು ಬಲವಾಗಿ ಸಲಹೆ ನೀಡುತ್ತೇವೆ.",
        "hi": "आपके शारीरिक संकेतों के आधार पर, आपका जोखिम स्कोर टाइप-2 मधुमेह की उच्च संभावना को दर्शाता है। हम आपको व्यापक चिकित्सीय परामर्श लेने, कम-ग्लाइसेमिक भारतीय आहार अपनाने और प्रति सप्ताह 150 मिनट एरोबिक व्यायाम करने की दृढ़ सलाह देते हैं।",
        "ta": "உங்கள் உடலியல் குறிப்பான்களின் அடிப்படையில், உங்கள் ஆபத்து ஸ்கோர் வகை-2 நீரிழிவுக்கான அதிக வாய்ப்பைக் குறிக்கிறது. மருத்துவ ஆலோசனையைப் பெறவும், குறைந்த கிளைசெமிக் இந்திய உணவை மேற்கொள்ளவும், வாரத்திற்கு 150 நிமிடங்கள் உடற்பயிற்சி செய்யவும் நாங்கள் கடுமையாக பரிந்துரைக்கிறோம்.",
        "te": "మీ శరీర గుర్తుల ఆధారంగా, మీ రిస్క్ స్కోరు టైప్-2 డయాబెటిస్ వచ్చే అవకాశాన్ని సూచిస్తుంది. సమగ్ర వైద్య సంప్రదింపులను పొందాలని, తక్కువ-గ్లైసెమిక్ భారతీయ ఆహారాన్ని తీసుకోవాలని మరియు వారానికి 150 నిమిషాలు ఏరోబిక్ వ్యాయామం చేయాలని మేము గట్టిగా సిఫార్సు చేస్తున్నాము.",
        "ml": "നിങ്ങളുടെ ശരീര സൂചകങ്ങളെ അടിസ്ഥാനമാക്കി, നിങ്ങളുടെ അപകടസാധ്യത സ്കോർ ടൈപ്പ്-2 പ്രമേഹത്തിനുള്ള ഉയർന്ന സാധ്യതയെ സൂചിപ്പിക്കുന്നു. സമഗ്രമായ വൈദ്യപരിശോധന നടത്താനും കുറഞ്ഞ ഗ്ലൈസെമിക് ഇന്ത്യൻ ഭക്ഷണക്രമം സ്വീകരിക്കാനും ആഴ്ചയിൽ 150 മിനിറ്റ് വ്യായാമം ചെയ്യാനും ഞങ്ങൾ ശക്തമായി നിർദ്ദേശിക്കുന്നു.",
    },
    "Non-Diabetic": {
        "en": "Your physiological markers indicate a normal diabetes screening status. Maintain a balanced high-fiber diet, stay physically active with regular exercise, and continue routine health monitoring.",
        "kn": "ನಿಮ್ಮ ಶಾರೀರಿಕ ಗುರುತುಗಳು ಸಾಮಾನ್ಯ ಮಧುಮೇಹ ತಪಾಸಣೆ ಸ್ಥಿತಿಯನ್ನು ಸೂಚಿಸುತ್ತವೆ. ಸಮತೋಲಿತ ಹೆಚ್ಚಿನ ಫೈಬರ್ ಆಹಾರವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ, ನಿಯಮಿತ ವ್ಯಾಯಾಮದೊಂದಿಗೆ ಸಕ್ರಿಯವಾಗಿರಿ ಮತ್ತು ದಿನಚರಿ ಆರೋಗ್ಯ ತಪಾಸಣೆಯನ್ನು ಮುಂದುವರಿಸಿ.",
        "hi": "आपके शारीरिक संकेत सामान्य मधुमेह स्क्रीनिंग स्थिति दर्शाते हैं। संतुलित उच्च-फाइबर आहार बनाए रखें, नियमित व्यायाम से सक्रिय रहें और समय-समय पर स्वास्थ्य निगरानी जारी रखें।",
        "ta": "உங்கள் உடலியல் குறிப்பான்கள் இயல்பான நீரிழிவு பரிசோதனை நிலையைக் காட்டுகின்றன. சீரான நார்ச்சத்து உள்ள உணவை பராமரிக்கவும், தொடர்ந்து உடற்பயிற்சி செய்யவும் மற்றும் வழக்கமான சுகாதார பரிசோதனையைத் தொடரவும்.",
        "te": "మీ శరీర గుర్తులు సాధారణ డయాబెటిస్ స్క్రీనింగ్ స్థితిని సూచిస్తున్నాయి. సమతుల్య అధిక పీచు పదార్ధాల ఆహారాన్ని తీసుకోండి, క్రమం తప్పకుండా వ్యాయామం చేయండి మరియు ఆరోగ్య పర్యవేక్షణను కొనసాగించండి.",
        "ml": "നിങ്ങളുടെ ശരീര സൂചകങ്ങൾ സാധാരണ പ്രമേഹ പരിശോധന നിലയെ കാണിക്കുന്നു. സമീകൃതമായ ഉയർന്ന നാരുകളടങ്ങിയ ഭക്ഷണം നിലനിർത്തുക, പതിവ് വ്യായാമത്തിലൂടെ സജീവമായിരിക്കുക, പതിവ് ആരോഗ്യ നിരീക്ഷണം തുടരുക.",
    },
}

DIET_PLANS: Dict[str, Dict[str, Dict[str, str]]] = {
    "HighRisk": {
        "breakfast": {
            "en": "Oats & Ragi Dosa (2 pcs) with Mint Chutney, 1 Boiled Egg / Paneer Bhurji (Low-GI Indian Breakfast).",
            "kn": "ಓಟ್ಸ್ ಮತ್ತು ರಾಗಿ ದೋಸೆ (2) ಪುದೀನಾ ಚಟ್ನಿ, ಪನೀರ್ ಭುರ್ಜಿ / 1 ಬೇಯಿಸಿದ ಮೊಟ್ಟೆಯೊಂದಿಗೆ (ಕಡಿಮೆ-ಜಿಐ ಭಾರತೀಯ ಉಪಹಾರ).",
            "hi": "ओट्स और रागी डोसा (2) पुदीना चटनी, 1 उबला अंडा / पनीर भुर्जी के साथ (लो-जीआई भारतीय नाश्ता)।",
            "ta": "ஓட்ஸ் மற்றும் ராகி தோசை (2) புதினா சட்னி, 1 வேகவைத்த முட்டை / பன்னீர் புர்ஜியுடன் (குறைந்த-ஜிஐ காலை உணவு).",
            "te": "ఓట్స్ మరియు రాగి దోస (2) పుదీనా చట్నీ, 1 ఉడకబెట్టిన గుడ్డు / పనీర్ భుర్జితో (తక్కువ-జిఐ అల్పాహారం).",
            "ml": "ഓട്സ് & റാഗി ദോശ (2) പുതിന ചട്ണി, 1 പുഴുങ്ങിയ മുട്ട / പനീർ ഭൂർജി (കുറഞ്ഞ-ജിഐ പ്രാതൽ).",
        },
        "lunch": {
            "en": "Moong Dal & Spinach Khichdi with 1 cup Cucumber Raita and Sprouted Chana Salad.",
            "kn": "ಹೆಸರು ಬೇಳೆ ಮತ್ತು ಪಾಲಕ್ ಕಿಚಡಿ, 1 ಕಪ್ ಸೌತೆಕಾಯಿ ರೈತಾ ಮತ್ತು ಮೊಳಕೆ ಕಟ್ಟಿದ ಕಾಳುಗಳ ಸಲಾಡ್.",
            "hi": "मूंग दाल और पालक खिचड़ी, 1 कप खीरा रायता और अंकुरित चना सलाद के साथ।",
            "ta": "பாசிப்பருப்பு மற்றும் கீரை கிச்சடி, 1 கப் வெள்ளரி ராய்தா மற்றும் முளைகட்டிய கொண்டைக்கடலை சாலட்.",
            "te": "పెసరపప్పు మరియు పాలకూర కిచిడీ, 1 కప్పు కీరదోస రైతా మరియు మొలకల సలాడ్.",
            "ml": "ചെറുപയർ പരിപ്പും ചീരയും ചേർത്ത കിച്ചടി, 1 കപ്പ് വെള്ളരിക്ക റായ്ത്ത, മുളപ്പിച്ച കടല സാലഡ്.",
        },
        "dinner": {
            "en": "Palak Paneer with 2 Bajra/Multigrain Rotis and Steamed Lauki/Turai Subzi.",
            "kn": "ಪಾಲಕ್ ಪನೀರ್ ಜೊತೆಗೆ 2 ಸಜ್ಜೆ/ಮಲ್ಟಿಗ್ರೇನ್ ರೊಟ್ಟಿಗಳು ಮತ್ತು ಸೋರೆಕಾಯಿ ಪಲ್ಯ.",
            "hi": "पालक पनीर, 2 बाजरा/मल्टीग्रेन रोटियां और उबली हुई लौकी की सब्जी।",
            "ta": "பாலக் பன்னீர், 2 கம்பு/தானிய ரொட்டிகள் மற்றும் சுரைக்காய் பொரியல்.",
            "te": "పాలక్ పనీర్, 2 సజ్జ/మల్టీగ్రెయిన్ రొట్టెలు మరియు సొరకాయ కూర.",
            "ml": "പാലക് പനീർ, 2 ബജ്റ/ധാന്യ റൊട്ടികൾ, വേവിച്ച ചുരയ്ക്ക കറി.",
        },
        "snacks": {
            "en": "1 cup Roasted Makhana (Fox Nuts) with Green Tea or Sprouted Moong Salad.",
            "kn": "1 ಕಪ್ ಹುರಿದ ಮಖಾನಾ ಹಸಿರು ಚಹಾದೊಂದಿಗೆ ಅಥವಾ ಮೊಳಕೆ ಕಾಳುಗಳ ಚಾಟ್.",
            "hi": "1 कप भुना हुआ मखाना ग्रीन टी के साथ या अंकुरित मूंग सलाद।",
            "ta": "1 கப் வறுத்த மக்கானா கிரீன் டீயுடன் அல்லது முளைகட்டிய பாசிப்பயறு சாலட்.",
            "te": "1 కప్పు వేయించిన మఖానా గ్రీన్ టీతో లేదా మొలకల సలాడ్.",
            "ml": "1 കപ്പ് വറുത്ത മഖാന ഗ്രീൻ ടീക്കൊപ്പം അല്ലെങ്കിൽ മുളപ്പിച്ച ചെറുപയർ സാലഡ്.",
        },
        "exercise": {
            "en": "30-45 mins Brisk Walking, 15 mins Surya Namaskar & Light Resistance Training 5 days/week.",
            "kn": "ದಿನಕ್ಕೆ 30-45 ನಿಮಿಷಗಳ ಚುರುಕಾದ ನಡಿಗೆ, 15 ನಿಮಿಷಗಳ ಸೂರ್ಯ ನಮಸ್ಕಾರ ಮತ್ತು ಹಗುರವಾದ ವ್ಯಾಯಾಮಗಳು (ವಾರಕ್ಕೆ 5 ದಿನಗಳು).",
            "hi": "30-45 मिनट तेज चलना, 15 मिनट सूर्य नमस्कार और हल्का व्यायाम (सप्ताह में 5 दिन)।",
            "ta": "30-45 நிமிடங்கள் விறுவிறுப்பான நடைபயிற்சி, 15 நிமிடங்கள் சூரிய நமஸ்காரம் மற்றும் லேசான உடற்பயிற்சி (வாரத்திற்கு 5 நாட்கள்).",
            "te": "30-45 నిమిషాలు వేగంగా నడవడం, 15 నిమిషాలు సూర్య నమస్కారాలు మరియు తేలికపాటి వ్యాయామాలు (వారానికి 5 రోజులు).",
            "ml": "30-45 മിനിറ്റ് വേഗത്തിലുള്ള നടത്തം, 15 മിനിറ്റ് സൂര്യനമസ്കാരം, ലഘു വ്യായാമങ്ങൾ (ആഴ്ചയിൽ 5 ദിവസം).",
        },
        "tips": {
            "en": "Limit polished white rice, replace with Brown Rice/Ragi/Bajra. Drink 3L water daily and eliminate sugary chai.",
            "kn": "ಬಿಳಿ ಅಕ್ಕಿಯನ್ನು ಮಿತಿಗೊಳಿಸಿ, ಕೆಂಪು ಅಕ್ಕಿ/ರಾಗಿ/ಸಜ್ಜೆಯೊಂದಿಗೆ ಬದಲಾಯಿಸಿ. ಪ್ರತಿದಿನ 3 ಲೀಟರ್ ನೀರು ಕುಡಿಯಿರಿ ಮತ್ತು ಸಕ್ಕರೆ ಚಹಾವನ್ನು ತ್ಯಜಿಸಿ.",
            "hi": "सफेद चावल सीमित करें, उसकी जगह भूरा चावल/रागी/बाजरा लें। रोजाना 3 लीटर पानी पिएं और मीठी चाय छोड़ें।",
            "ta": "வெள்ளை அரிசியைக் குறைத்து, அதற்குப் பதிலாக பழுப்பு அரிசி/ராகி/கம்பு சேர்க்கவும். தினமும் 3 லிட்டர் தண்ணீர் குடிக்கவும் மற்றும் சர்க்கரை தேநீரைத் தவிர்க்கவும்.",
            "te": "తెల్లటి బియ్యాన్ని తగ్గించి, బ్రౌన్ రైస్/రాగి/సజ్జలతో భర్తీ చేయండి. రోజూ 3 లీటర్ల నీరు త్రాగండి మరియు చక్కెర టీని నివారించండి.",
            "ml": "വെള്ള അരി പരിമിതപ്പെടുത്തി തവിട്ട് അരി/റാഗി/ബജ്റ ഉപയോഗിക്കുക. ദിവസവും 3 ലിറ്റർ വെള്ളം കുടിക്കുക, പഞ്ചസാര ചായ ഒഴിവാക്കുക.",
        },
    },
    "LowRisk": {
        "breakfast": {
            "en": "Methi Paratha (1 pc with curd) or Vegetable Oats Upma with 1 Boiled Egg.",
            "kn": "ಮೆಂತ್ಯ ಪರೋಟಾ (1 ಮೊಸರಿನೊಂದಿಗೆ) ಅಥವಾ ತರಕಾರಿ ಓಟ್ಸ್ ಉಪ್ಮಾ ಮತ್ತು 1 ಬೇಯಿಸಿದ ಮೊಟ್ಟೆ.",
            "hi": "मेथी पराठा (1 दही के साथ) या वेजिटेबल ओट्स उपमा और 1 उबला अंडा।",
            "ta": "மேத்தி பரோட்டா (1 தயிருடன்) அல்லது காய்கறி ஓட்ஸ் உப்மா மற்றும் 1 வேகவைத்த முட்டை.",
            "te": "మేథీ పరాఠా (1 పెరుగుతో) లేదా వెజిటబుల్ ఓట్స్ ఉప్మా మరియు 1 ఉడకబెట్టిన గుడ్డు.",
            "ml": "മേത്തി പറാത്ത (1 തൈരിനൊപ്പം) അല്ലെങ്കിൽ വെജിറ്റബിൾ ഓട്സ് ഉപ്പുമാവ്, 1 പുഴുങ്ങിയ മുട്ട.",
        },
        "lunch": {
            "en": "Brown Rice Bowl with Rajma/Chole, Mixed Green Salad, and Cucumber Raita.",
            "kn": "ಕಂದು ಅಕ್ಕಿ ಬೌಲ್ ರಾಜ್ಮಾ/ಚೋಲೆ, ಹಸಿರು ಸಲಾಡ್ ಮತ್ತು ಸೌತೆಕಾಯಿ ರೈತಾದೊಂದಿಗೆ.",
            "hi": "ब्राउन राइस बाउल राजमा/छोले, हरी सलाद और खीरे के रायते के साथ।",
            "ta": "பழுப்பு அரிசி சாதம் ராஜ்மா/கொண்டைக்கடலை, கீரை சாலட் மற்றும் வெள்ளரி ராய்தாவுடன்.",
            "te": "బ్రౌన్ రైస్ బౌల్ రాజ్మా/చోలే, ఆకుకూరల సలాడ్ మరియు కీరదోస రైతాతో.",
            "ml": "തവിട്ട് അരി രാജ്മ/ചോലെ, പച്ചക്കറി സാലഡ്, വെള്ളരിക്ക റായ്ത്ത എന്നിവയ്ക്കൊപ്പം.",
        },
        "dinner": {
            "en": "Tandoori Chicken / Paneer Tikka with Grilled Vegetables and 1 Whole Wheat Roti.",
            "kn": "ತಂದೂರಿ ಚಿಕನ್ / ಪನೀರ್ ಟಿಕ್ಕಾ ಹುರಿದ ತರಕಾರಿಗಳು ಮತ್ತು 1 ಗೋಧಿ ಚಪಾತಿಯೊಂದಿಗೆ.",
            "hi": "तंदूरी चिकन / पनीर टिक्का ग्रिल्ड सब्जियों और 1 गेहूं की रोटी के साथ।",
            "ta": "தந்தூரி சிக்கன் / பன்னீர் டிக்கா காய்கறிகள் மற்றும் 1 கோதுமை ரொட்டியுடன்.",
            "te": "తందూరి చికెన్ / పనీర్ టిక్కా కూరగాయలు మరియు 1 గోధుమ రొట్టెతో.",
            "ml": "തന്തൂരി ചിക്കൻ / പനീർ ടിക്ക ഗ്രിൽ ചെയ്ത പച്ചക്കറികൾ, 1 ഗോതമ്പ് റൊട്ടി.",
        },
        "snacks": {
            "en": "Roasted Chana, Apple Slices with Peanut Butter, or Handful of Almonds & Walnuts.",
            "kn": "ಹುರಿದ ಕಡಲೆ, ಕಡಲೆಕಾಯಿ ಬೆಣ್ಣೆಯೊಂದಿಗೆ ಸೇಬು, ಅಥವಾ ಬಾದಾಮಿ ಮತ್ತು ವಾಲ್ನಟ್ಸ್.",
            "hi": "भुना हुआ चना, पीनट बटर के साथ सेब के टुकड़े, या मुट्ठी भर बादाम और अखरोट।",
            "ta": "வறுத்த கடலை, வேர்க்கடலை வெண்ணெயுடன் ஆப்பிள், அல்லது பாதாம் மற்றும் அக்ரூட் பருப்புகள்.",
            "te": "వేయించిన శనగలు, పీనట్ బటర్‌తో యాపిల్ ముక్కలు, లేదా బాదం మరియు వాల్‌నట్‌లు.",
            "ml": "വറുത്ത കടല, പീനട്ട് ബട്ടറിനൊപ്പം ആപ്പിൾ, അല്ലെങ്കിൽ ബദാം, വാൽനട്ട്.",
        },
        "exercise": {
            "en": "150 minutes of moderate-intensity activity (Brisk Walk, Jogging, Yoga) per week.",
            "kn": "ವಾರಕ್ಕೆ 150 ನಿಮಿಷಗಳ ಮಧ್ಯಮ ತೀವ್ರತೆಯ ಚಟುವಟಿಕೆ (ಚುರುಕಾದ ನಡಿಗೆ, ಜಾಗಿಂಗ್, ಯೋಗ).",
            "hi": "प्रति सप्ताह 150 मिनट मध्यम तीव्रता की गतिविधि (तेज चलना, जॉगिंग, योग)।",
            "ta": "வாரத்திற்கு 150 நிமிடங்கள் மிதமான உடற்பயிற்சி (நடைபயிற்சி, ஜாகிங், யோகா).",
            "te": "వారానికి 150 నిమిషాలు మితమైన వ్యాయామం (నడక, జాగింగ్, యోగా).",
            "ml": "ആഴ്ചയിൽ 150 മിനിറ്റ് മിതമായ വ്യായാമം (വേഗത്തിലുള്ള നടത്തം, ജോഗിംഗ്, യോഗ).",
        },
        "tips": {
            "en": "Maintain consistent sleep schedule, practice stress management through Pranayama, and maintain balanced portion control.",
            "kn": "ನಿರಂತರ ನಿದ್ರೆಯ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ, ಪ್ರಾಣಾಯಾಮದ ಮೂಲಕ ಒತ್ತಡ ನಿರ್ವಹಣೆ ಮಾಡಿ ಮತ್ತು ಸಮತೋಲಿತ ಆಹಾರ ಸೇವಿಸಿ.",
            "hi": "नियमित नींद का समय रखें, प्राणायाम से तनाव प्रबंधन करें और संतुलित भोजन मात्रा बनाए रखें।",
            "ta": "சீரான தூக்க வழக்கத்தை வைத்திருங்கள், பிராணாயாமம் மூலம் மன அழுத்தத்தைக் குறைக்கவும் மற்றும் சீரான உணவை உட்கொள்ளவும்.",
            "te": "క్రమం తప్పకుండా నిద్రపోండి, ప్రాణాయామం ద్వారా ఒత్తిడిని తగ్గించండి మరియు సమతుల్య ఆహారం తీసుకోండి.",
            "ml": "കൃത്യമായ ഉറക്കക്രമം പാലിക്കുക, പ്രാണായാമം വഴി മാനസിക സമ്മർദ്ദം കുറയ്ക്കുക, സമീകൃതാഹാരം കഴിക്കുക.",
        },
    },
}

def localize_contributing_factors(factors: List[Dict[str, Any]], lang: str = "en") -> List[Dict[str, Any]]:
    norm_lang = normalize_lang(lang)
    if norm_lang == "en":
        return factors

    localized = []
    for f in factors:
        raw_factor = f.get("factor", "")
        raw_impact = f.get("impact", "")
        raw_desc = f.get("description", "")
        raw_val = f.get("value", "")

        # 1. Translate Factor Name
        factor_name = FACTOR_NAMES.get(raw_factor, {}).get(norm_lang, raw_factor)

        # 2. Translate Impact Label
        impact_label = IMPACT_LABELS.get(raw_impact, {}).get(norm_lang, raw_impact)

        # 3. Match and translate description
        desc = raw_desc
        for key, trans_dict in FACTOR_DESCRIPTIONS.items():
            if trans_dict.get("en") == raw_desc or key in raw_desc.lower():
                desc = trans_dict.get(norm_lang, raw_desc)
                break
        
        # If no direct match, check sub-strings
        if desc == raw_desc:
            if "100–139" in raw_desc or "pre-diabetic" in raw_desc.lower():
                desc = FACTOR_DESCRIPTIONS["glucose_mod"].get(norm_lang, desc)
            elif "elevated" in raw_desc.lower() or "impaired" in raw_desc.lower():
                desc = FACTOR_DESCRIPTIONS["glucose_high"].get(norm_lang, desc)
            elif "<100" in raw_desc or "normal range" in raw_desc.lower() and "glucose" in raw_factor.lower():
                desc = FACTOR_DESCRIPTIONS["glucose_opt"].get(norm_lang, desc)
            elif "obese" in raw_desc.lower():
                desc = FACTOR_DESCRIPTIONS["bmi_high"].get(norm_lang, desc)
            elif "overweight" in raw_desc.lower():
                desc = FACTOR_DESCRIPTIONS["bmi_mod"].get(norm_lang, desc)
            elif "normal healthy range" in raw_desc.lower() and "bmi" in raw_factor.lower():
                desc = FACTOR_DESCRIPTIONS["bmi_opt"].get(norm_lang, desc)
            elif "45+" in raw_desc:
                desc = FACTOR_DESCRIPTIONS["age_mod"].get(norm_lang, desc)
            elif "genetic" in raw_desc.lower() or "pedigree" in raw_desc.lower():
                desc = FACTOR_DESCRIPTIONS["dpf_high"].get(norm_lang, desc)
            elif "90 mmhg" in raw_desc.lower() or "diastolic" in raw_desc.lower():
                desc = FACTOR_DESCRIPTIONS["bp_mod"].get(norm_lang, desc)

        localized.append({
            "factor": factor_name,
            "value": raw_val,
            "impact": impact_label,
            "description": desc,
        })
    return localized

def localize_recommendation(pred_label: str, lang: str = "en") -> str:
    norm_lang = normalize_lang(lang)
    if pred_label in RECOMMENDATIONS:
        return RECOMMENDATIONS[pred_label].get(norm_lang, RECOMMENDATIONS[pred_label]["en"])
    return RECOMMENDATIONS["Non-Diabetic"].get(norm_lang, RECOMMENDATIONS["Non-Diabetic"]["en"])

def localize_diet_plan(plan_type: str, lang: str = "en") -> Dict[str, str]:
    norm_lang = normalize_lang(lang)
    category = "HighRisk" if plan_type in ["Diabetic", "HighRisk"] else "LowRisk"
    d = DIET_PLANS[category]
    return {
        "breakfast": d["breakfast"].get(norm_lang, d["breakfast"]["en"]),
        "lunch": d["lunch"].get(norm_lang, d["lunch"]["en"]),
        "dinner": d["dinner"].get(norm_lang, d["dinner"]["en"]),
        "snacks": d["snacks"].get(norm_lang, d["snacks"]["en"]),
        "exercise": d["exercise"].get(norm_lang, d["exercise"]["en"]),
        "tips": d["tips"].get(norm_lang, d["tips"]["en"]),
    }
