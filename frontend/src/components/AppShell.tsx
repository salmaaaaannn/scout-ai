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
  Menu,
  X,
  ChevronRight,
  Activity,
  Layers,
  Sparkles,
  ExternalLink
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, tag: 'Overview' },
  { name: 'Scouting Pool', href: '/scouting', icon: Users, tag: '336 Candidates' },
  { name: 'Pressure Index', href: '/rankings', icon: Flame, tag: 'BPRI / BOWPRI' },
  { name: 'Comparison', href: '/comparison', icon: GitCompare, tag: 'Head-to-Head' },
  { name: 'RR Weaknesses', href: '/weakness', icon: ShieldAlert, tag: '2024-26 Autopsy' },
  { name: 'XI Optimizer', href: '/optimizer', icon: Swords, tag: 'OR-Tools' },
  { name: 'Video Studio', href: '/video-studio', icon: Video, tag: 'YOLO11-Pose' },
  { name: 'Review Queue', href: '/verification', icon: CheckSquare, tag: 'Human-in-Loop' },
  { name: 'AI Assistance', href: '/assistant', icon: Bot, tag: 'AI Assistance' },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
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

  const activeItem = NAV_ITEMS.find((item) => item.href === pathname) || NAV_ITEMS[0];

  return (
    <div className="flex h-screen overflow-hidden bg-[#070A14] text-slate-100">
      {/* Mobile Backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800/80 bg-[#0B0F1C] transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Crest */}
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800/80 px-5">
          <Link href="/" className="flex items-center gap-3 group" onClick={() => setSidebarOpen(false)}>
            <img
              src="/rr_logo.png"
              alt="Rajasthan Royals"
              className="h-10 w-auto object-contain shrink-0"
            />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-sm tracking-wide text-white">ROYALS</span>
                <span className="rounded bg-[#E81A85] px-1.5 py-0.5 text-[10px] font-black tracking-wider text-white">
                  ScoutIQ
                </span>
              </div>
              <p className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">
                Rajasthan Royals
              </p>
            </div>
          </Link>

          <button
            onClick={() => setSidebarOpen(false)}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Platform Modules
          </div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center justify-between rounded-xl px-3 py-2.5 text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-[#E81A85]/15 text-pink-400 border border-pink-500/30 shadow-sm'
                    : 'text-slate-300 hover:bg-slate-800/60 hover:text-white border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4 w-4 ${isActive ? 'text-pink-400' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </div>
                {item.tag && (
                  <span
                    className={`rounded px-1.5 py-0.5 text-[9px] font-mono ${
                      isActive
                        ? 'bg-pink-500/20 text-pink-300'
                        : 'bg-slate-800/80 text-slate-400'
                    }`}
                  >
                    {item.tag}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer info in sidebar */}
        <div className="border-t border-slate-800/80 p-4 bg-slate-950/40">
          <div className="rounded-xl bg-slate-900/90 border border-slate-800 p-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold text-slate-400">War Room Node</span>
              <span className="text-[10px] text-slate-400 font-medium">RR Analytics</span>
            </div>
            <p className="mt-1 text-[11px] text-slate-300 font-medium">
              G. Lindsay &amp; K. Sangakkara
            </p>
            <p className="text-[10px] text-slate-500">Rajasthan Royals Strategy</p>
          </div>
        </div>
      </aside>

      {/* Main Column */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header */}
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800/80 bg-[#0B0F1C]/90 px-6 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Breadcrumb / Title */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Royals ScoutIQ</span>
              <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
              <span className="font-bold text-white">{activeItem.name}</span>
            </div>
          </div>

          {/* Right Header Status */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-block text-xs font-semibold text-slate-400">
              Rajasthan Royals Strategy
            </span>
          </div>
        </header>

        {/* Scrollable Content Body */}
        <main className="flex-1 overflow-y-auto bg-[#070A14] p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
