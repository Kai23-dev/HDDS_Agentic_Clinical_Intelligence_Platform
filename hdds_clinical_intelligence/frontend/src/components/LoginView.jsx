import { useState } from 'react';
import { Lock, User, AlertTriangle } from 'lucide-react';

export default function LoginView({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // In a real app, use the actual API URL
      const res = await fetch('http://127.0.0.1:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!res.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await res.json();
      // data contains { access_token, role, name }
      onLogin(data);
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl overflow-hidden border border-gray-100">
        <div className="bg-[#2e2e38] p-6 text-center">
          <h2 className="text-2xl font-bold text-white mb-2">HDDS Platform</h2>
          <p className="text-[#ffe600] text-sm font-medium">Secure Clinical Access</p>
        </div>
        
        <div className="p-8">
          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
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
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-[#ffe600] focus:ring-1 focus:ring-[#ffe600]"
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
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-[#ffe600] focus:ring-1 focus:ring-[#ffe600]"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#ffe600] text-[#2e2e38] py-2.5 rounded-lg font-bold hover:bg-[#e6cf00] transition-colors mt-2"
            >
              {isLoading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-8 border-t border-gray-100 pt-6">
            <p className="text-xs text-gray-500 font-medium mb-2 uppercase">Test Accounts</p>
            <div className="text-xs text-gray-600 space-y-1 bg-gray-50 p-3 rounded border border-gray-200">
              <p><strong>Doctor:</strong> doctor@ey.com / password123</p>
              <p><strong>Admin:</strong> admin@ey.com / admin</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
