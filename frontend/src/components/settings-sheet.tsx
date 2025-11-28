"use client"

import { Settings, Type, LayoutTemplate, Monitor } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { useUIStore } from "@/store/ui-store"
import React from "react"

export function SettingsSheet({ trigger }: { trigger?: React.ReactNode }) {
    const { fontSize, setFontSize } = useUIStore()

    return (
        <Sheet>
            <SheetTrigger asChild>
                {trigger ? trigger : (
                    <Button variant="ghost" size="icon" title="Настройки интерфейса">
                        <Settings className="h-[1.2rem] w-[1.2rem]" />
                    </Button>
                )}
            </SheetTrigger>
            <SheetContent>
                <SheetHeader>
                    <SheetTitle>Настройки вида</SheetTitle>
                    <SheetDescription>
                        Настройте рабочее пространство под себя.
                    </SheetDescription>
                </SheetHeader>

                <div className="grid gap-6 py-6">
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <Label className="flex items-center gap-2"><Type className="w-4 h-4" /> Размер шрифта</Label>
                            <span className="text-sm text-muted-foreground">{fontSize}px</span>
                        </div>
                        <Slider
                            defaultValue={[fontSize]}
                            max={20}
                            min={12}
                            step={1}
                            onValueChange={(val) => setFontSize(val[0])}
                        />
                    </div>
                    <div className="h-[1px] bg-border" />
                    <div className="flex items-center justify-between space-x-2">
                        <Label htmlFor="compact-mode" className="flex flex-col space-y-1">
                            <span className="flex items-center gap-2"><LayoutTemplate className="w-4 h-4" /> Компактный режим</span>
                            <span className="font-normal text-xs text-muted-foreground">Уменьшить отступы</span>
                        </Label>
                        <Switch id="compact-mode" disabled />
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    )
}