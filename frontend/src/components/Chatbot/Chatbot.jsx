import "./Chatbot.css";
import { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import {
  FaRobot,
  FaTimes,
  FaPaperPlane,
  FaLightbulb,
  FaUser,
  FaHeartbeat,
  FaMicrophone,
  FaMicrophoneSlash,
  FaVolumeUp,
  FaVolumeMute,
} from "react-icons/fa";
import { chatbotService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";
import useVoiceAssistant from "../../hooks/useVoiceAssistant";

function Chatbot() {
  const location = useLocation();
  const { t, currentLangConfig } = useTranslation();
  const {
    isListening,
    startListening,
    stopListening,
    transcript,
    isSpeaking,
    speak,
    stopSpeaking,
    activeLanguageName,
  } = useVoiceAssistant();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMsg, setInputMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Initialize and update greeting on language switch if no custom convo yet
  useEffect(() => {
    setMessages((prev) => {
      if (prev.length <= 1) {
        return [
          {
            sender: "bot",
            text: `👋 ${t("chatbot.welcomeGreeting")}`,
            source: "DiaSense Healthcare Engine",
          },
        ];
      }
      return prev;
    });
  }, [currentLangConfig?.code, t]);

  // Dynamic suggestion chips translated
  const suggestionChips = [
    t("chatbot.chip1"),
    t("chatbot.chip2"),
    t("chatbot.chip3"),
    t("chatbot.chip4"),
    t("chatbot.chip5"),
  ];

  // Sync speech recognition transcript into inputMsg
  useEffect(() => {
    if (transcript) {
      setInputMsg(transcript);
    }
  }, [transcript]);

  // Restrict Chatbot widget visibility strictly to authenticated logged-in users
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("user");
    setIsLoggedIn(!!(token && savedUser));
  }, [location]);

  useEffect(() => {
    if (isOpen) {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  // If user is not logged in, hide AI chatbot completely
  if (!isLoggedIn) {
    return null;
  }

  const handleSend = async (textToSend) => {
    const text = textToSend || inputMsg;
    if (!text.trim() || loading) return;

    // Stop listening if user was speaking
    if (isListening) stopListening();

    // Append user message
    const userMessage = { sender: "user", text };
    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInputMsg("");
    setLoading(true);

    try {
      const response = await chatbotService.query(text, {
        language: currentLangConfig?.name || "English",
        code: currentLangConfig?.code || "en",
      });
      const botReply = response.data.reply;
      const source = response.data.source;

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: botReply, source },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: t("chatbot.errorGreeting"),
          source: t("chatbot.systemError"),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const toggleVoiceInput = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening((finalText) => {
        if (finalText && finalText.trim()) {
          setInputMsg(finalText);
        }
      });
    }
  };

  return (
    <div className="chatbot-floating-wrapper">
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          className="chatbot-toggle-btn"
          onClick={() => setIsOpen(true)}
          aria-label="Open DiaSense AI Assistant"
        >
          <FaRobot className="bot-icon" />
          <span className="btn-label">{t("common.appName")}</span>
          <span className="online-badge" />
        </button>
      )}

      {/* Floating Chat Window Panel */}
      {isOpen && (
        <div className="chatbot-window">
          {/* Header */}
          <div className="chatbot-header">
            <div className="header-title">
              <FaRobot className="bot-header-icon" />
              <div>
                <h4>{t("chatbot.headerTitle")}</h4>
                <p>
                  {t("chatbot.headerSubtitle")} • 🌐 {activeLanguageName}
                </p>
              </div>
            </div>
            <button
              className="close-btn"
              onClick={() => {
                if (isSpeaking) stopSpeaking();
                if (isListening) stopListening();
                setIsOpen(false);
              }}
            >
              <FaTimes />
            </button>
          </div>

          {/* Messages Stream */}
          <div className="chatbot-body">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`chat-bubble-row ${
                  msg.sender === "user" ? "user-row" : "bot-row"
                }`}
              >
                <div className="avatar">
                  {msg.sender === "user" ? <FaUser /> : <FaHeartbeat />}
                </div>
                <div className="bubble-content">
                  <div className="bubble-text">
                    {msg.text.split("\n").map((line, lIdx) => (
                      <p key={lIdx}>{line}</p>
                    ))}
                  </div>

                  <div className="bubble-footer-actions">
                    {msg.source && msg.sender === "bot" && (
                      <span className="source-tag">
                        {t("chatbot.poweredBy")} {msg.source}
                      </span>
                    )}

                    {/* Text-to-Speech Speak Button on Bot messages */}
                    {msg.sender === "bot" && (
                      <button
                        type="button"
                        className="voice-tts-btn"
                        onClick={() =>
                          isSpeaking ? stopSpeaking() : speak(msg.text)
                        }
                        title={
                          isSpeaking
                            ? t("chatbot.stopSpeaking")
                            : `${t("chatbot.speakResponse")} (${activeLanguageName})`
                        }
                      >
                        {isSpeaking ? <FaVolumeMute /> : <FaVolumeUp />}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-bubble-row bot-row">
                <div className="avatar">
                  <FaHeartbeat />
                </div>
                <div className="bubble-content">
                  <div className="typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}
            <div ref={chatBottomRef} />
          </div>

          {/* Suggestion Chips */}
          <div className="chatbot-chips-bar">
            <span className="chips-label">
              <FaLightbulb /> {t("chatbot.suggestionsLabel")}
            </span>
            <div className="chips-scroll">
              {suggestionChips.map((chip, cIdx) => (
                <button
                  key={cIdx}
                  className="chip-btn"
                  onClick={() => handleSend(chip)}
                  disabled={loading}
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>

          {/* Voice Listening Active Indicator Banner */}
          {isListening && (
            <div className="voice-listening-banner">
              <span className="listening-pulse-dot" />
              <span>
                {t("chatbot.listening")} <strong>{activeLanguageName}</strong>...
              </span>
            </div>
          )}

          {/* Input Box */}
          <div className="chatbot-footer">
            <input
              type="text"
              placeholder={
                isListening
                  ? `${t("voice.listening")} (${activeLanguageName})...`
                  : t("chatbot.placeholder")
              }
              value={inputMsg}
              onChange={(e) => setInputMsg(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />

            {/* Voice Input Microphone Button */}
            <button
              type="button"
              className={`mic-btn ${isListening ? "listening" : ""}`}
              onClick={toggleVoiceInput}
              title={
                isListening
                  ? t("chatbot.stopVoiceInput")
                  : `${t("chatbot.voiceInput")} (${activeLanguageName})`
              }
              disabled={loading}
            >
              {isListening ? <FaMicrophoneSlash /> : <FaMicrophone />}
            </button>

            <button
              type="button"
              className="send-btn"
              onClick={() => handleSend()}
              disabled={loading || !inputMsg.trim()}
            >
              <FaPaperPlane />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chatbot;
