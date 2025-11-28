"use client"

import * as React from "react"
import { Send, Bot, User, Loader2, Sparkles, CreditCard, ShieldCheck, Link as LinkIcon, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useTypingEffect } from "@/hooks/use-typing-effect"
import { useUIStore } from "@/store/ui-store"
import ReactMarkdown from 'react-markdown'
import { Artifacts, ChatResponse, BackendRequirements } from "@/types/api"
import { mapBackendDocToSections } from "@/lib/mapper";

// --- MOCK DATA ---
const MOCK_REQUIREMENTS: BackendRequirements = {
    project_name: "Система Лояльности 'Black'",
    version: "1.0",
    document_status: "DRAFT",
    last_updated: "2025-11-28",
    business_goal: "Разработать автоматизированную систему начисления вознаграждений для премиальных клиентов с целью увеличения удержания **(Retention Rate) на 15%** в течение Q1 2026.",
    solution_scope: "Включает модуль начисления, интеграцию с процессингом и мобильное приложение.",
    functional_requirements: [
        "Система должна обрабатывать транзакции в реальном времени.",
        "Базовый кэшбек составляет 1.5%.",
        "Максимальная сумма выплаты — 50 000 KZT."
    ],
    non_functional_requirements: [
        "Время отклика API < 200ms",
        "Соответствие PCI DSS"
    ],
    diagram_mermaid: `graph TD
    A[Клиент] -->|Заявка| B(Скоринг)
    B -->|Одобрено| C[Выдача карты]
    B -->|Отказ| D[Уведомление]
    C --> E{Активация}
    E -->|Да| F[Начисление бонусов]
    E -->|Нет| G[Блокировка]`
}

function BotMessage({ content, isLatest }: { content: string, isLatest: boolean }) {
    const { displayedText, isCompleted } = useTypingEffect(content, 15, isLatest);
    return (
        <div className="flex w-full gap-4 justify-start items-start animate-slide-up group">
            <Avatar className="h-9 w-9 border ring-2 ring-background shadow-sm bg-gradient-to-br from-primary/10 to-purple-500/10">
                <AvatarFallback className="text-primary font-bold"><Bot className="h-5 w-5" /></AvatarFallback>
            </Avatar>
            <div className="flex flex-col gap-1.5 max-w-[85%]">
                <span className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider ml-1 opacity-0 group-hover:opacity-100 transition-opacity">Magenta Core</span>
                <Card className="p-5 text-sm bg-background/50 backdrop-blur-sm shadow-sm border border-border/50 rounded-2xl rounded-tl-none">
                    <div className="prose dark:prose-invert prose-sm max-w-none leading-relaxed prose-p:my-1 text-foreground/90">
                        <ReactMarkdown>{displayedText}</ReactMarkdown>
                    </div>
                    {!isCompleted && isLatest && (
                        <span className="inline-block w-1.5 h-4 ml-1 bg-primary animate-pulse align-middle rounded-full" />
                    )}
                </Card>
            </div>
        </div>
    )
}

type PublishResponse = {
  confluence_url: string;
  page_id: string;
  status: string; // "created" | "updated"
};

