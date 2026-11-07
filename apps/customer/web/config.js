/**
 * GaonBazaar Customer App Runtime Configuration
 * 
 * Admins can dynamically adjust serviceability limits and pilot coordinates
 * without modifying UI templates or compiled bundles.
 */
window.APP_CONFIG = {
  // Maximum delivery coverage radius from pilot fulfillment hub (in kilometers)
  MAX_DELIVERY_RADIUS_KM: 8.0,

  // Central pilot fulfillment hub coordinates (Minapur, Muzaffarpur, Bihar)
  HUB_LATITUDE: 26.2315,
  HUB_LONGITUDE: 85.3610,
  HUB_NAME: "Minapur Central Hub",

  // Pricing rules
  BASE_DELIVERY_FEE: 15.0,
  COD_SURCHARGE: 10.0,
  FREE_DELIVERY_THRESHOLD: 499.0,

  // Backend API Base Endpoint
  API_BASE_URL: "https://gaonbazaar-village.onrender.com/api/v1"
};
