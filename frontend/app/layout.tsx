import type { Metadata } from "next";
import { Libre_Baskerville } from "next/font/google";
import "./globals.css";
import { Navbar } from "../components/Navbar";

// Configure the Merriweather font
const merriweather = Libre_Baskerville({
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "IntelliDoc - AI Document Analysis",
  description: "Go from complex documents to clear decisions instantly.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`bg-gray-900 text-gray-200 font-sans ${merriweather.className}`}>
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
