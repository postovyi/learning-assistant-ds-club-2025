import { MessageSquare, FileText, BookOpen, BrainCircuit, Plus, ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Link, useLocation } from 'react-router-dom';
import { useSession } from '../../contexts/SessionContext';

const navigation = [
    { name: 'Chat', href: '/', icon: MessageSquare },
    { name: 'Materials', href: '/materials', icon: FileText },
    { name: 'Homework', href: '/homework', icon: BookOpen },
    { name: 'Mind Maps', href: '/mind-maps', icon: BrainCircuit },
];

export function Sidebar() {
    const location = useLocation();
    const { sessions, currentSessionId, setCurrentSessionId, createNewSession } = useSession();

    const currentSession = sessions.find(s => s.id === currentSessionId);

    return (
        <div className="flex h-screen w-64 flex-col border-r bg-white text-gray-600">
            {/* Header */}
            <div className="flex h-16 items-center border-b px-6">
                <span className="text-lg font-semibold text-gray-900">Learning Assistant</span>
            </div>

            {/* Subject Selector & New Session */}
            <div className="p-4 space-y-3">
                <div className="relative">
                    <button className="flex w-full items-center justify-between rounded-md border px-3 py-2 text-sm font-medium hover:bg-gray-50">
                        <span className="truncate">{currentSession?.title || 'Select Session'}</span>
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                    </button>
                    <select
                        className="absolute inset-0 opacity-0 cursor-pointer"
                        value={currentSessionId || ''}
                        onChange={(e) => setCurrentSessionId(e.target.value)}
                    >
                        {sessions.map(session => (
                            <option key={session.id} value={session.id}>{session.title}</option>
                        ))}
                    </select>
                </div>

                <button
                    onClick={() => {
                        const title = window.prompt('Enter a name for the new session:', 'New Session');
                        if (title !== null) {
                            const trimmed = title.trim();
                            if (trimmed.length > 0) {
                                createNewSession(trimmed);
                            }
                        }
                    }}
                    className="flex w-full items-center justify-center gap-2 rounded-md border border-dashed px-3 py-2 text-sm font-medium hover:bg-gray-50"
                >
                    <Plus className="h-4 w-4" />
                    New Session
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 px-2">
                {navigation.map((item) => {
                    const isActive = location.pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            to={item.href}
                            className={cn(
                                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                                isActive
                                    ? "bg-gray-100 text-gray-900"
                                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                            )}
                        >
                            <item.icon className={cn("h-5 w-5", isActive ? "text-gray-900" : "text-gray-400 group-hover:text-gray-500")} />
                            {item.name}
                        </Link>
                    );
                })}
            </nav>

            
        </div>
    );
}