export function ChatInterface() {
    const [input, setInput] = React.useState("")
    const [isLoading, setIsLoading] = React.useState(false)

    const backendBaseUrl =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

    const [sessionId] = React.useState(() => "session_" + Date.now());
    const [hasPublished, setHasPublished] = React.useState(false);

    const setGenerating = useUIStore((state) => state.setGenerating)
    const setArtifacts = useUIStore((state) => state.setArtifacts)
    const resetDocument = useUIStore((state) => state.resetDocument)

    const [messages, setMessages] = React.useState<any[]>([])
    const scrollRef = React.useRef<HTMLDivElement>(null)

    React.useEffect(() => {
        scrollRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages, isLoading])

    const handleQuickPrompt = (text: string) => {
        setInput(text);
    }

    // Функция для обработки успешного ответа (не важно, реального или мокового)
    const handleSuccessResponse = async (response: ChatResponse) => {
    // 1. Обновляем правую панель (LiveDocument), если пришли требования
        if (response.requirements) {
            const formattedSections = mapBackendDocToSections(response.requirements);
            setArtifacts({
                docTitle: response.requirements.project_name,
                docVersion: `v${response.requirements.version} (${response.requirements.document_status})`,
                sections: formattedSections,
                diagramCode: response.requirements.diagram_mermaid || ""
            });
        }

        // 2. Добавляем обычный ответ бота
        setMessages(prev => [
            ...prev,
            {
                id: Date.now() + 1,
                role: "assistant",
                content: response.assistant_message || "Ответ получен, но он пуст.",
            },
        ]);

        // 3. Если документ готов — сразу публикуем
        if (response.is_completed && response.requirements && !hasPublished) {
            try {
                const publishRes = await fetch(`${backendBaseUrl}/api/v1/publish`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: sessionId,
                        doc: response.requirements,
                        parent_title: null, // если не используешь иерархию — можно не отправлять
                    }),
                });

                if (!publishRes.ok) {
                    console.error("Publish failed", publishRes.status);
                    setMessages(prev => [
                        ...prev,
                        {
                            id: Date.now() + 2,
                            role: "assistant",
                            content:
                                "⚠️ Не удалось автоматически опубликовать документ в Confluence (ошибка сервера).",
                        },
                    ]);
                    return;
                }

                const publishData: PublishResponse = await publishRes.json();

                if (publishData.confluence_url) {
                    setMessages(prev => [
                        ...prev,
                        {
                            id: Date.now() + 3,
                            role: "assistant",
                            content: `Документ опубликован в Confluence:\n\n[Открыть документ](${publishData.confluence_url})`,
                        },
                    ]);
                    setHasPublished(true);
                } else {
                    setMessages(prev => [
                        ...prev,
                        {
                            id: Date.now() + 3,
                            role: "assistant",
                            content:
                                "Документ опубликован, но сервер не вернул ссылку Confluence.",
                        },
                    ]);
                }
            } catch (e) {
                console.error(e);
                setMessages(prev => [
                    ...prev,
                    {
                        id: Date.now() + 4,
                        role: "assistant",
                        content:
                            "⚠️ Не удалось автоматически опубликовать документ в Confluence (network error).",
                    },
                ]);
            }
        }
    };

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), role: "user", content: input };
        setMessages(prev => [...prev, userMsg]);

        const currentInput = input;
        setInput("");
        setIsLoading(true);
        setGenerating(true);

        try {
            const res = await fetch(`${backendBaseUrl}/api/v1/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: currentInput,
                    // пока можно без history, если на бэке он опционален
                }),
            });

            if (!res.ok) throw new Error("Backend error");

            const data: ChatResponse = await res.json();

            await handleSuccessResponse(data);
        } catch (error) {
            console.error(error);
            setMessages(prev => [
                ...prev,
                {
                    id: Date.now() + 1,
                    role: "assistant",
                    content:
                        "⚠️ **Не удалось соединиться с сервером.** Проверьте, запущен ли backend на порту 8000.",
                },
            ]);
        } finally {
            setIsLoading(false);
            setGenerating(false);
        }
    };

    const starterCards = [
        { icon: CreditCard, title: "Процесс кредитования", desc: "Схема BPMN для выдачи займов", prompt: "Опиши процесс выдачи кредита" },
        { icon: ShieldCheck, title: "Система Антифрод", desc: "Требования к безопасности", prompt: "Нужна система антифрода" },
        { icon: User, title: "User Story: Авторизация", desc: "Сценарии входа (FaceID, SMS)", prompt: "Создай User Story для логина" },
        { icon: LinkIcon, title: "Интеграция с 1С", desc: "API спецификация и мэппинг", prompt: "Нарисуй схему интеграции с 1С" },
    ]

    return (
        <div className="flex flex-col h-full bg-background/50 relative overflow-hidden">
            <div className="absolute inset-0 bg-grid-pattern opacity-[0.4] pointer-events-none" />

            <ScrollArea className="flex-1 px-4 py-6">
                <div className="space-y-8 pb-4 max-w-3xl mx-auto">
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-10 animate-in fade-in zoom-in-95 duration-500">
                            <div className="space-y-6 flex flex-col items-center relative z-10">
                                <div className="relative">
                                    <div className="absolute -inset-4 bg-gradient-to-r from-primary/20 to-purple-600/20 rounded-full blur-xl animate-pulse" />
                                    <div className="bg-background p-4 rounded-2xl shadow-xl ring-1 ring-border relative">
                                        <Sparkles className="h-12 w-12 text-primary fill-primary/10" />
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <h3 className="font-bold text-3xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                                        Magenta Cognitive Core
                                    </h3>
                                    <p className="text-muted-foreground max-w-md mx-auto leading-relaxed text-base">
                                        AI-партнер для бизнес-анализа. <br/>
                                        <span className="text-sm opacity-70">Собирает требования, рисует схемы, пишет документацию.</span>
                                    </p>
                                </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full px-4">
                                {starterCards.map((card, i) => (
                                    <button
                                        key={i}
                                        onClick={() => handleQuickPrompt(card.prompt)}
                                        className="flex items-start gap-4 p-4 rounded-xl border bg-background/60 hover:bg-background hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 group text-left backdrop-blur-sm"
                                    >
                                        <div className="bg-muted p-2.5 rounded-lg group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                                            <card.icon className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-sm group-hover:text-primary transition-colors">{card.title}</h4>
                                            <p className="text-xs text-muted-foreground mt-1">{card.desc}</p>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((m, index) => (
                        <div key={m.id} className="relative z-10">
                            {m.role === "user" ? (
                                <div className="flex w-full gap-4 justify-end items-start animate-slide-up">
                                    <div className="max-w-[80%]">
                                        <Card className="p-4 text-sm bg-gradient-to-br from-primary to-primary/90 text-primary-foreground border-none shadow-md rounded-2xl rounded-tr-none selection:bg-white/30">
                                            {m.content}
                                        </Card>
                                    </div>
                                    <Avatar className="h-9 w-9 border-2 border-background shadow-sm bg-primary">
                                        <AvatarFallback className="text-primary-foreground"><User className="h-5 w-5" /></AvatarFallback>
                                    </Avatar>
                                </div>
                            ) : (
                                <BotMessage content={m.content} isLatest={index === messages.length - 1} />
                            )}
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex w-full gap-4 justify-start items-center ml-1 animate-pulse">
                            <Avatar className="h-9 w-9 border bg-muted">
                                <AvatarFallback><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></AvatarFallback>
                            </Avatar>
                            <span className="text-xs font-medium text-muted-foreground">Magenta анализирует контекст...</span>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>
            </ScrollArea>

            <div className="p-4 border-t bg-background/80 backdrop-blur-md z-20">
                <form onSubmit={handleSend} className="max-w-3xl mx-auto relative flex gap-3 items-end p-2 bg-background border rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Опишите задачу или процесс..."
                        className="flex-1 bg-transparent border-none shadow-none focus-visible:ring-0 min-h-[44px] py-3 text-base"
                    />
                    <Button
                        type="submit"
                        size="icon"
                        disabled={isLoading || !input.trim()}
                        className={cn(
                            "mb-1 mr-1 transition-all duration-300",
                            input.trim() ? "bg-primary hover:bg-primary/90 scale-100" : "bg-muted text-muted-foreground scale-90 opacity-70"
                        )}
                    >
                        {input.trim() ? <ArrowRight className="h-5 w-5" /> : <Send className="h-5 w-5" />}
                    </Button>
                </form>
            </div>
        </div>
    )
}