import { useState, useEffect, useRef, useCallback } from "react";
import { useTranslation } from "../context/LanguageContext";
import { toast } from "react-toastify";

export function useVoiceAssistant() {
  const { currentLanguage, currentLangConfig, t } = useTranslation();
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);

  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  // Check browser capabilities
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechSupported(!!SpeechRecognition);

    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      synthRef.current = window.speechSynthesis;
      setTtsSupported(true);
    }
  }, []);

  // Initialize & configure SpeechRecognition whenever language changes
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) return;

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = currentLangConfig.voiceLang || "en-IN";

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event) => {
        let currentTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setTranscript(currentTranscript);
      };

      recognition.onerror = (event) => {
        setIsListening(false);
        if (event.error === "not-allowed") {
          toast.warn(t("voice.permissionDenied"));
        } else if (event.error !== "no-speech") {
          toast.info(`${t("voice.speechError")} (${event.error})`);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    } catch (err) {
      console.warn("SpeechRecognition initialization error:", err);
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch (e) {}
      }
    };
  }, [currentLanguage, currentLangConfig, t]);

  // Start Speech Recognition
  const startListening = useCallback(
    (onFinalTranscript) => {
      if (!speechSupported || !recognitionRef.current) {
        toast.info(t("voice.notSupported"));
        return;
      }

      setTranscript("");
      try {
        if (isSpeaking && synthRef.current) {
          synthRef.current.cancel();
          setIsSpeaking(false);
        }

        // Set callback for completion if provided
        if (onFinalTranscript) {
          recognitionRef.current.onresult = (event) => {
            let finalStr = "";
            let interimStr = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
              if (event.results[i].isFinal) {
                finalStr += event.results[i][0].transcript;
              } else {
                interimStr += event.results[i][0].transcript;
              }
            }
            const textToSet = finalStr || interimStr;
            setTranscript(textToSet);
            if (finalStr) {
              onFinalTranscript(finalStr);
            }
          };
        }

        recognitionRef.current.lang = currentLangConfig.voiceLang || "en-IN";
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        // Recognition already started or error
        setIsListening(false);
      }
    },
    [speechSupported, isSpeaking, currentLangConfig, t]
  );

  // Stop Speech Recognition
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsListening(false);
    }
  }, [isListening]);

  // Text-To-Speech (Speech Synthesis) in selected language
  const speak = useCallback(
    (textToSpeak) => {
      if (!ttsSupported || !synthRef.current || !textToSpeak) {
        if (!ttsSupported) toast.info(t("voice.ttsNotSupported"));
        return;
      }

      try {
        // Cancel any ongoing speech
        synthRef.current.cancel();

        // Strip markdown asterisks or code formatting for clear natural voice reading
        const cleanText = textToSpeak
          .replace(/\*\*(.*?)\*\*/g, "$1")
          .replace(/\*(.*?)\*/g, "$1")
          .replace(/#{1,6}\s?/g, "")
          .replace(/`{1,3}(.*?)`{1,3}/g, "$1")
          .replace(/\[(.*?)\]\(.*?\)/g, "$1")
          .trim();

        if (!cleanText) return;

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = currentLangConfig.voiceLang || "en-IN";
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        // Try selecting matching voice from available browser voices
        const voices = synthRef.current.getVoices();
        const langPrefix = currentLangConfig.voiceLang.split("-")[0].toLowerCase();

        // Match exact voiceLang (e.g. kn-IN, hi-IN, ta-IN, te-IN, ml-IN, en-IN) or prefix
        const matchedVoice =
          voices.find(
            (v) =>
              v.lang.toLowerCase() === currentLangConfig.voiceLang.toLowerCase()
          ) ||
          voices.find((v) =>
            v.lang.toLowerCase().startsWith(langPrefix)
          );

        if (matchedVoice) {
          utterance.voice = matchedVoice;
        }

        utterance.onstart = () => {
          setIsSpeaking(true);
        };

        utterance.onend = () => {
          setIsSpeaking(false);
        };

        utterance.onerror = () => {
          setIsSpeaking(false);
        };

        synthRef.current.speak(utterance);
      } catch (err) {
        console.warn("SpeechSynthesis error:", err);
        setIsSpeaking(false);
      }
    },
    [ttsSupported, currentLangConfig, t]
  );

  // Stop Text-to-Speech
  const stopSpeaking = useCallback(() => {
    if (synthRef.current && isSpeaking) {
      try {
        synthRef.current.cancel();
      } catch (e) {}
      setIsSpeaking(false);
    }
  }, [isSpeaking]);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSpeaking,
    speak,
    stopSpeaking,
    speechSupported,
    ttsSupported,
    activeVoiceLang: currentLangConfig.voiceLang,
    activeLanguageName: currentLangConfig.nativeName,
  };
}

export default useVoiceAssistant;
