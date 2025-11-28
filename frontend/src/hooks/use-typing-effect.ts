import { useState, useEffect } from 'react';

export function useTypingEffect(text: string, speed: number = 30, isEnabled: boolean = true) {
    const [displayedText, setDisplayedText] = useState("");
    const [isCompleted, setIsCompleted] = useState(false);

    useEffect(() => {
        // Если эффект выключен, показываем текст сразу
        if (!isEnabled) {
            setDisplayedText(text);
            setIsCompleted(true);
            return;
        }

        setDisplayedText("");
        setIsCompleted(false);

        let i = 0;
        const intervalId = setInterval(() => {
            // ГЛАВНОЕ ИСПРАВЛЕНИЕ:
            // Мы не прибавляем букву, а берем срез строки от 0 до i.
            // Это гарантирует, что буквы всегда будут на своих местах.
            setDisplayedText(text.slice(0, i + 1));
            i++;

            if (i >= text.length) {
                clearInterval(intervalId);
                setIsCompleted(true);
            }
        }, speed);

        return () => clearInterval(intervalId);
    }, [text, speed, isEnabled]);

    return { displayedText, isCompleted };
}