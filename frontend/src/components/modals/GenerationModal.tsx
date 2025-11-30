import { useState, useEffect } from 'react';
import { X, Sparkles } from 'lucide-react';
import { materialsApi, type Material } from '../../api';
import { useSession } from '../../contexts/SessionContext';

interface GenerationModalProps {
    isOpen: boolean;
    onClose: () => void;
    type: 'homework' | 'lesson';
    onSubmit: (data: { topic: string; difficulty: string; materials: string[] }) => Promise<void>;
}

export function GenerationModal({ isOpen, onClose, type, onSubmit }: GenerationModalProps) {
    const { currentSessionId } = useSession();
    const [topic, setTopic] = useState('');
    const [difficulty, setDifficulty] = useState('intermediate');
    const [selectedMaterials, setSelectedMaterials] = useState<string[]>([]);
    const [materials, setMaterials] = useState<Material[]>([]);
    const [isGenerating, setIsGenerating] = useState(false);

    useEffect(() => {
        if (isOpen && currentSessionId) {
            loadMaterials();
        }
    }, [isOpen, currentSessionId]);

    const loadMaterials = async () => {
        if (!currentSessionId) return;
        try {
            const response = await materialsApi.list(currentSessionId);
            setMaterials(response.data);
        } catch (error) {
            console.error('Failed to load materials:', error);
        }
    };

    const toggleMaterial = (materialId: string) => {
        setSelectedMaterials(prev =>
            prev.includes(materialId)
                ? prev.filter(id => id !== materialId)
                : [...prev, materialId]
        );
    };

    if (!isOpen) return null;

    const handleSubmit = async () => {
        if (!topic) return;

        setIsGenerating(true);
        try {
            await onSubmit({ topic, difficulty, materials: selectedMaterials });
            onClose();
            setTopic('');
            setSelectedMaterials([]);
        } catch (error) {
            console.error('Generation failed:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
                <div className="flex items-center justify-between border-b pb-4">
                    <h2 className="text-xl font-semibold text-gray-900">
                        Generate {type === 'homework' ? 'Homework' : 'Lesson'}
                    </h2>
                    <button onClick={onClose} className="rounded-full p-1 hover:bg-gray-100">
                        <X className="h-5 w-5 text-gray-500" />
                    </button>
                </div>

                <div className="mt-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Topic or Concept</label>
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                            placeholder="e.g., Quantum Entanglement"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Difficulty Level</label>
                        <select
                            value={difficulty}
                            onChange={(e) => setDifficulty(e.target.value)}
                            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                            <option value="beginner">Beginner</option>
                            <option value="intermediate">Intermediate</option>
                            <option value="advanced">Advanced</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Source Materials</label>
                        <div className="mt-1 max-h-48 overflow-y-auto rounded-md border border-gray-300 p-3">
                            {materials.length === 0 ? (
                                <p className="text-sm text-gray-500 italic">No materials available. Upload some first!</p>
                            ) : (
                                <div className="space-y-2">
                                    {materials.map((material) => (
                                        <label key={material.id} className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-2 rounded">
                                            <input
                                                type="checkbox"
                                                checked={selectedMaterials.includes(material.id)}
                                                onChange={() => toggleMaterial(material.id)}
                                                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                            />
                                            <span className="text-sm text-gray-700">{material.name}</span>
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>
                        {selectedMaterials.length > 0 && (
                            <p className="mt-1 text-xs text-gray-500">
                                {selectedMaterials.length} material{selectedMaterials.length > 1 ? 's' : ''} selected
                            </p>
                        )}
                    </div>
                </div>

                <div className="mt-8 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={isGenerating || !topic}
                        className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                    >
                        <Sparkles className="h-4 w-4" />
                        {isGenerating ? 'Generating...' : 'Generate'}
                    </button>
                </div>
            </div>
        </div>
    );
}
