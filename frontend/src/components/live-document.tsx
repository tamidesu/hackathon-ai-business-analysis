"use client"

import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { MermaidDiagram } from "@/components/mermaid-diagram"
import { Skeleton } from "@/components/ui/skeleton"
import { useUIStore } from "@/store/ui-store"
import { Button } from "@/components/ui/button"
import { Download, Copy, Share2, Check, FileText } from "lucide-react"
import { toast } from "sonner"
import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'

export function LiveDocument() {
    // ПОДТЯГИВАЕМ ДАННЫЕ ИЗ STORE
    const {
        isGenerating,
        fontSize,
        docTitle,
        docVersion,
        sections,
        diagramCode
    } = useUIStore()

    const [isCopied, setIsCopied] = useState(false)
    const [scrolled, setScrolled] = useState(false)
    const viewportRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const viewport = viewportRef.current?.querySelector('[data-radix-scroll-area-viewport]');
        const handleScroll = () => {
            if (viewport) {
                setScrolled(viewport.scrollTop > 10)
            }
        }
        viewport?.addEventListener('scroll', handleScroll)
        return () => viewport?.removeEventListener('scroll', handleScroll)
    }, [])

    const handleCopy = () => {
        setIsCopied(true)
        toast.success("Скопировано в буфер")
        setTimeout(() => setIsCopied(false), 2000)
    }

    const handleDownload = () => {
        toast.info("Экспорт PDF...", { description: "Генерация файла..." })
        setTimeout(() => toast.success(`${docTitle}.pdf скачан`), 1500)
    }

    // Пустое состояние (если данных еще нет)
    const isEmpty = sections.length === 0 && !diagramCode && !isGenerating;

    return (
        <div className="h-full bg-background/50 flex flex-col relative group">
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] bg-repeat" />

            {/* ШАПКА */}
            <div className={cn(
                "h-14 flex items-center justify-between px-6 shrink-0 z-20 transition-all duration-300 border-b",
                scrolled ? "bg-background/80 backdrop-blur-md border-border" : "bg-transparent border-transparent"
            )}>
                <div className="flex items-center gap-3">
                    <div className="bg-primary/10 p-1.5 rounded-md">
                        <FileText className="w-4 h-4 text-primary" />
                    </div>
                    <div className="flex flex-col leading-none">
                        {/* ДИНАМИЧЕСКИЙ ЗАГОЛОВОК */}
                        <span className="font-semibold text-sm text-foreground truncate max-w-[200px]">{docTitle}</span>
                        <span className="text-[10px] text-muted-foreground mt-0.5">{docVersion}</span>
                    </div>

                    {isGenerating ? (
                        <Badge variant="secondary" className="animate-pulse text-[10px] bg-emerald-500/10 text-emerald-600 ml-2">WRITING...</Badge>
                    ) : (
                        <Badge variant="outline" className="text-[10px] border-amber-500/30 text-amber-600 ml-2">DRAFT</Badge>
                    )}
                </div>

                <div className="flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-primary/10 hover:text-primary" onClick={handleCopy}>
                        {isCopied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-primary/10 hover:text-primary" onClick={handleDownload}>
                        <Download className="w-4 h-4" />
                    </Button>
                </div>
            </div>

            {/* ТЕЛО ДОКУМЕНТА */}
            <ScrollArea className="flex-1" ref={viewportRef}>
                <div
                    className="max-w-3xl mx-auto py-12 px-10 min-h-[calc(100vh-4rem)] bg-background shadow-sm my-4 border mx-4 sm:mx-auto rounded-lg transition-all"
                    style={{ fontSize: `${fontSize}px` }}
                >

                    {isGenerating && sections.length === 0 ? (
                        // СКЕЛЕТОНЫ (Показываем только при первой генерации)
                        <div className="space-y-8 animate-in fade-in duration-700 opacity-60">
                            <Skeleton className="h-12 w-3/4" />
                            <Skeleton className="h-5 w-1/2" />
                            <div className="space-y-3 pt-4"><Skeleton className="h-4 w-full" /><Skeleton className="h-4 w-5/6" /></div>
                            <Skeleton className="h-64 w-full rounded-xl" />
                        </div>
                    ) : isEmpty ? (
                        // ПУСТОЕ СОСТОЯНИЕ
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-20 opacity-50">
                            <FileText className="w-16 h-16 mb-4 stroke-1" />
                            <p>Документ пока пуст</p>
                            <p className="text-sm">Начните диалог с AI для генерации</p>
                        </div>
                    ) : (
                        // ДИНАМИЧЕСКИЙ КОНТЕНТ
                        <div className="animate-in slide-in-from-bottom-4 duration-700 fade-in space-y-8 text-foreground/90 leading-loose">

                            {/* Заголовок Документа */}
                            <div className="border-b pb-6">
                                <h1 className="font-serif font-bold text-4xl tracking-tight mb-3 text-foreground">{docTitle}</h1>
                                <div className="flex items-center gap-4 text-sm text-muted-foreground font-medium">
                                    <span>Generated by Magenta</span>
                                    <span>•</span>
                                    <span>{new Date().toLocaleDateString()}</span>
                                </div>
                            </div>

                            {/* Рендеринг секций из Store */}
                            {sections.map((section, index) => (
                                <section key={index}>
                                    <h2 className="font-serif font-bold text-2xl mb-4 flex items-center gap-2 text-foreground">
                                        <span className="text-primary/40 text-lg mr-1">#</span> {section.title}
                                    </h2>
                                    <div className="text-muted-foreground text-justify prose dark:prose-invert max-w-none">
                                        <ReactMarkdown>{section.content}</ReactMarkdown>
                                    </div>
                                </section>
                            ))}

                            {/* Диаграмма (если есть) */}
                            {diagramCode && (
                                <section className="bg-muted/30 p-6 rounded-xl border border-border/50 break-inside-avoid">
                                    <h2 className="font-serif font-bold text-xl mb-4 text-foreground">Визуализация процесса</h2>
                                    <MermaidDiagram chart={diagramCode} />
                                </section>
                            )}
                        </div>
                    )}

                </div>
            </ScrollArea>
        </div>
    )
}