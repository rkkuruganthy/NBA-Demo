import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NBA Context Engine — Next Best Action",
  description:
    "Financial services Next Best Action recommendation engine with context graph intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased dark`} suppressHydrationWarning>
      <body className="min-h-full flex bg-gray-950 text-gray-100">
        <Sidebar />
        <main className="flex-1 ml-64 p-8 overflow-auto">{children}</main>
      </body>
    </html>
  );
}
