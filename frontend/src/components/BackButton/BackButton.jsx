import "./BackButton.css";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "../../context/LanguageContext";

function BackButton() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div className="back-wrapper">
      <button
        className="back-btn"
        onClick={() => navigate(-1)}
      >
        ← {t("common.goBack")}
      </button>
    </div>
  );
}

export default BackButton;