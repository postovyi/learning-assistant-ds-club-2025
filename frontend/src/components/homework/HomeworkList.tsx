import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { GenerationModal } from '../modals/GenerationModal';
import { homeworkApi, type Homework } from '../../api';
import { useSession } from '../../contexts/SessionContext';

export function HomeworkList() {
    const { currentSessionId } = useSession();
    const navigate = useNavigate();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [homeworks, setHomeworks] = useState<Homework[]>([]);

    useEffect(() => {
        if (currentSessionId) {
            loadHomeworks();
        } else {
            setHomeworks([]);
        }
    }, [currentSessionId]);

    const loadHomeworks = async () => {
        if (!currentSessionId) return;
        try {
            const response = await homeworkApi.list(currentSessionId);
            setHomeworks(response.data);
        } catch (error) {
            console.error('Failed to load homeworks:', error);
        }
    };

    const handleCreateHomework = async (data: { topic: string; difficulty: string; materials: string[] }) => {
        if (!currentSessionId) return;
        await homeworkApi.create(currentSessionId, data.topic, data.difficulty, data.materials);
        await loadHomeworks();
    };

    if (!currentSessionId) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-50 text-gray-500">
                Select or create a session to view homework.
            </div>
        );
    }

    return (
        <div className="h-full bg-gray-50 p-8">
            <div className="mx-auto max-w-5xl space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Homework Assignments</h1>
                        <p className="text-gray-500">Manage and track your homework tasks</p>
                    </div>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
                    >
                        <Plus className="h-4 w-4" />
                        Create Homework
                    </button>
                </div>

                <div className="space-y-4">
                    {homeworks.map((hw) => (
                        <div
                            key={hw.id}
                            onClick={() => navigate(`/homework/${hw.id}`)}
                            className="cursor-pointer rounded-lg border bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
                        >
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-lg font-medium text-gray-900">{hw.title}</h3>
                                    <p className="text-sm text-gray-500">
                                        Created {hw.generated_at ? new Date(hw.generated_at).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'short',
                                            day: 'numeric'
                                        }) : 'Unknown date'}
                                    </p>
                                </div>
                                <span className={`rounded-full px-3 py-1 text-xs font-medium ${hw.status === 'submitted' ? 'bg-green-100 text-green-800' :
                                        hw.status === 'graded' ? 'bg-blue-100 text-blue-800' :
                                            'bg-yellow-100 text-yellow-800'
                                    }`}>
                                    {hw.status.charAt(0).toUpperCase() + hw.status.slice(1)}
                                </span>
                            </div>
                            <p className="mt-2 text-sm text-gray-600">{hw.tasks.length} task{hw.tasks.length !== 1 ? 's' : ''}</p>
                        </div>
                    ))}

                    {homeworks.length === 0 && (
                        <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-200 py-12 text-center">
                            <p className="text-gray-500">No homework assignments yet. Create one to get started!</p>
                        </div>
                    )}
                </div>
            </div>

            <GenerationModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                type="homework"
                onSubmit={handleCreateHomework}
            />
        </div>
    );
}
