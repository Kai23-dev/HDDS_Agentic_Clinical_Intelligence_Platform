/*
  Sidebar - persistent EY-branded left navigation.
  Fixed on desktop (md+), off-canvas drawer with overlay on mobile.
*/
import { Activity, Upload, Database, X } from 'lucide-react';

const NAV_ITEMS = [
  { key: 'upload', label: 'New Analysis', icon: Upload },
  { key: 'results', label: 'Results', icon: Database },
];

export default function Sidebar({ view, onNavigate, mobileOpen, onClose }) {
  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 w-64 flex-shrink-0 bg-ey-dark text-white
          flex flex-col transition-transform duration-300 ease-in-out
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}
      >
        <div className="flex items-center justify-between px-5 py-5 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="bg-ey-yellow rounded-lg p-2 shadow-lg shadow-ey-yellow/20">
              <Activity className="w-5 h-5 text-ey-dark" />
            </div>
            <div>
              <p className="text-sm font-bold tracking-tight leading-none">EY HDDS</p>
              <p className="text-[10px] text-ey-yellow/80 uppercase tracking-wide mt-1">Clinical Intelligence</p>
            </div>
          </div>
          <button onClick={onClose} className="md:hidden text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 px-3 py-6 space-y-1">
          {NAV_ITEMS.map(({ key, label, icon: Icon }) => {
            const active = view === key;
            return (
              <button
                key={key}
                onClick={() => onNavigate(key)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                  ${active
                    ? 'bg-ey-yellow text-ey-dark shadow-sm'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'}`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            );
          })}
        </nav>

        <div className="px-5 py-4 border-t border-white/10">
          <p className="text-[10px] text-gray-500 uppercase tracking-wide">Prototype v3.0</p>
          <p className="text-[10px] text-gray-500 mt-1">Synthetic data only</p>
        </div>
      </aside>
    </>
  );
}
