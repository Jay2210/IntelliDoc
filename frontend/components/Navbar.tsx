"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const Navbar = () => {
  const pathname = usePathname();

  const navLinks = [
    { label: "Features", href: "/#features" },
    { label: "How It Works", href: "/#how-it-works" },
  ];

  return (
    <header className="bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50 border-b border-gray-700">
        <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
            <Link href="/" className="text-2xl font-bold text-white">IntelliDoc</Link>
            <div className="flex items-center space-x-4">
                {/* Only show these links on the landing page */}
                {pathname === '/' && navLinks.map((link) => (
                    <a key={link.label} href={link.href} className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                        {link.label}
                    </a>
                ))}
                <Link href="/chat" className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                    Try Demo
                </Link>
            </div>
        </nav>
    </header>
  );
};