import type { Metadata } from "next";
import { Inter } from "next/font/google"; // Corrected import path
import "./globals.css";
import { SidebarProvider } from "@/context/SidebarContext";
import { MainLayout } from "@/components/MainLayout";

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
        <SidebarProvider>
          <MainLayout>{children}</MainLayout>
        </SidebarProvider>
      </body>
    </html>
  );
}
