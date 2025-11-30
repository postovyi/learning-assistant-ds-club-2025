import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { chatApi, type Session } from '../api';

interface SessionContextType {
    currentSessionId: string | null;
    sessions: Session[];
    setCurrentSessionId: (id: string) => void;
    createNewSession: (title: string) => Promise<void>;
    refreshSessions: () => Promise<void>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
    const [sessions, setSessions] = useState<Session[]>([]);

    const refreshSessions = async () => {
        try {
            const response = await chatApi.getSessions();
            setSessions(response.data);
            if (!currentSessionId && response.data.length > 0) {
                setCurrentSessionId(response.data[0].id);
            }
        } catch (error) {
            console.error('Failed to fetch sessions:', error);
        }
    };

    const createNewSession = async (title: string) => {
        try {
            const response = await chatApi.createSession(title);
            await refreshSessions();
            setCurrentSessionId(response.data.id);
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    };

    useEffect(() => {
        refreshSessions();
    }, []);

    return (
        <SessionContext.Provider value={{
            currentSessionId,
            sessions,
            setCurrentSessionId,
            createNewSession,
            refreshSessions
        }}>
            {children}
        </SessionContext.Provider>
    );
}

export function useSession() {
    const context = useContext(SessionContext);
    if (context === undefined) {
        throw new Error('useSession must be used within a SessionProvider');
    }
    return context;
}
