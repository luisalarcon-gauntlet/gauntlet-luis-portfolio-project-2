"use client";

import Link from "next/link";

export function NavBar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0a]/80 backdrop-blur-sm border-b border-gray-800">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-white hover:text-gray-300 transition-colors">
            Luis Alarcon
          </Link>
          <div className="flex gap-6">
            <a
              href="#projects"
              className="text-gray-400 hover:text-white transition-colors"
            >
              Projects
            </a>
            <a
              href="#about"
              className="text-gray-400 hover:text-white transition-colors"
            >
              About
            </a>
            <a
              href="#contact"
              className="text-gray-400 hover:text-white transition-colors"
            >
              Contact
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}
