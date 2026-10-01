import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Yu Picture · 雲端圖庫",
  description: "以 Next.js 與 FastAPI 重做的協作圖庫。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="zh-Hant"><body>{children}</body></html>;
}
