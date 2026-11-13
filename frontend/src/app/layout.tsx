import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Royals ScoutIQ | Rajasthan Royals Pressure Reliability & Strategic Investment Intelligence",
  description: "SupeRR Selector Season 2 — Ground-truth ball-by-ball pressure reliability rankings and IPL 2027 long-term investment shortlist",
};

import AppShell from "@/components/AppShell";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <body className="h-full bg-[#070A14] text-slate-100 antialiased font-sans">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
