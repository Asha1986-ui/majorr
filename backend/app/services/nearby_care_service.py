import math
import os
import re
from typing import Dict, Any, List, Optional, Tuple
import httpx

from app.config.settings import settings
from app.schemas.nearby_care_schema import (
    NearbyFacilityItem,
    NearbyCareListResponse,
    GeocodeResult,
)
from app.utils.logger import logger


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) using Haversine formula.
    Returns distance in kilometers rounded to 2 decimal places.
    """
    R = 6371.0  # Earth radius in kilometers

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 2)


class NearbyCareService:
    """
    Service responsible for querying real healthcare facilities (Hospitals, Clinics, Diagnostic Labs)
    near a given user location using OpenStreetMap Overpass API, Nominatim Geocoder, and optional Google Places API.
    """

    OVERPASS_ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]

    NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
    USER_AGENT = "DiaSenseAI-HealthcarePlatform/1.0 (contact@diasense.ai)"

    def __init__(self):
        self.google_api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", "").strip() or os.getenv(
            "GOOGLE_PLACES_API_KEY", ""
        ).strip()

    KNOWN_INDIAN_PIN_CLUSTERS = {
        "560049": (13.0163, 77.7056, "560049 (Bhattarahalli / Virgonagar, Bangalore East, Bengaluru)"),
        "560001": (12.9716, 77.5946, "560001 (MG Road / Central Bangalore, Bengaluru)"),
        "560034": (12.9279, 77.6271, "560034 (Koramangala, Bengaluru)"),
        "560037": (12.9698, 77.7500, "560037 (Marathahalli / Whitefield, Bengaluru)"),
        "560066": (12.9698, 77.7500, "560066 (Whitefield, Bengaluru)"),
        "560076": (12.8996, 77.6101, "560076 (BTM Layout / Bannerghatta Road, Bengaluru)"),
        "560100": (12.8452, 77.6602, "560100 (Electronic City, Bengaluru)"),
        "560078": (12.9081, 77.5855, "560078 (JP Nagar, Bengaluru)"),
        "560085": (12.9250, 77.5467, "560085 (Banashankari, Bengaluru)"),
        "110001": (28.6139, 77.2090, "110001 (Connaught Place, New Delhi)"),
        "400001": (18.9388, 72.8354, "400001 (Fort / South Mumbai, Mumbai)"),
        "500001": (17.3850, 78.4867, "500001 (Abids / Central Hyderabad)"),
        "600001": (13.0827, 80.2707, "600001 (George Town, Chennai)"),
        "411001": (18.5204, 73.8567, "411001 (Shivajinagar / Camp, Pune)"),
        "570001": (12.2958, 76.6394, "570001 (Devaraja Market / Central Mysuru)"),
    }

    def geocode_location(self, query: str) -> Optional[GeocodeResult]:
        """
        Geocodes a user-entered location query (PIN code, City, Locality, Area)
        into latitude and longitude coordinates.
        Supports 6-digit Indian PIN codes, city names, and areas with multiple fallback tiers.
        """
        if not query or not query.strip():
            return None

        clean_query = query.strip()

        # 1. Check known PIN code cache for instant ultra-accurate match
        if clean_query in self.KNOWN_INDIAN_PIN_CLUSTERS:
            lat, lon, display = self.KNOWN_INDIAN_PIN_CLUSTERS[clean_query]
            return GeocodeResult(
                latitude=lat,
                longitude=lon,
                display_name=display,
                city="Bengaluru" if "560" in clean_query else "India",
                state="Karnataka" if "560" in clean_query or "570" in clean_query else "India",
                country="India",
            )

        headers = {"User-Agent": self.USER_AGENT}
        is_pin = bool(re.match(r"^\d{6}$", clean_query))

        # 2. If 6-digit PIN code, query Nominatim with structured postalcode + India
        if is_pin:
            try:
                params = {
                    "postalcode": clean_query,
                    "country": "India",
                    "format": "json",
                    "addressdetails": 1,
                    "limit": 1,
                }
                with httpx.Client(timeout=8.0) as client:
                    res = client.get(f"{self.NOMINATIM_BASE}/search", params=params, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        if data and len(data) > 0:
                            top = data[0]
                            addr = top.get("address", {})
                            city = (
                                addr.get("city")
                                or addr.get("town")
                                or addr.get("village")
                                or addr.get("city_district")
                                or addr.get("county")
                                or addr.get("state_district")
                            )
                            return GeocodeResult(
                                latitude=float(top["lat"]),
                                longitude=float(top["lon"]),
                                display_name=top.get("display_name", f"{clean_query}, India"),
                                city=city,
                                state=addr.get("state"),
                                country=addr.get("country", "India"),
                            )
            except Exception as e:
                logger.warning(f"Nominatim postal query error for '{clean_query}': {e}")

            # 2b. Indian Postal PIN API fallback (api.postalpincode.in)
            try:
                with httpx.Client(timeout=6.0) as client:
                    pin_res = client.get(f"https://api.postalpincode.in/pincode/{clean_query}")
                    if pin_res.status_code == 200:
                        pin_json = pin_res.json()
                        if pin_json and len(pin_json) > 0 and pin_json[0].get("Status") == "Success":
                            post_offices = pin_json[0].get("PostOffice", [])
                            if post_offices:
                                po = post_offices[0]
                                po_name = po.get("Name", "")
                                district = po.get("District", "")
                                state = po.get("State", "")
                                fallback_search = f"{po_name}, {district}, {state}, India" if po_name else f"{district}, {state}, India"

                                # Geocode the resolved district / place name
                                geo_res = client.get(
                                    f"{self.NOMINATIM_BASE}/search",
                                    params={"q": fallback_search, "format": "json", "limit": 1},
                                    headers=headers,
                                )
                                if geo_res.status_code == 200:
                                    gdata = geo_res.json()
                                    if gdata:
                                        return GeocodeResult(
                                            latitude=float(gdata[0]["lat"]),
                                            longitude=float(gdata[0]["lon"]),
                                            display_name=f"{clean_query} ({po_name}, {district}, {state})",
                                            city=district,
                                            state=state,
                                            country="India",
                                        )
            except Exception as e:
                logger.warning(f"India Postal API fallback error for '{clean_query}': {e}")

        # 3. Standard City / Locality Geocoding via Nominatim
        search_queries = [clean_query]
        if "india" not in clean_query.lower():
            search_queries.append(f"{clean_query}, India")

        for sq in search_queries:
            try:
                params = {
                    "q": sq,
                    "format": "json",
                    "addressdetails": 1,
                    "limit": 1,
                }
                with httpx.Client(timeout=8.0) as client:
                    res = client.get(f"{self.NOMINATIM_BASE}/search", params=params, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        if data and len(data) > 0:
                            top = data[0]
                            addr = top.get("address", {})
                            city = (
                                addr.get("city")
                                or addr.get("town")
                                or addr.get("village")
                                or addr.get("county")
                                or addr.get("state_district")
                            )
                            return GeocodeResult(
                                latitude=float(top["lat"]),
                                longitude=float(top["lon"]),
                                display_name=top.get("display_name", clean_query),
                                city=city,
                                state=addr.get("state"),
                                country=addr.get("country"),
                            )
            except Exception as e:
                logger.warning(f"Nominatim search error for '{sq}': {e}")

        # 4. PIN Prefix Cluster Fallback if external APIs are completely unreachable
        if is_pin and clean_query.startswith("560"):
            return GeocodeResult(
                latitude=12.9716,
                longitude=77.5946,
                display_name=f"Bengaluru ({clean_query}, Karnataka, India)",
                city="Bengaluru",
                state="Karnataka",
                country="India",
            )

        return None

    def get_nearby_facilities(
        self,
        latitude: float,
        longitude: float,
        facility_type: str = "hospital",
        radius_meters: int = 5000,
        location_name: Optional[str] = None,
    ) -> NearbyCareListResponse:
        """
        Fetch real healthcare facilities near (latitude, longitude) within radius_meters.
        facility_type must be either 'hospital' or 'laboratory'.
        """
        norm_type = "laboratory" if "lab" in facility_type.lower() else "hospital"
        radius = max(500, min(radius_meters, 50000))  # Cap radius between 500m and 50km

        facilities: List[NearbyFacilityItem] = []

        # 1. If Google Places API Key is provided, use Google Places
        if self.google_api_key:
            try:
                facilities = self._fetch_from_google_places(
                    latitude, longitude, norm_type, radius
                )
            except Exception as e:
                logger.warning(f"Google Places API fetch failed: {e}. Falling back to OpenStreetMap Overpass.")
                facilities = []

        # 2. If no Google Places or Google Places yielded no results, query OpenStreetMap Overpass
        if not facilities:
            facilities = self._fetch_from_overpass(latitude, longitude, norm_type, radius)

        # 3. If Overpass timed out or returned empty, attempt Nominatim POI search fallback
        if not facilities:
            facilities = self._fetch_from_nominatim_poi(latitude, longitude, norm_type, radius)

        # Calculate distances & sort strictly by nearest to farthest
        for fac in facilities:
            if fac.distance <= 0:
                fac.distance = calculate_haversine_distance(
                    latitude, longitude, fac.latitude, fac.longitude
                )

        # Remove duplicate IDs or identical coordinates/names
        unique_facilities: List[NearbyFacilityItem] = []
        seen_keys = set()
        for f in facilities:
            key = f"{round(f.latitude, 4)}_{round(f.longitude, 4)}_{f.name.lower()}"
            if key not in seen_keys:
                seen_keys.add(key)
                unique_facilities.append(f)

        # Sort by distance
        unique_facilities.sort(key=lambda x: x.distance)

        return NearbyCareListResponse(
            facilities=unique_facilities,
            total_count=len(unique_facilities),
            facility_type=norm_type,
            radius_meters=radius,
            center_lat=latitude,
            center_lng=longitude,
            location_name=location_name,
        )

    def _fetch_from_overpass(
        self, latitude: float, longitude: float, facility_type: str, radius: int
    ) -> List[NearbyFacilityItem]:
        """
        Queries OpenStreetMap Overpass API for real hospitals, clinics, or diagnostic laboratories.
        """
        if facility_type == "laboratory":
            query = f"""
            [out:json][timeout:10];
            (
              nwr["amenity"="laboratory"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="laboratory"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="blood_bank"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="pathology"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="sample_collection"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="medical_laboratory"](around:{radius},{latitude},{longitude});
              nwr["craft"="laboratory"](around:{radius},{latitude},{longitude});
              node["amenity"="clinic"](around:{radius},{latitude},{longitude})[name~"Diagnostic|Pathology|Lab|Thyrocare|Lal PathLabs|Metropolis|SRL|Blood",i];
              node["healthcare"](around:{radius},{latitude},{longitude})[name~"Diagnostic|Pathology|Lab|Thyrocare|Lal PathLabs|Metropolis|SRL|Blood",i];
            );
            out center tags;
            """
        else:
            query = f"""
            [out:json][timeout:15];
            (
              nwr["amenity"="hospital"](around:{radius},{latitude},{longitude});
              nwr["amenity"="clinic"](around:{radius},{latitude},{longitude});
              nwr["amenity"="doctors"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="hospital"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="clinic"](around:{radius},{latitude},{longitude});
              nwr["healthcare"="centre"](around:{radius},{latitude},{longitude});
            );
            out center tags;
            """

        headers = {"User-Agent": self.USER_AGENT}

        for endpoint in self.OVERPASS_ENDPOINTS:
            try:
                with httpx.Client(timeout=6.0) as client:
                    res = client.post(endpoint, data={"data": query}, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        elements = data.get("elements", [])
                        return self._parse_overpass_elements(
                            elements, latitude, longitude, facility_type
                        )
                    else:
                        logger.warning(
                            f"Overpass endpoint {endpoint} returned status {res.status_code}"
                        )
            except Exception as e:
                logger.warning(f"Overpass endpoint {endpoint} error: {e}. Trying next mirror...")

        return []

    def _parse_overpass_elements(
        self,
        elements: List[Dict[str, Any]],
        user_lat: float,
        user_lon: float,
        facility_type: str,
    ) -> List[NearbyFacilityItem]:
        results: List[NearbyFacilityItem] = []

        for el in elements:
            # Extract coordinates (node lat/lon or way/relation center)
            lat = el.get("lat")
            lon = el.get("lon")
            if lat is None or lon is None:
                center = el.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")

            if lat is None or lon is None:
                continue

            lat = float(lat)
            lon = float(lon)
            tags = el.get("tags", {})

            # Name extraction
            name = (
                tags.get("name")
                or tags.get("name:en")
                or tags.get("official_name")
                or tags.get("operator")
            )

            # Determine facility specific type
            amenity = tags.get("amenity", "")
            healthcare = tags.get("healthcare", "")

            specific_type = "Healthcare Facility"
            if facility_type == "laboratory":
                if any(x in (name or "").lower() for x in ["pathology", "path"]):
                    specific_type = "Pathology Laboratory"
                elif any(x in (name or "").lower() for x in ["diagnostic", "diagnostics"]):
                    specific_type = "Diagnostic Center"
                elif "blood" in (name or "").lower() or healthcare == "blood_bank":
                    specific_type = "Blood Testing Center"
                elif healthcare == "laboratory" or amenity == "laboratory":
                    specific_type = "Medical Diagnostic Laboratory"
                else:
                    specific_type = "Clinical Diagnostic Laboratory"
            else:
                if amenity == "hospital" or healthcare == "hospital":
                    specific_type = "Hospital"
                elif amenity == "clinic" or healthcare == "clinic":
                    specific_type = "Medical Clinic"
                elif amenity == "doctors":
                    specific_type = "Doctor's Medical Center"
                elif healthcare == "centre":
                    specific_type = "Health Care Centre"
                else:
                    specific_type = "Hospital / Medical Center"

            if not name:
                name = f"{specific_type} (Nearby)"

            # Construct clean address
            address_parts = []
            if tags.get("addr:housenumber"):
                address_parts.append(tags["addr:housenumber"])
            if tags.get("addr:street"):
                address_parts.append(tags["addr:street"])
            if tags.get("addr:suburb"):
                address_parts.append(tags["addr:suburb"])
            if tags.get("addr:district"):
                address_parts.append(tags["addr:district"])
            if tags.get("addr:city"):
                address_parts.append(tags["addr:city"])
            if tags.get("addr:postcode"):
                address_parts.append(tags["addr:postcode"])

            if address_parts:
                address = ", ".join(address_parts)
            elif tags.get("addr:full"):
                address = tags["addr:full"]
            else:
                # Fallback to general locality descriptor
                address = f"Near {round(lat, 3)}°N, {round(lon, 3)}°E"

            # Check 24/7 or opening hours
            opening_hours = tags.get("opening_hours", "")
            open_now = None
            if opening_hours:
                if "24/7" in opening_hours:
                    open_now = True

            # Contact
            phone = tags.get("phone") or tags.get("contact:phone") or tags.get("emergency:phone")
            website = tags.get("website") or tags.get("contact:website")

            dist = calculate_haversine_distance(user_lat, user_lon, lat, lon)
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}"

            results.append(
                NearbyFacilityItem(
                    id=f"osm_{el.get('type', 'node')}_{el.get('id', len(results)+1)}",
                    name=name,
                    type=specific_type,
                    category=facility_type,
                    address=address,
                    latitude=lat,
                    longitude=lon,
                    distance=dist,
                    distance_unit="km",
                    rating=None,  # OSM does not have verified reviews
                    open_now=open_now,
                    phone=phone,
                    website=website,
                    maps_url=maps_url,
                )
            )

        return results

    def _fetch_from_nominatim_poi(
        self, latitude: float, longitude: float, facility_type: str, radius: int
    ) -> List[NearbyFacilityItem]:
        """
        Fallback POI query using Nominatim when Overpass is busy.
        """
        results: List[NearbyFacilityItem] = []
        search_terms = (
            ["diagnostic laboratory", "pathology lab", "blood test lab"]
            if facility_type == "laboratory"
            else ["hospital", "clinic", "medical center"]
        )

        headers = {"User-Agent": self.USER_AGENT}
        for term in search_terms:
            try:
                params = {
                    "q": f"{term}",
                    "format": "json",
                    "addressdetails": 1,
                    "limit": 15,
                    "viewbox": f"{longitude - 0.08},{latitude + 0.08},{longitude + 0.08},{latitude - 0.08}",
                    "bounded": 1,
                }
                with httpx.Client(timeout=8.0) as client:
                    res = client.get(f"{self.NOMINATIM_BASE}/search", params=params, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        for item in data:
                            lat = float(item["lat"])
                            lon = float(item["lon"])
                            dist = calculate_haversine_distance(latitude, longitude, lat, lon)
                            if dist * 1000 <= radius * 1.3:  # Within radius margin
                                results.append(
                                    NearbyFacilityItem(
                                        id=f"nom_{item.get('place_id', len(results)+1)}",
                                        name=item.get("name") or item.get("display_name", "").split(",")[0],
                                        type="Diagnostic Laboratory" if facility_type == "laboratory" else "Hospital / Clinic",
                                        category=facility_type,
                                        address=item.get("display_name", "Local Address"),
                                        latitude=lat,
                                        longitude=lon,
                                        distance=dist,
                                        distance_unit="km",
                                        maps_url=f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}",
                                    )
                                )
            except Exception as e:
                logger.warning(f"Nominatim POI query error for '{term}': {e}")

        return results

    def _fetch_from_google_places(
        self, latitude: float, longitude: float, facility_type: str, radius: int
    ) -> List[NearbyFacilityItem]:
        """
        Queries Google Places Nearby Search API if GOOGLE_PLACES_API_KEY is configured.
        """
        results: List[NearbyFacilityItem] = []
        keyword = "diagnostic laboratory pathology blood test HbA1c" if facility_type == "laboratory" else "hospital clinic"
        g_type = "medical_lab" if facility_type == "laboratory" else "hospital"

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "keyword": keyword,
            "type": g_type,
            "key": self.google_api_key,
        }

        with httpx.Client(timeout=10.0) as client:
            res = client.get(url, params=params)
            if res.status_code == 200:
                data = res.json()
                places = data.get("results", [])
                for p in places:
                    geom = p.get("geometry", {}).get("location", {})
                    lat = geom.get("lat")
                    lng = geom.get("lng")
                    if lat is None or lng is None:
                        continue

                    dist = calculate_haversine_distance(latitude, longitude, lat, lng)
                    rating = p.get("rating")
                    open_now = p.get("opening_hours", {}).get("open_now")

                    results.append(
                        NearbyFacilityItem(
                            id=f"gplace_{p.get('place_id', len(results)+1)}",
                            name=p.get("name", "Healthcare Facility"),
                            type="Diagnostic Laboratory" if facility_type == "laboratory" else "Hospital",
                            category=facility_type,
                            address=p.get("vicinity", "Local Area"),
                            latitude=lat,
                            longitude=lng,
                            distance=dist,
                            distance_unit="km",
                            rating=float(rating) if rating is not None else None,
                            open_now=open_now,
                            maps_url=f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}",
                        )
                    )

        return results
