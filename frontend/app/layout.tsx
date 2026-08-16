import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const sansBody = Inter({
  variable: "--font-sans-body",
  subsets: ["latin"],
});

const monoStamp = JetBrains_Mono({
  variable: "--font-mono-stamp",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: "Ledger — Mini REST API",
  description: "A note-taking app run like a card catalog, not a journal.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${sansBody.variable} ${monoStamp.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
