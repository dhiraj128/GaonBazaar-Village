import { useState } from 'react';
import { adminApi } from '../api';

interface LoginViewProps {
  onLoginSuccess: () => void;
}

export function LoginView({ onLoginSuccess }: LoginViewProps) {
  const [phone, setPhone] = useState('');
  const [secretOrOtp, setSecretOrOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const result = await adminApi.login(phone, secretOrOtp);
      if (result.success) {
        onLoginSuccess();
      } else {
        setError(result.error || 'Authentication failed. Please verify admin credentials.');
      }
    } catch (err: any) {
      setError(err?.message || 'Unable to connect to administrative services. Please check your network connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#F3F4F6',
      padding: '1.5rem',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif'
    }}>
      <div style={{
        maxWidth: '420px',
        width: '100%',
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden'
      }}>
        {/* Header Header Banner */}
        <div style={{
          backgroundColor: '#15803D',
          padding: '2rem 1.5rem',
          textAlign: 'center',
          color: '#FFFFFF'
        }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '48px',
            height: '48px',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            marginBottom: '0.75rem',
            fontSize: '1.5rem'
          }}>
            🛒
          </div>
          <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.025em' }}>
            GaonBazaar Super Admin
          </h1>
          <p style={{ margin: '0.35rem 0 0', fontSize: '0.875rem', opacity: 0.9 }}>
            ग्रामीण हाइपरलोकल प्रबंधन पोर्टल — मीनापुर (Minapur Pilot)
          </p>
        </div>

        {/* Body Form */}
        <div style={{ padding: '2rem 1.5rem' }}>
          {error && (
            <div style={{
              backgroundColor: '#FEF2F2',
              border: '1px solid #FCA5A5',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: '#991B1B',
              fontSize: '0.875rem',
              marginBottom: '1.25rem'
            }}>
              <strong>ত্রুটি / Error:</strong> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                एडमिन मोबाइल नंबर (Admin Mobile Number)
              </label>
              <div style={{ position: 'relative' }}>
                <span style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: '#6B7280',
                  fontSize: '0.875rem',
                  fontWeight: 500
                }}>
                  +91
                </span>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="9800000099"
                  required
                  style={{
                    width: '100%',
                    padding: '0.625rem 0.75rem 0.625rem 48px',
                    borderRadius: '8px',
                    border: '1px solid #D1D5DB',
                    fontSize: '0.95rem',
                    boxSizing: 'border-box',
                    outline: 'none',
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.35rem' }}>
                मास्टर की या ओटीपी (Master Key or OTP)
              </label>
              <input
                type="password"
                value={secretOrOtp}
                onChange={(e) => setSecretOrOtp(e.target.value)}
                placeholder="Enter Admin Secret Key or Authorized OTP"
                required
                style={{
                  width: '100%',
                  padding: '0.625rem 0.75rem',
                  borderRadius: '8px',
                  border: '1px solid #D1D5DB',
                  fontSize: '0.95rem',
                  boxSizing: 'border-box',
                  outline: 'none',
                }}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              style={{
                width: '100%',
                backgroundColor: '#15803D',
                color: '#FFFFFF',
                padding: '0.75rem',
                borderRadius: '8px',
                border: 'none',
                fontWeight: 600,
                fontSize: '0.95rem',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                opacity: isLoading ? 0.7 : 1,
                transition: 'background-color 0.15s ease',
                marginTop: '0.5rem'
              }}
            >
              {isLoading ? 'सत्यापन जारी है (Verifying...)' : 'लॉग इन करें (Sign In)'}
            </button>
          </form>
        </div>

        {/* Footer Security Badge */}
        <div style={{
          backgroundColor: '#F9FAFB',
          padding: '0.75rem 1.5rem',
          borderTop: '1px solid #F3F4F6',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: '#6B7280'
        }}>
          🔒 256-bit Encrypted • Official GaonBazaar Operations Portal
        </div>
      </div>
    </div>
  );
}
