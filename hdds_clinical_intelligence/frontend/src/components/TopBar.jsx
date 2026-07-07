/*
  TopBar - shell header: mobile sidebar toggle, page title, user badge, logout.
*/
import { Menu, LogOut, UserCircle } from 'lucide-react';

const PAGE_TITLES = {
  upload: 'New Analysis',
  processing: 'Processing',
  results: 'Clinical Insights',
  error: 'Error',
};

export default function TopBar({ view, onMenuClick, userName, role, onLogout }) {
  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center justify-between px-4 sm:px-6 py-3.5">
        <div className="flex items-center gap-3 min-w-0">
          <button onClick={onMenuClick} className="md:hidden text-gray-500 hover:text-ey-dark flex-shrink-0">
            <Menu className="w-5 h-5" />
          </button>
          <h2 className="text-base sm:text-lg font-bold text-ey-dark truncate">
            {PAGE_TITLES[view] || 'HDDS'}
          </h2>
        </div>

        <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
          <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
            <UserCircle className="w-5 h-5 text-gray-400" />
            <span className="font-medium">{userName}</span>
            {role && (
              <span className="text-[10px] font-bold uppercase tracking-wide bg-ey-yellow/20 text-ey-dark px-2 py-0.5 rounded-full border border-ey-yellow/40">
                {role}
              </span>
            )}
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
}
