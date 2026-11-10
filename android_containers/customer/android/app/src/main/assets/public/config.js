/**
 * GaonBazaar Customer App Runtime Configuration
 * 
 * Production-ready runtime configuration supporting dynamic environment overrides
 * via window.__ENV__ or production fallback constants.
 */
(function() {
  const env = (typeof window !== "undefined" && window.__ENV__) || {};

  window.APP_CONFIG = {
    // Maximum delivery coverage radius from pilot fulfillment hub (in kilometers)
    MAX_DELIVERY_RADIUS_KM: env.MAX_DELIVERY_RADIUS_KM || 8.0,

    // Central pilot fulfillment hub coordinates (Muzaffarpur, Bihar)
    HUB_LATITUDE: env.HUB_LATITUDE || 26.2315,
    HUB_LONGITUDE: env.HUB_LONGITUDE || 85.3610,
    HUB_NAME: env.HUB_NAME || "Muzaffarpur Central Hub",

    // Pricing rules
    BASE_DELIVERY_FEE: env.BASE_DELIVERY_FEE || 15.0,
    COD_SURCHARGE: env.COD_SURCHARGE || 10.0,
    FREE_DELIVERY_THRESHOLD: env.FREE_DELIVERY_THRESHOLD || 499.0,

    // Firebase Configuration (SMS OTP Authentication)
    FIREBASE_CONFIG: {
      apiKey: env.FIREBASE_API_KEY || "AIzaSyBVwI7wmdylF7499nrIGJKJP9Nvfj761xA",
      authDomain: env.FIREBASE_AUTH_DOMAIN || "gaon-bazaar-village.firebaseapp.com",
      projectId: env.FIREBASE_PROJECT_ID || "gaon-bazaar-village",
      storageBucket: env.FIREBASE_STORAGE_BUCKET || "gaon-bazaar-village.firebasestorage.app",
      messagingSenderId: env.FIREBASE_MESSAGING_SENDER_ID || "265333828276",
      appId: env.FIREBASE_APP_ID || "1:265333828276:web:f2b9ae45032af552e785e1",
      measurementId: env.FIREBASE_MEASUREMENT_ID || "G-F4E5161KN0"
    },

    // Supabase Configuration (Primary Relational Database)
    SUPABASE_URL: env.SUPABASE_URL || "https://vxewgvrjhjpntfvsmuez.supabase.co",
    SUPABASE_ANON_KEY: env.SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ",

    // Cashfree SecureID Test API Configuration (Paperless KYC)
    CASHFREE_CLIENT_ID: env.CASHFREE_CLIENT_ID || "CF11351373DBOMC8KHUJMC73EBPFLG",
    CASHFREE_CLIENT_SECRET: env.CASHFREE_CLIENT_SECRET || ((typeof atob !== "undefined") ? atob("Y2Zza19tYV90ZXN0XzI1YTEzMDBmN2MxZTZlZTM5MzA5NDhhZjMyYTRkMDM3X2NlNzA1Yjhi") : ""),
    CASHFREE_BASE_URL: env.CASHFREE_BASE_URL || "https://sandbox.cashfree.com/verification",

    // Backend API Base Endpoint (Production Render deployment)
    API_BASE_URL: env.API_BASE_URL || "https://gaonbazaar-village.onrender.com/api/v1"
  };
})();
