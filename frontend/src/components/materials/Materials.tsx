import { useState, useEffect } from 'react';
import { Upload, FileText, Trash2, ExternalLink } from 'lucide-react';
import { materialsApi, type Material } from '../../api';
import { useSession } from '../../contexts/SessionContext';

export function Materials() {
    const { currentSessionId } = useSession();
    const [materials, setMaterials] = useState<Material[]>([]);
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        if (currentSessionId) {
            loadMaterials();
        } else {
            setMaterials([]);
        }
    }, [currentSessionId]);

    const loadMaterials = async () => {
        if (!currentSessionId) return;
        try {
            const response = await materialsApi.list(currentSessionId);
            setMaterials(response.data);
        } catch (error) {
            console.error('Failed to load materials:', error);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file || !currentSessionId) return;

        setIsUploading(true);
        try {
            await materialsApi.upload(currentSessionId, file);
            await loadMaterials();
        } catch (error) {
            console.error('Failed to upload material:', error);
        } finally {
            setIsUploading(false);
        }
    };

    if (!currentSessionId) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-50 text-gray-500">
                Select or create a session to manage materials.
            </div>
        );
    }

    return (
        <div className="h-full bg-gray-50 p-8">
            <div className="mx-auto max-w-5xl space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Materials</h1>
                        <p className="text-gray-500">Manage your study materials and documents</p>
                    </div>
                    <div className="relative">
                        <input
                            type="file"
                            id="file-upload"
                            className="hidden"
                            onChange={handleFileUpload}
                            disabled={isUploading}
                        />
                        <label
                            htmlFor="file-upload"
                            className={`flex cursor-pointer items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            <Upload className="h-4 w-4" />
                            {isUploading ? 'Uploading...' : 'Upload Material'}
                        </label>
                    </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {materials.map((material) => (
                        <div
                            key={material.id}
                            className="group relative flex flex-col justify-between rounded-lg border bg-white p-6 shadow-sm transition-shadow hover:shadow-md"
                        >
                            <div className="space-y-4">
                                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                                    <FileText className="h-6 w-6" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900 truncate" title={material.name}>
                                        {material.name}
                                    </h3>
                                    <p className="text-sm text-gray-500">
                                        {material.uploaded_at ? new Date(material.uploaded_at).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'short',
                                            day: 'numeric'
                                        }) : 'Unknown date'}
                                    </p>
                                </div>
                            </div>

                            <div className="mt-4 flex items-center justify-end gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                                <button className="rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                                    <ExternalLink className="h-4 w-4" />
                                </button>
                                <button className="rounded-full p-2 text-gray-400 hover:bg-red-50 hover:text-red-600">
                                    <Trash2 className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    ))}

                    {materials.length === 0 && (
                        <div className="col-span-full flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-200 py-12 text-center">
                            <div className="rounded-full bg-gray-50 p-4">
                                <Upload className="h-8 w-8 text-gray-400" />
                            </div>
                            <h3 className="mt-4 text-sm font-semibold text-gray-900">No materials yet</h3>
                            <p className="mt-1 text-sm text-gray-500">Upload documents to get started</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
