import { useState } from 'react';
import { Lock, User, AlertTriangle, Activity, ArrowRight } from 'lucide-react';
import { API_URL } from '../config';

export default function LoginView({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const endpoint = mode === 'login' ? '/api/login' : '/api/register';
    const body = mode === 'login' ? { email, password } : { name, email, password };

    try {
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }
      onLogin(data);
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  const switchMode = (next) => {
    setMode(next);
    setError('');
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Brand panel */}
      <div className="relative md:w-1/2 bg-ey-dark text-white flex flex-col justify-between px-8 sm:px-12 py-10 overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_20%_20%,#ffe600,transparent_40%),radial-gradient(circle_at_80%_70%,#ffe600,transparent_35%)]" />
        <div className="relative flex items-center gap-3">
          <div className="bg-ey-yellow rounded-lg p-2.5 shadow-lg shadow-ey-yellow/20">
            <Activity className="w-6 h-6 text-ey-dark" />
          </div>
          <div>
            <p className="text-lg font-bold leading-none">EY HDDS</p>
            <p className="text-[11px] text-ey-yellow/80 uppercase tracking-wide mt-1">Clinical Intelligence Platform</p>
          </div>
        </div>

        <div className="relative max-w-md">
          <h1 className="text-3xl sm:text-4xl font-extrabold leading-tight mb-4">
            Agentic clinical insight,<br />reviewed by you.
          </h1>
          <p className="text-gray-300 text-sm leading-relaxed">
            A pipeline of coordinated AI agents turns discharge data into
            clinician-reviewable risk, treatment, and follow-up insights —
            every output routed back through you before it matters.
          </p>
        </div>

        <p className="relative text-[11px] text-gray-500">
          Prototype using synthetic data. Not a final diagnosis or treatment decision.
        </p>
      </div>

      {/* Form panel */}
      <div className="flex-1 flex items-center justify-center bg-gray-50 px-4 sm:px-8 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-ey-dark mb-1">
              {mode === 'login' ? 'Sign in' : 'Create your account'}
            </h2>
            <p className="text-sm text-gray-500">
              {mode === 'login' ? 'Secure clinical access' : 'Register as a doctor to get started'}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="w-4 h-4 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-ey-yellow focus:ring-1 focus:ring-ey-yellow"
                    placeholder="Dr. Jane Smith"
                    required
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-ey-yellow focus:ring-1 focus:ring-ey-yellow"
                  placeholder="doctor@ey.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-ey-yellow focus:ring-1 focus:ring-ey-yellow"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-ey-yellow text-ey-dark py-2.5 rounded-lg font-bold hover:bg-[#e6cf00] transition-colors mt-2 disabled:opacity-60"
            >
              {isLoading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
              {!isLoading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <p className="text-sm text-gray-500 text-center mt-6">
            {mode === 'login' ? (
              <>No account? <button onClick={() => switchMode('register')} className="text-ey-dark font-semibold hover:underline">Register</button></>
            ) : (
              <>Already have an account? <button onClick={() => switchMode('login')} className="text-ey-dark font-semibold hover:underline">Sign in</button></>
            )}
          </p>

          {mode === 'login' && (
            <div className="mt-8 border-t border-gray-200 pt-6">
              <p className="text-xs text-gray-500 font-medium mb-2 uppercase">Test Accounts</p>
              <div className="text-xs text-gray-600 space-y-1 bg-white p-3 rounded-lg border border-gray-200">
                <p><strong>Doctor:</strong> doctor@ey.com / password123</p>
                <p><strong>Admin:</strong> admin@ey.com / admin</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
