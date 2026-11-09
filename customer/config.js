/**
 * GaonBazaar Customer App Runtime Configuration
 * 
 * Admins can dynamically adjust serviceability limits, pilot coordinates,
 * and auth / database parameters without modifying UI templates.
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

  // Firebase Configuration (SMS OTP Authentication)
  FIREBASE_CONFIG: {
    apiKey: "AIzaSyBVwI7wmdylF7499nrIGJKJP9Nvfj761xA",
    authDomain: "gaon-bazaar-village.firebaseapp.com",
    projectId: "gaon-bazaar-village",
    storageBucket: "gaon-bazaar-village.firebasestorage.app",
    messagingSenderId: "265333828276",
    appId: "1:265333828276:web:f2b9ae45032af552e785e1",
    measurementId: "G-F4E5161KN0"
  },

  // Supabase Configuration (Primary Relational Database)
  SUPABASE_URL: "https://vxewgvrjhjpntfvsmuez.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ4ZXdndnJqaGpwbnRmdnNtdWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTM1NDkwMzcsImV4cCI6MjEwOTEyNTAzN30.3jUR0U9RGcgc2q-zeWX7OeWaFqugSHOFdDieYoGFIwQ",

  // Cashfree SecureID Test API Configuration (Paperless KYC)
  CASHFREE_CLIENT_ID: "CF11351373DBOMC8KHUJMC73EBPFLG",
  CASHFREE_CLIENT_SECRET: (typeof atob !== "undefined") ? atob("Y2Zza19tYV90ZXN0XzI1YTEzMDBmN2MxZTZlZTM5MzA5NDhhZjMyYTRkMDM3X2NlNzA1Yjhi") : "",
  CASHFREE_BASE_URL: "https://sandbox.cashfree.com/verification",

  // Backend API Base Endpoint
  API_BASE_URL: "https://gaonbazaar-village.onrender.com/api/v1"
};
