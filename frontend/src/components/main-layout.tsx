"use client"

import React, { useState } from "react"
import {
    ResizableHandle,
    ResizablePanel,
    ResizablePanelGroup,
} from "@/components/ui/resizable"
import { ChatInterface } from "@/components/chat-interface"
import { LiveDocument } from "@/components/live-document"
import { SettingsSheet } from "@/components/settings-sheet"
import { cn } from "@/lib/utils"
import { PlusCircle, Menu, PanelLeftClose, PanelLeftOpen, Settings, SunMoon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useUIStore } from "@/store/ui-store"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme } from "next-themes"

// --- ЛОГОТИП ---
interface MagentaBrainLogoProps {
    className?: string;
    neon?: boolean;
    color?: string;
}

export function MagentaBrainLogo({
                                     className = "",
                                     neon = false,
                                     color = "currentColor"
                                 }: MagentaBrainLogoProps) {

    const maskId = React.useId();
    const glowId = React.useId();

    return (
        <svg
            viewBox="0 0 100 100"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={className}
            style={{
                overflow: 'visible',
                color: color
            }}
        >
            <defs>
                {/* 1. ФИЛЬТР НЕОНОВОГО СВЕЧЕНИЯ */}
                {neon && (
                    <filter id={glowId} x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                )}

                {/* 2. МАСКА ДЛЯ ГЛАЗ (Вырезаем глаза из лица) */}
                <mask id={maskId}>
                    {/* Белый цвет = видимо */}
                    <rect x="0" y="0" width="100" height="100" fill="white" />
                    {/* Черный цвет = прозрачно */}
                    <g stroke="black" strokeWidth="3" strokeLinecap="round" fill="none">
                        <path d="M42 52 Q 45 47 48 52" /> {/* Левый глаз */}
                        <path d="M52 52 Q 55 47 58 52" /> {/* Правый глаз */}
                    </g>
                </mask>
            </defs>

            {/* ГРУППА С ЭФФЕКТАМИ */}
            <g filter={neon ? `url(#${glowId})` : undefined}>

                {/* 3. ВНУТРЕННИЕ ГРАНИ (Y-структура) */}
                {/* Рисуем их чуть тоньше и прозрачнее */}
                <path
                    d="M50 90 V50 M85 30 L50 50 M15 30 L50 50"
                    stroke="currentColor"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity="0.5"
                />

                {/* 4. ВНЕШНИЙ КОНТУР КУБА */}
                <path
                    d="M50 10 L85 30 V70 L50 90 L15 70 V30 Z"
                    stroke="currentColor"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />

                {/* 5. ГОЛОВА С ВЫРЕЗАННЫМИ ГЛАЗАМИ */}
                {/* Применяем маску к кругу */}
                <circle
                    cx="50"
                    cy="50"
                    r="19"
                    fill="currentColor"
                    mask={`url(#${maskId})`}
                />
            </g>
        </svg>
    );
}

// --- ЗАСТАВКА ---
function SplashScreen() {
    return (
        <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-zinc-950 text-white animate-fade-out pointer-events-none">
            <div className="relative">
                <div className="absolute inset-0 bg-primary/30 blur-[120px] rounded-full animate-pulse" />
                <MagentaBrainLogo className="w-40 h-40 text-primary relative z-10" neon />
            </div>
            <div className="mt-10 text-center space-y-3 relative z-10">
                <h1 className="text-5xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white via-primary to-purple-400">
                    Magenta
                </h1>
                <p className="text-sm text-zinc-400 tracking-[0.4em] uppercase opacity-0 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-500 fill-mode-forwards">
                    AI Analyst
                </p>
            </div>
        </div>
    )
}

