
import { cn } from '../../lib/utils';
import { User, Bot } from 'lucide-react';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
    const isUser = role === 'user';

    return (
        <div className={cn("flex w-full gap-4 p-4", isUser ? "flex-row-reverse" : "flex-row")}>
            <div className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                isUser ? "bg-blue-600 text-white" : "bg-green-600 text-white"
            )}>
                {isUser ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
            </div>
            <div className={cn(
                "flex max-w-[80%] flex-col gap-2 rounded-lg p-4",
                isUser ? "bg-blue-600 text-white" : "bg-white border text-gray-900"
            )}>
                <p className="text-sm leading-relaxed">{content}</p>
            </div>
        </div>
    );
}
