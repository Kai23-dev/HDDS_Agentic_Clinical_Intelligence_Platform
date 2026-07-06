/*
  Header component for the HDDS platform.
  Shows the EY-style top bar with project name.
*/
import { Activity } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-ey-dark text-white shadow-md relative z-10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="bg-ey-yellow rounded-lg p-2 shadow-lg shadow-ey-yellow/20">
            <Activity className="w-5 h-5 text-ey-dark" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">EY HDDS <span className="font-light text-gray-300">Clinical Intelligence</span></h1>
            <p className="text-xs text-ey-yellow/90 tracking-wide uppercase mt-0.5 font-semibold">Hospital Discharge Data Summary</p>
          </div>
        </div>
        <span className="text-xs bg-white/10 backdrop-blur-sm border border-white/20 text-white font-medium px-3 py-1.5 rounded-full shadow-sm">
          PROTOTYPE v2.0
        </span>
      </div>
      {/* Yellow accent line with glow */}
      <div className="h-1 bg-ey-yellow shadow-[0_0_10px_rgba(255,230,0,0.5)]"></div>
    </header>
  );
}
