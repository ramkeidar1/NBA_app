import { useState } from 'react';
import { useNavigate } from 'react-router';
import AppShell from '../components/layout/AppShell';
import { register } from '../services/authService';
import { useAuthStore } from '../store/authStore';
import type { UserRole } from '../types/auth';

type Mode = 'signin' | 'signup';

const ROLE_OPTIONS: { value: UserRole; label: string }[] = [
  { value: 'viewer', label: 'Viewer' },
  { value: 'analyst', label: 'Analyst' },
  { value: 'admin', label: 'Admin' },
];

export default function LoginRoute() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const [mode, setMode] = useState<Mode>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('viewer');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function switchMode(next: Mode) {
    setMode(next);
    setError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === 'signup') {
        const { access_token } = await register({ email, password, role });
        useAuthStore.getState().setAccessToken(access_token);
      } else {
        await login(email, password);
      }
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  const isSignUp = mode === 'signup';

  return (
    <AppShell>
      <div className="login-body">
        <div className="login-card">

          {/* Card header — mirrors panel-header pattern */}
          <div className="login-card__header">
            <span className="login-card__title">Authentication</span>
            <div className="login-tabs">
              <button
                type="button"
                className={`login-tab${!isSignUp ? ' login-tab--active' : ''}`}
                onClick={() => switchMode('signin')}
              >
                Sign In
              </button>
              <button
                type="button"
                className={`login-tab${isSignUp ? ' login-tab--active' : ''}`}
                onClick={() => switchMode('signup')}
              >
                Sign Up
              </button>
            </div>
          </div>

          {/* Form body */}
          <form onSubmit={handleSubmit} className="login-card__body">
            {error && <p className="login-error">{error}</p>}

            <div className="login-field">
              <label className="login-label">Email</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="login-input"
              />
            </div>

            <div className="login-field">
              <label className="login-label">
                {isSignUp ? 'Password & Role' : 'Password'}
              </label>
              <div className="login-row">
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="login-input"
                  style={{ flex: 1 }}
                />
                {isSignUp && (
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value as UserRole)}
                    className="login-select"
                  >
                    {ROLE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </div>

            <div className="login-divider" />

            <button type="submit" disabled={loading} className="login-submit">
              {loading
                ? isSignUp ? 'Creating account…' : 'Signing in…'
                : isSignUp ? 'Create Account' : 'Sign In'}
            </button>
          </form>

        </div>
      </div>
    </AppShell>
  );
}
