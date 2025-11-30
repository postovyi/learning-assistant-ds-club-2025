import { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { chatApi, type Message } from '../../api';
import { useSession } from '../../contexts/SessionContext';

export function ChatInterface() {
    const { currentSessionId } = useSession();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        if (currentSessionId) {
            chatApi.getMessages(currentSessionId)
                .then(response => setMessages(response.data))
                .catch(console.error);
        } else {
            setMessages([]);
        }
    }, [currentSessionId]);

    const handleSend = async () => {
        if (!input.trim() || !currentSessionId) return;

        // Optimistic update
        const tempId = Date.now().toString();
        const userMessage: Message = {
            id: tempId,
            role: 'user',
            content: input,
            created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');

        try {
            const response = await chatApi.sendMessage(currentSessionId, input);
            // Replace optimistic message or just append response
            // Ideally we replace, but appending response is easier for now
            setMessages(prev => [...prev, response.data]);
        } catch (error) {
            console.error('Error sending message:', error);
            // Handle error (maybe remove optimistic message)
        }
    };

    if (!currentSessionId) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-50 text-gray-500">
                Select or create a session to start chatting.
            </div>
        );
    }

    return (
        <div className="flex h-full flex-col bg-gray-50">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
                ))}
                <div ref={messagesEndRef} />
            </div>
            <div className="border-t bg-white p-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type your message..."
                        className="flex-1 rounded-md border px-4 py-2 focus:border-blue-500 focus:outline-none"
                    />
                    <button
                        onClick={handleSend}
                        className="flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                    >
                        <Send className="h-5 w-5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
