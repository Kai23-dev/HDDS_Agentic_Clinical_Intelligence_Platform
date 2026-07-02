/*
  Header component for the HDDS platform.
  Shows the EY-style top bar with project name.
*/
import { Activity } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-[#2e2e38] text-white">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-[#ffe600] rounded p-1.5">
            <Activity className="w-5 h-5 text-[#2e2e38]" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">HDDS Clinical Intelligence</h1>
            <p className="text-xs text-gray-400">Hospital Discharge Data Summary Platform</p>
          </div>
        </div>
        <span className="text-xs bg-[#ffe600] text-[#2e2e38] font-semibold px-2.5 py-1 rounded">
          PROTOTYPE v2.0
        </span>
      </div>
      {/* Yellow accent line */}
      <div className="h-1 bg-[#ffe600]"></div>
    </header>
  );
}
