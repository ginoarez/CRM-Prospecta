import "./globals.css";
import { Providers } from "./providers";

export const metadata = { title: "Prospecta CRM" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body><Providers>{children}</Providers></body>
    </html>
  );
}
