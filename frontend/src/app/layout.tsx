import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Playfair_Display } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner"
import { cn } from "@/lib/utils";

// 1. Основной шрифт интерфейса (читаемый)
const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

// 2. Шрифт для кода и JSON (технический)
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono" });

// 3. Шрифт для Документа (премиальный, с засечками)
const playfair = Playfair_Display({ subsets: ["latin", "cyrillic"], variable: "--font-serif" });

export const metadata: Metadata = {
    title: "Magenta | AI Analyst",
    description: "Automated Requirements Gathering System",
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
        <body className={cn(
            "min-h-screen bg-background font-sans antialiased",
            inter.variable,
            mono.variable,
            playfair.variable
        )}>
        <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
        >
            {children}
            <Toaster position="bottom-right" theme="system" />
        </ThemeProvider>
        </body>
        </html>
    );
}