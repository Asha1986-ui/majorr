import "./Contact.css";
import { useState } from "react";
import { toast } from "react-toastify";
import { FaEnvelope, FaUser, FaPaperPlane, FaCommentAlt, FaCheckCircle, FaHeadset } from "react-icons/fa";

import Navbar from "../../components/Navbar/Navbar";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import { contactService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";

function Contact() {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.email.trim() || !formData.message.trim()) {
      toast.error(t("auth.fillRequiredFields"));
      return;
    }

    setLoading(true);
    try {
      await contactService.submitContact({
        name: formData.name,
        email: formData.email,
        subject: formData.subject || "DiaSense Inquiry",
        message: formData.message,
      });

      toast.success(`✅ ${t("contact.successToast")}`);
      setFormData({ name: "", email: "", subject: "", message: "" });
    } catch (err) {
      toast.error(err.message || t("contact.failedToast"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <div className="contact-page">
        <div className="contact-container">
          <BackButton />

          <div className="contact-grid">
            {/* Left Info Card */}
            <div className="contact-info-card">
              <div className="badge-pill"><FaHeadset /> {t("contact.badge")}</div>
              <h1>{t("contact.title")}</h1>
              <p>{t("contact.desc")}</p>

              <div className="info-points">
                <div className="info-point">
                  <FaCheckCircle className="info-icon" />
                  <div>
                    <h4>{t("contact.fastResponseTitle")}</h4>
                    <p>{t("contact.fastResponseDesc")}</p>
                  </div>
                </div>

                <div className="info-point">
                  <FaCheckCircle className="info-icon" />
                  <div>
                    <h4>{t("contact.academicSupportTitle")}</h4>
                    <p>{t("contact.academicSupportDesc")}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Contact Form */}
            <div className="contact-form-card">
              <h2>{t("contact.sendMessage")}</h2>

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label><FaUser /> {t("contact.nameLabel")} *</label>
                  <input
                    type="text"
                    placeholder={t("contact.namePlaceholder")}
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label><FaEnvelope /> {t("contact.emailLabel")} *</label>
                  <input
                    type="email"
                    placeholder={t("contact.emailPlaceholder")}
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                </div>

                <div className="form-group">
                  <label><FaCommentAlt /> {t("contact.subjectLabel")}</label>
                  <input
                    type="text"
                    placeholder={t("contact.subjectPlaceholder")}
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label><FaPaperPlane /> {t("contact.messageLabel")} *</label>
                  <textarea
                    rows="5"
                    placeholder={t("contact.messagePlaceholder")}
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    required
                  />
                </div>

                <button type="submit" className="submit-btn" disabled={loading}>
                  {loading ? t("contact.submittingBtn") : t("contact.submitBtn")}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}

export default Contact;