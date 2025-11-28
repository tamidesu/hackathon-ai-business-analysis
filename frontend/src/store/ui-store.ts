import { create } from 'zustand'
import { DocumentSection, Artifacts } from '@/types/api'

interface UIState {
    isGenerating: boolean
    setGenerating: (value: boolean) => void
    fontSize: number
    setFontSize: (value: number) => void

    // Данные документа
    docTitle: string
    docVersion: string
    diagramCode: string
    sections: DocumentSection[]

    setArtifacts: (data: Partial<Artifacts>) => void
    resetDocument: () => void
}

const initialDocState = {
    docTitle: "Новый документ",
    docVersion: "DRAFT v0.1",
    diagramCode: "",
    sections: []
}

export const useUIStore = create<UIState>((set) => ({
    isGenerating: false,
    setGenerating: (value) => set({ isGenerating: value }),
    fontSize: 16,
    setFontSize: (value) => set({ fontSize: value }),

    ...initialDocState,

    setArtifacts: (data) => set((state) => ({
        docTitle: data.docTitle ?? state.docTitle,
        docVersion: data.docVersion ?? state.docVersion,
        diagramCode: data.diagramCode ?? state.diagramCode,
        sections: data.sections ?? state.sections
    })),

    resetDocument: () => set(initialDocState)
}))