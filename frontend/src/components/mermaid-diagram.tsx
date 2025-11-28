"use client"

import React, { useEffect, useRef, useState } from "react"
import mermaid from "mermaid"
import { useTheme } from "next-themes" // Слушаем тему

interface MermaidProps {
    chart: string
}

export function MermaidDiagram({ chart }: MermaidProps) {
    const ref = useRef<HTMLDivElement>(null)
    const [isRendered, setIsRendered] = useState(false)
    const { theme, systemTheme } = useTheme() // Получаем текущую тему (light/dark)

    useEffect(() => {
        const renderChart = async () => {
            if (ref.current && chart) {
                try {
                    // Определяем реальную тему (учитывая системную настройку)
                    const currentTheme = theme === 'system' ? systemTheme : theme;
                    const mermaidTheme = currentTheme === 'dark' ? 'dark' : 'default';

                    // Реинициализация с новой темой
                    mermaid.initialize({
                        startOnLoad: false,
                        theme: mermaidTheme,
                        securityLevel: "loose",
                        fontFamily: "Inter, sans-serif",
                        themeVariables: {
                            // Кастомизация цветов под бренд Forte (по желанию)
                            primaryColor: currentTheme === 'dark' ? '#10b981' : '#059669',
                            lineColor: currentTheme === 'dark' ? '#a1a1aa' : '#52525b',
                        }
                    })

                    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`
                    ref.current.innerHTML = ""
                    const { svg } = await mermaid.render(id, chart)
                    ref.current.innerHTML = svg
                    setIsRendered(true)
                } catch (error) {
                    console.error("Mermaid error:", error)
                }
            }
        }

        // Добавляем theme в зависимости: если тема сменится, график перерисуется
        renderChart()
    }, [chart, theme, systemTheme])

    return (
        <div className="w-full flex justify-center py-6 bg-muted/30 rounded-lg border my-4 overflow-x-auto">
            <div ref={ref} className="opacity-90 hover:opacity-100 transition-opacity" />
        </div>
    )
}