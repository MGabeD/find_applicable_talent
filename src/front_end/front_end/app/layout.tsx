import type React from "react";
import "@/app/globals.css";
import { Inter } from "next/font/google";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Candidate Management System",
  description: "Manage and filter candidates",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="light">
        {children}
        <Toaster />
      </body>
    </html>
  );
}