export function MainLayout() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true)
    const resetDocument = useUIStore((state) => state.resetDocument)
    const { setTheme } = useTheme()

    const handleNewChat = () => {
        if (confirm("Начать новый анализ? Текущий прогресс будет сброшен.")) {
            resetDocument();
            window.location.reload();
        }
    }

    // --- ВНУТРЕННОСТЬ САЙДБАРА ---
    const SidebarContent = ({ collapsed = false }) => (
        <div className="flex flex-col h-full py-3 w-full">

            {/* 1. ЛОГОТИП И ШАПКА */}
            <div className={cn("flex items-center shrink-0 transition-all mb-4 w-full", collapsed ? "justify-center px-0" : "justify-between px-3")}>
                <div className="flex items-center gap-3 overflow-hidden">
                    {/* Иконка */}
                    <div className="bg-primary/10 p-2 rounded-xl shrink-0 flex items-center justify-center">
                        <MagentaBrainLogo className="w-7 h-7 text-primary" />
                    </div>
                    {/* Текст (Скрываем плавно) */}
                    {!collapsed && (
                        <span className="font-bold text-lg tracking-tight whitespace-nowrap animate-in fade-in slide-in-from-left-2 duration-300">
                          Magenta
                      </span>
                    )}
                </div>
                {/* Кнопка закрытия */}
                {!collapsed && (
                    <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(false)} className="hidden md:flex h-8 w-8 text-muted-foreground hover:text-foreground">
                        <PanelLeftClose className="w-4 h-4" />
                    </Button>
                )}
            </div>

            {/* 2. КНОПКА "НОВЫЙ АНАЛИЗ" */}
            <div className={cn("px-2 w-full flex", collapsed ? "justify-center" : "justify-start")}>
                <Button
                    variant={collapsed ? "ghost" : "default"}
                    size={collapsed ? "icon" : "default"}
                    className={cn(
                        "relative overflow-hidden transition-all duration-300 shadow-sm",
                        collapsed
                            ? "h-10 w-10 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 p-0 flex items-center justify-center" // Свернуто: Квадрат по центру
                            : "w-full bg-primary hover:bg-primary/90 justify-start h-10 px-3" // Развернуто: Широкая кнопка
                    )}
                    onClick={handleNewChat}
                    title="Новый анализ"
                >
                    <PlusCircle className={cn("w-5 h-5 shrink-0 transition-transform", !collapsed && "mr-2")} />
                    {!collapsed && <span className="whitespace-nowrap animate-in fade-in font-medium">Новый анализ</span>}
                </Button>
            </div>

            <div className="flex-1" />

            {/* 3. НИЗ: ТЕМА И НАСТРОЙКИ */}
            <div className="p-2 border-t border-border/40 space-y-1 w-full flex flex-col items-center">

                {/* Тема */}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button
                            variant="ghost"
                            className={cn(
                                "h-10 transition-all duration-200 hover:bg-muted/60 flex items-center",
                                collapsed
                                    ? "w-10 justify-center px-0 rounded-lg" // Свернуто: Квадрат по центру
                                    : "w-full justify-start px-2" // Развернуто: Широкая
                            )}
                        >
                            <SunMoon className="w-5 h-5 shrink-0 text-muted-foreground" />
                            {!collapsed && <span className="ml-3 text-sm font-normal truncate animate-in fade-in">Тема</span>}
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent side="right" align="start" className="w-40 ml-2">
                        <DropdownMenuItem onClick={() => setTheme("light")}>Светлая</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setTheme("dark")}>Темная</DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setTheme("system")}>Системная</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>

                {/* Настройки */}
                <SettingsSheet trigger={
                    <Button
                        variant="ghost"
                        className={cn(
                            "h-10 transition-all duration-200 hover:bg-muted/60 flex items-center",
                            collapsed
                                ? "w-10 justify-center px-0 rounded-lg" // Свернуто: Квадрат по центру
                                : "w-full justify-start px-2" // Развернуто: Широкая
                        )}
                    >
                        <Settings className="w-5 h-5 shrink-0 text-muted-foreground" />
                        {!collapsed && <span className="ml-3 text-sm font-normal truncate animate-in fade-in">Настройки</span>}
                    </Button>
                } />

            </div>
        </div>
    )

    return (
        <div className="h-screen w-full bg-background text-foreground flex overflow-hidden font-sans">
            <SplashScreen />

            {/* --- САЙДБАР --- */}
            <aside
                className={cn(
                    "border-r bg-muted/30 backdrop-blur-xl hidden md:flex flex-col transition-all duration-300 ease-in-out z-50 relative",
                    isSidebarOpen ? "w-64" : "w-[72px]"
                )}
            >
                {/* Кнопка ОТКРЫТИЯ */}
                {!isSidebarOpen && (
                    <div className="absolute top-5 left-[80px] z-50 animate-in fade-in slide-in-from-left-2 duration-500">
                        <Button
                            variant="outline"
                            size="icon"
                            onClick={() => setIsSidebarOpen(true)}
                            className="h-9 w-9 bg-background shadow-md hover:bg-muted transition-all text-muted-foreground border-dashed"
                            title="Развернуть меню"
                        >
                            <PanelLeftOpen className="w-4 h-4" />
                        </Button>
                    </div>
                )}

                <SidebarContent collapsed={!isSidebarOpen} />
            </aside>

            {/* --- ОСНОВНАЯ ЗОНА --- */}
            <main className="flex-1 flex flex-col min-w-0 bg-background relative transition-all duration-300">
                <div className="absolute inset-0 bg-grid-pattern opacity-[0.2] pointer-events-none" />

                {/* Мобильная шапка */}
                <header className="h-14 md:hidden border-b flex items-center justify-between px-4 bg-background/80 backdrop-blur-md shrink-0">
                    <div className="flex items-center gap-2">
                        <div className="bg-primary/10 p-1.5 rounded-lg">
                            <MagentaBrainLogo className="w-6 h-6 text-primary" />
                        </div>
                        <span className="font-bold text-lg">Magenta</span>
                    </div>

                    <Sheet>
                        <SheetTrigger asChild>
                            <Button variant="ghost" size="icon"><Menu className="w-5 h-5" /></Button>
                        </SheetTrigger>
                        <SheetContent side="left" className="p-0 w-72 bg-background/95 backdrop-blur-xl">
                            <SidebarContent collapsed={false} />
                        </SheetContent>
                    </Sheet>
                </header>

                <div className="flex-1 overflow-hidden p-2 md:p-4 relative z-10">
                    <ResizablePanelGroup direction="horizontal" className="h-full w-full rounded-2xl border bg-card/50 shadow-sm overflow-hidden ring-1 ring-border/10 backdrop-blur-sm">
                        <ResizablePanel defaultSize={35} minSize={30} maxSize={45} className="bg-background/60 backdrop-blur-md z-10 border-r border-border/50">
                            <ChatInterface />
                        </ResizablePanel>
                        <ResizableHandle withHandle className="bg-border/20 hover:bg-primary/50 transition-colors w-1.5 z-20 backdrop-blur-xl" />
                        <ResizablePanel defaultSize={65} className="bg-background/90 relative">
                            <LiveDocument />
                        </ResizablePanel>
                    </ResizablePanelGroup>
                </div>
            </main>
        </div>
    )
}