import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TIMELOCK - 무음 타임블로킹",
  description: "독서실에서도 눈치 안 보고 쓰는 무음 타이머",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
