import "./FindCare.css";
import { useState } from "react";
import { toast } from "react-toastify";
import Navbar from "../../components/Navbar/Navbar";
import BackButton from "../../components/BackButton/BackButton";
import Footer from "../../components/Footer/Footer";
import {
  FaHospital,
  FaVial,
  FaMapMarkerAlt,
  FaSearch,
  FaLocationArrow,
  FaDirections,
  FaPhone,
  FaStar,
  FaExclamationTriangle,
  FaCheckCircle,
  FaSpinner,
  FaMapMarkedAlt,
  FaList,
  FaClock,
  FaCompass,
  FaInfoCircle,
} from "react-icons/fa";
import { nearbyCareService } from "../../services/api";
import { useTranslation } from "../../context/LanguageContext";

const RADIUS_OPTIONS = [
  { label: "2 km", value: 2000 },
  { label: "5 km", value: 5000 },
  { label: "10 km", value: 10000 },
  { label: "20 km", value: 20000 },
];

function FindCare() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState("hospital"); // 'hospital' | 'laboratory'
  const [radius, setRadius] = useState(5000); // 5000 meters = 5 km default
  const [viewMode, setViewMode] = useState("list"); // 'list' | 'map'

  // Location state
  const [location, setLocation] = useState(null); // { lat, lng, name }
  const [locationStatus, setLocationStatus] = useState("idle"); // 'idle' | 'locating' | 'success' | 'error'
  const [locationError, setLocationError] = useState("");
  const [manualQuery, setManualQuery] = useState("");

  // Results state
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchedOnce, setSearchedOnce] = useState(false);
  const [selectedFacility, setSelectedFacility] = useState(null);

  // Request user's current GPS location
  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      const err = "Geolocation is not supported by your browser.";
      setLocationStatus("error");
      setLocationError(err);
      toast.error(err);
      return;
    }

    setLocationStatus("locating");
    setLocationError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          name: "Current GPS Location",
        };
        setLocation(coords);
        setLocationStatus("success");
        setLocationError("");
        toast.success("📍 Location detected successfully!");
        fetchFacilities(coords.lat, coords.lng, activeTab, radius, "Current Location");
      },
      (err) => {
        setLocationStatus("error");
        let msg = "We couldn't determine your current location. Please try again or search manually.";
        if (err.code === 1) {
          msg = t("findCare.permissionDenied");
        } else if (err.code === 2) {
          msg = t("findCare.locationUnavailable");
        } else if (err.code === 3) {
          msg = t("findCare.locationTimeout");
        }
        setLocationError(msg);
        toast.warn(msg);
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 }
    );
  };

  // Manual search by city / locality / pincode
  const handleManualSearch = async (e) => {
    if (e) e.preventDefault();
    if (!manualQuery.trim()) {
      toast.error("Please enter a city, area, or PIN code.");
      return;
    }

    setLocationStatus("locating");
    setLocationError("");
    setLoading(true);

    try {
      const res = await nearbyCareService.geocodeLocation(manualQuery.trim());
      if (res && res.data) {
        const coords = {
          lat: res.data.latitude,
          lng: res.data.longitude,
          name: res.data.display_name,
        };
        setLocation(coords);
        setLocationStatus("success");
        setLocationError("");
        toast.success(`📍 Found location: ${res.data.city || res.data.display_name.split(",")[0]}`);
        fetchFacilities(coords.lat, coords.lng, activeTab, radius, res.data.display_name);
      }
    } catch (err) {
      setLocationStatus("error");
      const msg = err.message || `Unable to locate "${manualQuery}". Please try another city or PIN code.`;
      setLocationError(msg);
      toast.error(msg);
      setLoading(false);
    }
  };

  // Fetch facilities from backend
  const fetchFacilities = async (lat, lng, type, rad, locName) => {
    setLoading(true);
    setSearchedOnce(true);
    try {
      const response = await nearbyCareService.getNearbyCare({
        latitude: lat,
        longitude: lng,
        type: type,
        radius: rad,
      });

      if (response && response.data && response.data.facilities) {
        setFacilities(response.data.facilities);
        if (response.data.facilities.length > 0) {
          setSelectedFacility(response.data.facilities[0]);
        }
      } else {
        setFacilities([]);
      }
    } catch (err) {
      toast.error(err.message || "Unable to find nearby healthcare facilities right now. Please try again.");
      setFacilities([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle Tab Switch
  const handleTabChange = (newTab) => {
    setActiveTab(newTab);
    if (location) {
      fetchFacilities(location.lat, location.lng, newTab, radius, location.name);
    }
  };

  // Handle Radius Change
  const handleRadiusChange = (newRadius) => {
    setRadius(newRadius);
    if (location) {
      fetchFacilities(location.lat, location.lng, activeTab, newRadius, location.name);
    }
  };

  // Increase radius for empty state
  const handleIncreaseRadius = () => {
    let nextRadius = 10000;
    if (radius === 2000) nextRadius = 5000;
    else if (radius === 5000) nextRadius = 10000;
    else if (radius === 10000) nextRadius = 20000;
    else nextRadius = 50000;

    setRadius(nextRadius);
    if (location) {
      fetchFacilities(location.lat, location.lng, activeTab, nextRadius, location.name);
    }
  };

  return (
    <>
      <Navbar />

      <div className="find-care-page">
        <div className="find-care-container">
          <BackButton />

          {/* Hero Header */}
          <div className="find-care-header text-center">
            <span className="badge-pill">
              <FaMapMarkerAlt /> {t("findCare.headerBadge")}
            </span>
            <h1>{t("findCare.headerTitle")}</h1>
            <p>{t("findCare.headerDesc")}</p>
          </div>

          {/* Location Action Card */}
          <div className="location-card">
            <div className="location-card-header">
              <div className="location-icon-title">
                <div className="loc-pin-icon">
                  <FaCompass />
                </div>
                <div>
                  <h2>{t("findCare.yourLocation")}</h2>
                  <p className="card-subtext">{t("findCare.locationSubtext")}</p>
                </div>
              </div>

              {locationStatus === "success" && (
                <div className="location-status-badge success">
                  <FaCheckCircle /> {t("findCare.locationDetected")}:{" "}
                  <strong>
                    {location?.name?.length > 35
                      ? location.name.slice(0, 35) + "..."
                      : location?.name}
                  </strong>
                </div>
              )}
            </div>

            <div className="location-inputs-grid">
              {/* GPS Button */}
              <button
                type="button"
                className="btn-use-location"
                onClick={handleUseCurrentLocation}
                disabled={locationStatus === "locating" || loading}
              >
                {locationStatus === "locating" ? (
                  <>
                    <FaSpinner className="spin-icon" /> {t("findCare.obtainingGps")}
                  </>
                ) : (
                  <>
                    <FaLocationArrow /> {t("findCare.useGpsBtn")}
                  </>
                )}
              </button>

              <div className="divider-text">{t("findCare.or")}</div>

              {/* Manual Form */}
              <form onSubmit={handleManualSearch} className="manual-location-form">
                <div className="input-with-button">
                  <input
                    type="text"
                    placeholder={t("findCare.searchPlaceholder")}
                    value={manualQuery}
                    onChange={(e) => setManualQuery(e.target.value)}
                  />
                  <button type="submit" className="btn-search-manual" disabled={loading}>
                    {loading && locationStatus === "locating" ? (
                      <FaSpinner className="spin-icon" />
                    ) : (
                      <>
                        <FaSearch /> {t("findCare.searchBtn")}
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Error Message Box */}
            {locationStatus === "error" && locationError && (
              <div className="location-error-banner">
                <FaExclamationTriangle className="err-icon" />
                <div>
                  <strong>{t("findCare.locationNotice")}: </strong>
                  <span>{locationError}</span>
                </div>
              </div>
            )}
          </div>

          {/* Facility Type Switcher & Controls */}
          <div className="care-controls-bar">
            {/* Primary Tabs */}
            <div className="facility-tabs">
              <button
                className={`tab-item ${activeTab === "hospital" ? "active" : ""}`}
                onClick={() => handleTabChange("hospital")}
              >
                <FaHospital /> 🏥 {t("findCare.hospitalsTab")}
              </button>
              <button
                className={`tab-item ${activeTab === "laboratory" ? "active" : ""}`}
                onClick={() => handleTabChange("laboratory")}
              >
                <FaVial /> 🧪 {t("findCare.labsTab")}
              </button>
            </div>

            {/* Radius & View Selector */}
            <div className="controls-right">
              <div className="radius-selector">
                <span className="ctrl-label">{t("findCare.radiusLabel")}</span>
                <div className="radius-chips">
                  {RADIUS_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      className={`chip-btn ${radius === opt.value ? "active" : ""}`}
                      onClick={() => handleRadiusChange(opt.value)}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="view-toggle">
                <button
                  className={`view-btn ${viewMode === "list" ? "active" : ""}`}
                  onClick={() => setViewMode("list")}
                  title="List View"
                >
                  <FaList /> {t("findCare.listView")}
                </button>
                <button
                  className={`view-btn ${viewMode === "map" ? "active" : ""}`}
                  onClick={() => setViewMode("map")}
                  title="Map View"
                >
                  <FaMapMarkedAlt /> {t("findCare.mapView")}
                </button>
              </div>
            </div>
          </div>

          {/* Diagnostic Labs Informational Note */}
          {activeTab === "laboratory" && (
            <div className="lab-info-banner">
              <FaInfoCircle className="info-icon" />
              <div>
                <strong>{t("findCare.labNoteTitle")}</strong> {t("findCare.labNoteDesc")}
              </div>
            </div>
          )}

          {/* Results Area */}
          <div className="results-container">
            {/* Loading State */}
            {loading && (
              <div className="loading-state-card">
                <FaSpinner className="spin-icon-large" />
                <h3>{t("findCare.findingCare")}</h3>
                <p>Querying real medical facilities within {radius / 1000} km radius.</p>
              </div>
            )}

            {/* Prompt to set location */}
            {!loading && !location && !searchedOnce && (
              <div className="initial-prompt-card">
                <div className="prompt-icon">
                  <FaCompass />
                </div>
                <h3>{t("findCare.readyPrompt")}</h3>
                <p>{t("findCare.readyDesc")}</p>
              </div>
            )}

            {/* Empty State */}
            {!loading && location && facilities.length === 0 && (
              <div className="empty-state-card">
                <div className="empty-icon">
                  <FaExclamationTriangle />
                </div>
                <h3>{t("findCare.noResults")} {radius / 1000} km</h3>
                <p>
                  We couldn't locate any {activeTab === "hospital" ? "hospitals or clinics" : "diagnostic laboratories"} registered in OpenStreetMap within the selected radius.
                </p>
                <button className="btn-increase-radius" onClick={handleIncreaseRadius}>
                  <FaSearch /> {t("findCare.expandRadius")} to {radius < 10000 ? "10 km" : "20 km"}
                </button>
              </div>
            )}

            {/* Results Header */}
            {!loading && facilities.length > 0 && (
              <div className="results-summary-bar">
                <span className="count-badge">
                  Found <strong>{facilities.length}</strong> {activeTab === "hospital" ? t("findCare.hospitalsTab") : t("findCare.labsTab")}
                </span>
                <span className="radius-indicator">
                  Sorted by nearest distance within {radius / 1000} km
                </span>
              </div>
            )}

            {/* View Mode 1: List View */}
            {!loading && facilities.length > 0 && viewMode === "list" && (
              <div className="facilities-grid">
                {facilities.map((fac) => (
                  <div key={fac.id} className="facility-card">
                    <div className="card-top-row">
                      <div className="fac-icon-wrapper">
                        {fac.category === "laboratory" ? <FaVial /> : <FaHospital />}
                      </div>
                      <div className="fac-title-area">
                        <span className="fac-type-pill">{fac.type}</span>
                        <h3>{fac.name}</h3>
                      </div>
                    </div>

                    <div className="fac-details">
                      <p className="fac-address">
                        <FaMapMarkerAlt className="detail-icon" />
                        <span>{fac.address}</span>
                      </p>

                      <div className="fac-meta-row">
                        <div className="meta-item distance">
                          <FaLocationArrow />
                          <strong>{fac.distance} km</strong> {t("findCare.distanceAway")}
                        </div>

                        {fac.open_now !== null && fac.open_now !== undefined && (
                          <div className={`meta-item status ${fac.open_now ? "open" : "closed"}`}>
                            <FaClock />
                            <span>{fac.open_now ? t("findCare.openNow") : t("findCare.closed")}</span>
                          </div>
                        )}

                        {fac.rating && (
                          <div className="meta-item rating">
                            <FaStar />
                            <span>{fac.rating.toFixed(1)}</span>
                          </div>
                        )}
                      </div>

                      {fac.phone && (
                        <p className="fac-phone">
                          <FaPhone className="detail-icon" />
                          <a href={`tel:${fac.phone}`}>{fac.phone}</a>
                        </p>
                      )}
                    </div>

                    <div className="card-actions">
                      <a
                        href={fac.mapsUrl || `https://www.google.com/maps/dir/?api=1&destination=${fac.latitude},${fac.longitude}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-directions"
                      >
                        <FaDirections /> {t("common.getDirections")}
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* View Mode 2: Interactive Map View */}
            {!loading && facilities.length > 0 && viewMode === "map" && (
              <div className="map-view-layout">
                {/* Facilities Sidebar on Desktop */}
                <div className="map-sidebar">
                  <h3>{t("findCare.facilitiesList")} ({facilities.length})</h3>
                  <div className="map-sidebar-list">
                    {facilities.map((fac) => (
                      <div
                        key={fac.id}
                        className={`map-sidebar-item ${selectedFacility?.id === fac.id ? "active" : ""}`}
                        onClick={() => setSelectedFacility(fac)}
                      >
                        <div className="sidebar-item-header">
                          <strong>{fac.name}</strong>
                          <span className="dist-tag">{fac.distance} km</span>
                        </div>
                        <p className="sidebar-address">{fac.address}</p>
                        <a
                          href={fac.mapsUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="sidebar-dir-link"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <FaDirections /> {t("common.getDirections")}
                        </a>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Map Display Card */}
                <div className="map-display-card">
                  {selectedFacility && (
                    <div className="map-selected-preview">
                      <div className="preview-header">
                        <div>
                          <span className="fac-type-pill">{selectedFacility.type}</span>
                          <h4>{selectedFacility.name}</h4>
                          <p className="prev-address">{selectedFacility.address}</p>
                        </div>
                        <div className="prev-dist">
                          <strong>{selectedFacility.distance} km</strong>
                        </div>
                      </div>
                      <div className="preview-action-row">
                        <a
                          href={selectedFacility.mapsUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-directions-sm"
                        >
                          <FaDirections /> {t("common.openGoogleMaps")}
                        </a>
                      </div>
                    </div>
                  )}

                  {/* OpenStreetMap Interactive Embed */}
                  <div className="map-iframe-wrapper">
                    {location && (
                      <iframe
                        title="Healthcare Facilities Map"
                        width="100%"
                        height="480"
                        frameBorder="0"
                        scrolling="no"
                        marginHeight="0"
                        marginWidth="0"
                        src={`https://www.openstreetmap.org/export/embed.html?bbox=${(selectedFacility?.longitude || location.lng) - 0.03}%2C${(selectedFacility?.latitude || location.lat) - 0.02}%2C${(selectedFacility?.longitude || location.lng) + 0.03}%2C${(selectedFacility?.latitude || location.lat) + 0.02}&layer=mapnik&marker=${selectedFacility?.latitude || location.lat}%2C${selectedFacility?.longitude || location.lng}`}
                      ></iframe>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Medical Legal Disclaimer */}
          <div className="find-care-disclaimer">
            <h4>
              <FaInfoCircle /> {t("common.disclaimerTitle")}
            </h4>
            <p>{t("common.disclaimerText")}</p>
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}

export default FindCare;
