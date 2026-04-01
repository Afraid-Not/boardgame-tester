"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Gamepad2, Plus, BarChart3, Home } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/games", label: "Games", icon: Gamepad2 },
  { href: "/games/new", label: "New Game", icon: Plus },
];

export const Sidebar = () => {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-zinc-950 text-white border-r border-zinc-800 flex flex-col">
      <div className="p-6 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-emerald-400" />
          <div>
            <h1 className="font-bold text-lg leading-tight">Balance Tester</h1>
            <p className="text-xs text-zinc-400">Board Game Analysis</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-zinc-800 text-white"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-800/50",
              )}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-zinc-800">
        <p className="text-xs text-zinc-500">v0.1.0 - MVP</p>
      </div>
    </aside>
  );
};
