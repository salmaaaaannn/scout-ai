'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Flame,
  GitCompare,
  ShieldAlert,
  Swords,
  Video,
  CheckSquare,
  Bot,
  FileText,
  Activity,
  Layers,
  ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Scouting', href: '/scouting', icon: Users },
  { name: 'Pressure Index', href: '/rankings', icon: Flame },
  { name: 'Compare', href: '/comparison', icon: GitCompare },
  { name: 'RR Weakness', href: '/weakness', icon: ShieldAlert },
  { name: 'XI Optimizer', href: '/optimizer', icon: Swords },
  { name: 'Video Studio', href: '/video-studio', icon: Video },
  { name: 'Verification Queue', href: '/verification', icon: CheckSquare },
  { name: 'AI Assistance', href: '/assistant', icon: Bot },
];

export default function Navbar() {
  const pathname = usePathname();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/health`);
        setBackendOnline(res.ok);
      } catch {
        setBackendOnline(false);
      }
    }
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-pink-500/20 bg-[#090D1A]/95 backdrop-blur-md">
      {/* Top War-Room Bar */}
      <div className="border-b border-white/5 px-4 py-1.5 text-xs text-slate-400">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-semibold uppercase tracking-wider text-amber-400/90">
              IPL 2027 Auction Intelligence
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">
              Evaluators: <strong className="text-slate-200">Giles Lindsay</strong> (Strategy) &amp; <strong className="text-slate-200">Kumar Sangakkara</strong> (Coach)
            </span>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="text-slate-500">FastAPI Backend:</span>
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                backendOnline === true
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : backendOnline === false
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
              }`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  backendOnline === true
                    ? 'bg-emerald-400 animate-pulse'
                    : backendOnline === false
                    ? 'bg-rose-400'
                    : 'bg-amber-400 animate-ping'
                }`}
              />
              {backendOnline === true ? 'ONLINE :8000' : backendOnline === false ? 'OFFLINE' : 'CHECKING...'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#E81A85] via-[#004B87] to-[#D4AF37] p-[2px] shadow-lg shadow-pink-500/20 group-hover:scale-105 transition-transform">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#070913]">
              <span className="font-black text-sm tracking-tighter text-[#E81A85]">RR</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-base tracking-wide text-white">ROYALS</span>
              <span className="rounded bg-gradient-to-r from-[#E81A85] to-pink-600 px-1.5 py-0.5 text-xs font-black tracking-wider text-white">
                ScoutIQ
              </span>
            </div>
            <p className="text-[10px] uppercase tracking-wider text-slate-400">
              Computer Vision &amp; Pressure Analytics
            </p>
          </div>
        </Link>

        {/* Links */}
        <nav className="hidden lg:flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-pink-600/20 text-pink-400 border border-pink-500/40 shadow-sm shadow-pink-500/20'
                    : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
