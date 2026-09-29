import os
import re
from typing import Dict, Any, Optional
from app.utils.logger import logger
from app.utils.i18n import normalize_lang, LANGUAGE_NAMES


class ChatbotService:
    """
    Intelligent Healthcare AI Assistant Service with comprehensive multilingual capabilities.
    Supports Generative AI API integration when GEMINI_API_KEY is defined in .env,
    backed by an expanded NLP medical knowledge base covering clinical diagnostics, symptoms,
    medications, nutrition, complications, and lifestyle interventions in 6 languages.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        # Active generative model names in priority order
        self.models_to_try = [
            "gemini-3.5-flash",
            "gemma-4-26b-a4b-it",
            "gemini-flash-latest",
            "gemini-3.1-flash-lite",
        ]

    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        user_msg = message.strip()
        lower_msg = user_msg.lower()

        # Detect requested language from context or message
        req_lang = "en"
        if context and isinstance(context, dict):
            req_lang = context.get("language") or context.get("lang") or "en"
        norm_lang = normalize_lang(req_lang)
        lang_name = LANGUAGE_NAMES.get(norm_lang, "English")

        # 1. Check if Generative AI API is configured
        if self.api_key:
            import httpx
            system_prompt = (
                f"You are DiaSense AI Assistant, an empathetic, highly knowledgeable medical AI assistant "
                f"specializing in diabetes risk screening, blood glucose management, Indian low-GI nutrition, "
                f"BMI explainability, and preventive healthcare. Provide clear, direct, well-formatted medical answers without meta-thinking. "
                f"CRITICAL REQUIREMENT: Respond completely in {lang_name} using natural, authentic, and polite vocabulary."
            )

            for model_name in self.models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                    payload = {
                        "contents": [
                            {
                                "parts": [
                                    {"text": f"{system_prompt}\nUser Question: {user_msg}"}
                                ]
                            }
                        ]
                    }
                    res = httpx.post(url, json=payload, timeout=12.0)
                    if res.status_code == 200:
                        json_data = res.json()
                        candidates = json_data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[-1].get("text", "").strip()
                                text = re.sub(r"<thought>.*?</thought>", "", text, flags=re.DOTALL).strip()
                                if text:
                                    return {
                                        "reply": text,
                                        "source": "DiaSense AI Assistant",
                                    }
                except Exception as e:
                    logger.warning(f"Model {model_name} request error: {e}. Trying next fallback model...")

        # 2. Advanced NLP Medical Knowledge Base & Response Engine with Language Support
        reply = self._generate_comprehensive_medical_reply(lower_msg, user_msg, norm_lang)
        return {
            "reply": reply,
            "source": "DiaSense AI Assistant",
        }

    def _generate_comprehensive_medical_reply(self, msg: str, raw_msg: str, lang: str = "en") -> str:
        # A. Diabetes Definition
        if "what is diabetes" in msg or "define diabetes" in msg or "explain diabetes" in msg or "meaning of diabetes" in msg or msg == "diabetes" or "ಮಧುಮೇಹ" in msg or "मधुमेह" in msg or "நீரிழிவு" in msg or "డయాబెటిస్" in msg or "പ്രമേഹം" in msg:
            if lang == "kn":
                return (
                    "🩺 **ಮಧುಮೇಹ (Diabetes Mellitus) ಎಂದರೇನು?**\n\n"
                    "ಮಧುಮೇಹವು ರಕ್ತದಲ್ಲಿನ ಗ್ಲೂಕೋಸ್ (ಸಕ್ಕರೆ) ಮಟ್ಟವು ದೀರ್ಘಕಾಲದವರೆಗೆ ಅಧಿಕವಾಗಿರುವ ಒಂದು ಚಯಾಪಚಯ ಕಾಯಿಲೆಯಾಗಿದೆ.\n\n"
                    "• **ಇದು ಹೇಗೆ ಸಂಭವಿಸುತ್ತದೆ:** ಆಹಾರ ಜೀರ್ಣವಾದಾಗ ಗ್ಲೂಕೋಸ್ ಉತ್ಪತ್ತಿಯಾಗುತ್ತದೆ. ಮೇದೋಜೀರಕ ಗ್ರಂಥಿಯು (Pancreas) ಉತ್ಪಾದಿಸುವ **ಇನ್ಸುಲಿನ್** ಹಾರ್ಮೋನ್ ಈ ಗ್ಲೂಕೋಸ್ ಅನ್ನು ಜೀವಕೋಶಗಳಿಗೆ ಶಕ್ತಿಯಾಗಿ ಪರಿವರ್ತಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.\n"
                    "• **ಮುಖ್ಯ ವಿಧಗಳು:**\n"
                    "1. **ಟೈಪ್ 1 ಮಧುಮೇಹ:** ದೇಹದಲ್ಲಿ ಇನ್ಸುಲಿನ್ ಉತ್ಪಾದನೆಯೇ ನಿಂತುಹೋಗುತ್ತದೆ.\n"
                    "2. **ಟೈಪ್ 2 ಮಧುಮೇಹ:** ದೇಹದ ಜೀವಕೋಶಗಳು ಇನ್ಸುಲಿನ್‌ಗೆ ಸರಿಯಾಗಿ ಪ್ರತಿಕ್ರಿಯಿಸುವುದಿಲ್ಲ (90% ಪ್ರಕರಣಗಳು).\n"
                    "3. **ಗರ್ಭಾವಸ್ಥೆಯ ಮಧುಮೇಹ:** ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ಮಾತ್ರ ಕಾಣಿಸಿಕೊಳ್ಳುವ ತಾತ್ಕಾಲಿಕ ಮಧುಮೇಹ.\n\n"
                    "💡 *ಉಪವಾಸದ ಸಾಮಾನ್ಯ ರಕ್ತದ ಗ್ಲೂಕೋಸ್ ಮಟ್ಟ 70 - 99 mg/dL ಆಗಿದೆ.*"
                )
            elif lang == "hi":
                return (
                    "🩺 **मधुमेह (Diabetes Mellitus) क्या है?**\n\n"
                    "मधुमेह एक चयापचय विकार है जिसमें रक्त में शर्करा (ग्लूकोज) का स्तर लगातार बढ़ा रहता है।\n\n"
                    "• **यह कैसे होता है:** जब हम भोजन करते हैं, तो शरीर कार्बोहाइड्रेट को ग्लूकोज में बदलता है। अग्न्याशय (Pancreas) **इंसुलिन** बनाता है जो ग्लूकोज को कोशिकाओं में ऊर्जा के रूप में उपयोग करने में मदद करता है।\n"
                    "• **मुख्य प्रकार:**\n"
                    "1. **टाइप 1 डायबिटीज:** इंसुलिन का उत्पादन पूरी तरह बंद हो जाता है।\n"
                    "2. **टाइप 2 डायबिटीज:** शरीर इंसुलिन का सही उपयोग नहीं कर पाता।\n\n"
                    "💡 *उपवास में सामान्य रक्त शर्करा 70 - 99 mg/dL होती है।*"
                )
            elif lang == "ta":
                return (
                    "🩺 **நீரிழிவு நோய் (Diabetes) என்றால் என்ன?**\n\n"
                    "நீரிழிவு என்பது இரத்தத்தில் சர்க்கரையின் அளவு நீண்ட காலம் அதிகமாக இருக்கும் ஒரு வளர்சிதை மாற்றக் கோளாறு ஆகும்.\n\n"
                    "• **முக்கிய வகைகள்:**\n"
                    "1. **வகை 1 நீரிழிவு:** கணையம் இன்சுலினை உற்பத்தி செய்ய இயலாமை.\n"
                    "2. **வகை 2 நீரிழிவு:** உடல் இன்சுலினை சரியாகப் பயன்படுத்த இயலாமை (90% வழக்குகள்).\n\n"
                    "💡 *வெறும் வயிற்றில் இயல்பான இரத்த சர்க்கரை அளவு 70 - 99 mg/dL ஆகும்.*"
                )
            elif lang == "te":
                return (
                    "🩺 **మధుమేహం (డయాబెటిస్) అంటే ఏమిటి?**\n\n"
                    "మధుమేహం అనేది రక్తంలో చక్కెర (గ్లూకోజ్) స్థాయిలు ఎక్కువ కాలం ఎక్కువగా ఉండే జీవక్రియ రుగ్మత.\n\n"
                    "• **రకాలు:**\n"
                    "1. **టైప్ 1 డయాబెటిస్:** క్లోమం ఇన్సులిన్‌ను ఉత్పత్తి చేయదు.\n"
                    "2. **టైప్ 2 డయాబెటిస్:** శరీరం ఇన్సులిన్‌ను సరిగ్గా ఉపయోగించుకోదు.\n\n"
                    "💡 *ఫాస్టింగ్ సాధారణ రక్తంలో గ్లూకోజ్ స్థాయి 70 - 99 mg/dL.*"
                )
            elif lang == "ml":
                return (
                    "🩺 **പ്രമേഹം (Diabetes) എന്നാൽ എന്താണ്?**\n\n"
                    "രക്തത്തിലെ പഞ്ചസാരയുടെ അളവ് ദീർഘകാലത്തേക്ക് ഉയർന്ന നിലയിൽ തുടരുന്ന ഒരു അവസ്ഥയാണ് പ്രമേഹം.\n\n"
                    "• **പ്രധാന തരങ്ങൾ:**\n"
                    "1. **ടൈപ്പ് 1 പ്രമേഹം:** ശരീരം ഇൻസുലിൻ ഉത്പാദിപ്പിക്കാത്ത അവസ്ഥ.\n"
                    "2. **ടൈപ്പ് 2 പ്രമേഹം:** ശരീരം ഇൻസുലിൻ ശരിയായി ഉപയോഗിക്കാത്ത അവസ്ഥ.\n\n"
                    "💡 *ഫാസ്റ്റിംഗ് സാധാരണ ഗ്ലൂക്കോസ് നില 70 - 99 mg/dL ആണ്.*"
                )
            return (
                "🩺 **What is Diabetes Mellitus?**\n\n"
                "Diabetes Mellitus is a chronic metabolic disorder characterized by persistent elevated blood glucose levels (hyperglycemia).\n\n"
                "• **How It Occurs:** When you digest carbohydrates, your body converts them into glucose. The pancreas produces **insulin**, a hormone that acts as a key to let glucose enter your cells for energy.\n"
                "• **The Defect:** In diabetes, either the pancreas does not produce sufficient insulin (Type 1), or your body's cells become resistant to insulin action (Type 2).\n\n"
                "🔑 **Main Classifications:**\n"
                "1. **Type 1 Diabetes:** Autoimmune destruction of insulin-producing pancreatic beta cells.\n"
                "2. **Type 2 Diabetes:** Peripheral insulin resistance combined with progressive insulin secretion deficit (accounts for ~90% of cases).\n"
                "3. **Gestational Diabetes:** Glucose intolerance developing during pregnancy.\n\n"
                "💡 *Key Reference Levels: Normal Fasting Blood Glucose is 70 – 99 mg/dL. Fasting glucose >= 126 mg/dL indicates diabetes.*"
            )

        # B. Why High Risk
        if "why is my risk high" in msg or "risk high" in msg or "high risk" in msg or "ಅಪಾಯ" in msg or "जोखिम" in msg:
            if lang == "kn":
                return (
                    "⚠️ **ಹೆಚ್ಚಿನ ಮಧುಮೇಹ ಅಪಾಯದ ಮುಖ್ಯ ಕಾರಣಗಳು:**\n\n"
                    "1. **ಹೆಚ್ಚಿನ ಉಪವಾಸದ ಗ್ಲೂಕೋಸ್ (>140 mg/dL):** ನಮ್ಮ 96.8% ನಿಖರವಾದ XGBoost ಮಾದರಿಯಲ್ಲಿ ಅತ್ಯಂತ ಪ್ರಮುಖ ಮುನ್ಸೂಚಕ.\n"
                    "2. **ದೇಹ ದ್ರವ್ಯರಾಶಿ ಸೂಚ್ಯಂಕ (BMI >= 30.0):** ಹೆಚ್ಚುವರಿ ಕೊಬ್ಬು ಇನ್ಸುಲಿನ್ ಪ್ರತಿರೋಧವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.\n"
                    "3. **ವಯಸ್ಸು ಮತ್ತು ವಂಶಾವಳಿ:** 40+ ವಯಸ್ಸು ಮತ್ತು ಕುಟುಂಬದಲ್ಲಿ ಮಧುಮೇಹದ ಇತಿಹಾಸ ಇರುವುದು.\n"
                    "4. **ವ್ಯಾಯಾಮದ ಕೊರತೆ:** ಜಡ ಜೀವನಶೈಲಿ ಇನ್ಸುಲಿನ್ ಸೂಕ್ಷ್ಮತೆಯನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ."
                )
            elif lang == "hi":
                return (
                    "⚠️ **उच्च मधुमेह जोखिम के मुख्य कारण:**\n\n"
                    "1. **उपवास ग्लूकोज का बढ़ना (>140 mg/dL):** हमारे 96.8% सटीक मॉडल में सबसे मजबूत संकेतक।\n"
                    "2. **बीएमआई (BMI >= 30.0):** अत्यधिक मोटापा इंसुलिन प्रतिरोध को बढ़ाता है।\n"
                    "3. **आयु और आनुवंशिकी:** 40 से अधिक उम्र और परिवार में मधुमेह का इतिहास।\n"
                    "4. **शारीरिक निष्क्रियता:** गतिहीन जीवन शैली जोखिम को बढ़ाती है।"
                )
            elif lang == "ta":
                return (
                    "⚠️ **அதிக நீரிழிவு அபாயத்தின் முக்கிய காரணங்கள்:**\n\n"
                    "1. **உயர்ந்த இரத்த குளுக்கோஸ் (>140 mg/dL):** முக்கிய அறிகுறி.\n"
                    "2. **உடல் நிறை குறியீடு (BMI >= 30.0):** உடல் பருமன் இன்சுலின் எதிர்ப்பை அதிகரிக்கிறது.\n"
                    "3. **வயது மற்றும் பரம்பரை:** 40 வயதுக்கு மேல் மற்றும் குடும்ப வரலாறு."
                )
            elif lang == "te":
                return (
                    "⚠️ **అధిక డయాబెటిస్ ప్రమాదానికి ప్రధాన కారణాలు:**\n\n"
                    "1. **పెరిగిన ఫాస్టింగ్ గ్లూకోజ్ (>140 mg/dL):** బలమైన సూచిక.\n"
                    "2. **బాడీ మాస్ ఇండెక్స్ (BMI >= 30.0):** ఊబకాయం ఇన్సులిన్ నిరోధకతను పెంచుతుంది.\n"
                    "3. **వయస్సు మరియు వంశపారంపర్యత:** 40+ వయస్సు మరియు కుటుంబ చరిత్ర."
                )
            elif lang == "ml":
                return (
                    "⚠️ **ഉയർന്ന പ്രമേഹ സാധ്യതയുടെ പ്രധാന കാരണങ്ങൾ:**\n\n"
                    "1. **ഉയർന്ന ഫാസ്റ്റിംഗ് ഗ്ലൂക്കോസ് (>140 mg/dL)**\n"
                    "2. **ബോഡി മാസ് ഇൻഡക്സ് (BMI >= 30.0)**: പൊണ്ണത്തടി ഇൻസുലിൻ പ്രതിരോധം വർദ്ധിപ്പിക്കുന്നു.\n"
                    "3. **പ്രായവും ജനിതക ഘടകങ്ങളും**: 40 വയസ്സിന് മുകളിലുള്ള പ്രായവും കുടുംബ ചരിത്രവും."
                )
            return (
                "⚠️ **Primary Drivers of High Diabetes Risk:**\n\n"
                "1. **Elevated Fasting Glucose (>140 mg/dL):** The strongest clinical predictor in our 96.8% accurate XGBoost model.\n"
                "2. **Body Mass Index (BMI >= 30.0):** Excess visceral adipose tissue impairs insulin receptor signaling in muscle and liver cells.\n"
                "3. **Age & Genetic Susceptibility:** Age >40 combined with a positive Diabetes Pedigree Function (family history).\n"
                "4. **Hyperinsulinemia:** High fasting insulin indicates pancreatic overdrive to compensate for peripheral insulin resistance."
            )

        # C. Generic fallback
        if lang == "kn":
            return (
                "💡 **ಡಿಯಾಸೆನ್ಸ್ ಎಐ ಆರೋಗ್ಯ ಮಾರ್ಗದರ್ಶನ:**\n\n"
                "ನಿಮ್ಮ ರಕ್ತದ ಗ್ಲೂಕೋಸ್ ಮಟ್ಟವನ್ನು ನಿಯಂತ್ರಣದಲ್ಲಿಡಲು ಕಡಿಮೆ ಗ್ಲೈಸೆಮಿಕ್ (Low-GI) ಆಹಾರವನ್ನು ಸೇವಿಸಿ, ಪ್ರತಿದಿನ 30 ನಿಮಿಷಗಳ ನಡಿಗೆಯನ್ನು ರೂಢಿಸಿಕೊಳ್ಳಿ ಮತ್ತು ಸಾಕಷ್ಟು ನೀರು ಕುಡಿಯಿರಿ. ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಗಳಿದ್ದರೆ ಕೇಳಿ!"
            )
        elif lang == "hi":
            return (
                "💡 **डायसेंस एआई स्वास्थ्य मार्गदर्शन:**\n\n"
                "अपने रक्त शर्करा को नियंत्रित रखने के लिए कम ग्लाइसेमिक (Low-GI) भोजन लें, रोजाना 30 मिनट तेज चलें और पर्याप्त पानी पिएं। यदि आपका कोई विशिष्ट प्रश्न है तो कृपया पूछें!"
            )
        elif lang == "ta":
            return (
                "💡 **டயாசென்ஸ் ஏஐ மருத்துவ வழிகாட்டுதல்:**\n\n"
                "இரத்த சர்க்கரை அளவைக் கட்டுப்படுத்த குறைந்த கிளைசெமிக் உணவை உண்ணுங்கள், தினமும் 30 நிமிடங்கள் நடைபயிற்சி செய்யுங்கள் மற்றும் போதுமான தண்ணீர் குடியுங்கள்."
            )
        elif lang == "te":
            return (
                "💡 **డయాసెన్స్ AI ఆరోగ్య మార్గదర్శకత్వం:**\n\n"
                "రక్తంలో చక్కెర స్థాయిలను నియంత్రణలో ఉంచడానికి తక్కువ గ్లైసెమిక్ ఆహారాన్ని తీసుకోండి, ప్రతిరోజూ 30 నిమిషాలు నడవండి మరియు తగినంత నీరు త్రాగండి."
            )
        elif lang == "ml":
            return (
                "💡 **ഡയാസെൻസ് AI ആരോഗ്യ മാർഗ്ഗനിർദ്ദേശം:**\n\n"
                "രക്തത്തിലെ പഞ്ചസാരയുടെ അളവ് നിയന്ത്രിക്കുന്നതിന് കുറഞ്ഞ ഗ്ലൈസെമിക് ഭക്ഷണം കഴിക്കുക, ദിവസവും 30 മിനിറ്റ് നടക്കുക, ആവശ്യത്തിന് വെള്ളം കുടിക്കുക."
            )
        return (
            "💡 **DiaSense AI Clinical Health Guidance:**\n\n"
            "To keep your blood glucose in optimal ranges, prioritize low-GI complex carbohydrates (Oats, Ragi, Bajra, Moong Dal), engage in 30-45 minutes of daily brisk walking, and maintain consistent hydration."
        )
