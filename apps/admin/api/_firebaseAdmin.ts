import admin from 'firebase-admin';

export function getFirebaseAdmin(): typeof admin {
  if (admin.apps.length > 0) {
    return admin;
  }

  const projectId = process.env.FIREBASE_PROJECT_ID || 'gaon-bazaar-village';
  const serviceAccountEnv = process.env.FIREBASE_SERVICE_ACCOUNT;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY
    ? process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, '\n')
    : undefined;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;

  if (serviceAccountEnv) {
    try {
      const creds = typeof serviceAccountEnv === 'string' ? JSON.parse(serviceAccountEnv) : serviceAccountEnv;
      admin.initializeApp({
        credential: admin.credential.cert(creds),
        projectId: creds.project_id || projectId,
      });
      console.log('[Firebase Admin] Initialized with FIREBASE_SERVICE_ACCOUNT');
      return admin;
    } catch (e) {
      console.error('[Firebase Admin] Error parsing FIREBASE_SERVICE_ACCOUNT:', e);
    }
  }

  if (privateKey && clientEmail) {
    try {
      admin.initializeApp({
        credential: admin.credential.cert({
          projectId,
          clientEmail,
          privateKey,
        }),
        projectId,
      });
      console.log('[Firebase Admin] Initialized with privateKey and clientEmail');
      return admin;
    } catch (e) {
      console.error('[Firebase Admin] Error initializing with privateKey:', e);
    }
  }

  // Initialize with application default or projectId
  try {
    admin.initializeApp({
      projectId,
    });
    console.log('[Firebase Admin] Initialized with project ID fallback');
  } catch (e) {
    console.warn('[Firebase Admin] Default initialization warning:', e);
  }

  return admin;
}

export default admin;
