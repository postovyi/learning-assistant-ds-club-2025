import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { homeworkApi, type Homework } from '../../api';
import { ArrowLeft, Upload, CheckCircle } from 'lucide-react';

export function HomeworkDetail() {
    const { homeworkId } = useParams<{ homeworkId: string }>();
    const navigate = useNavigate();
    const [homework, setHomework] = useState<Homework | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [uploadingTaskId, setUploadingTaskId] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        if (homeworkId) {
            loadHomework();
        }
    }, [homeworkId]);

    const loadHomework = async () => {
        if (!homeworkId) return;
        try {
            const response = await homeworkApi.get(homeworkId);
            setHomework(response.data);
        } catch (error) {
            console.error('Failed to load homework:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (taskId: string, file: File) => {
        setUploadingTaskId(taskId);
        try {
            const hid = homework?.id ?? homeworkId;
            if (!hid) return;
            await homeworkApi.uploadTaskSolution(hid, taskId, file);
            await loadHomework();
        } catch (error: any) {
            console.error('Failed to upload task solution:', error);
            const detail = error?.response?.data?.detail;
            alert(`Failed to upload file${detail ? `: ${detail}` : '.'}`);
        } finally {
            setUploadingTaskId(null);
        }
    };

    const handleSubmitHomework = async () => {
        if (!homeworkId) return;
        setIsSubmitting(true);
        try {
            await homeworkApi.submitHomework(homeworkId);
            await loadHomework();
            alert('Homework submitted successfully!');
        } catch (error) {
            console.error('Failed to submit homework:', error);
            alert('Failed to submit homework. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-50">
                <div className="text-gray-500">Loading...</div>
            </div>
        );
    }

    if (!homework) {
        return (
            <div className="flex h-full items-center justify-center bg-gray-50">
                <div className="text-gray-500">Homework not found</div>
            </div>
        );
    }

    const latestReview = homework.reviews.length > 0 ? homework.reviews[homework.reviews.length - 1] : null;

    return (
        <div className="h-full overflow-y-auto bg-gray-50 p-8">
            <div className="mx-auto max-w-4xl space-y-6">
                <button
                    onClick={() => navigate('/homework')}
                    className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Back to Homework List
                </button>

                <div className="rounded-lg border bg-white p-6 shadow-sm">
                    <div className="flex items-start justify-between">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">{homework.title}</h1>
                            <p className="mt-1 text-sm text-gray-500">
                                Created {new Date(homework.generated_at).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                })}
                            </p>
                        </div>
                        <span className={`rounded-full px-3 py-1 text-xs font-medium ${homework.status === 'submitted' ? 'bg-green-100 text-green-800' :
                                homework.status === 'graded' ? 'bg-blue-100 text-blue-800' :
                                    'bg-yellow-100 text-yellow-800'
                            }`}>
                            {homework.status.charAt(0).toUpperCase() + homework.status.slice(1)}
                        </span>
                    </div>
                </div>

                {latestReview && (
                    <div className="rounded-lg border border-blue-200 bg-blue-50 p-6 shadow-sm">
                        <div className="flex items-start justify-between">
                            <h2 className="text-lg font-semibold text-blue-900">Overall Feedback</h2>
                            {latestReview.grade && (
                                <span className="rounded-full bg-blue-600 px-3 py-1 text-sm font-medium text-white">
                                    Grade: {latestReview.grade}
                                </span>
                            )}
                        </div>
                        {latestReview.overall_feedback && (
                            <p className="mt-3 text-gray-700 whitespace-pre-wrap">{latestReview.overall_feedback}</p>
                        )}
                        <p className="mt-2 text-xs text-gray-500">
                            Reviewed {new Date(latestReview.reviewed_at).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            })}
                        </p>
                    </div>
                )}

                <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-gray-900">Tasks</h2>
                    {homework.tasks.map((task) => {
                        const taskReview = task.reviews.length > 0 ? task.reviews[task.reviews.length - 1] : null;

                        return (
                            <div key={task.id} className="rounded-lg border bg-white p-6 shadow-sm">
                                <div className="flex items-start gap-4">
                                    <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
                                        {task.task_number}
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-gray-900 whitespace-pre-wrap">{task.description}</p>

                                        {task.uploaded_file_url ? (
                                            <div className="mt-4 flex items-center gap-2 rounded-md bg-green-50 p-3">
                                                <CheckCircle className="h-5 w-5 text-green-600" />
                                                <span className="text-sm text-green-800">Submitted</span>
                                                <a
                                                    href={task.uploaded_file_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="ml-auto text-sm text-blue-600 hover:text-blue-800"
                                                >
                                                    View submission
                                                </a>
                                            </div>
                                        ) : (
                                            <div className="mt-4">
                                                <label className="flex cursor-pointer items-center gap-2 rounded-md border border-dashed border-gray-300 p-4 text-center hover:border-blue-500 hover:bg-blue-50">
                                                    <Upload className="h-5 w-5 text-gray-400" />
                                                    <span className="text-sm text-gray-600">
                                                        {uploadingTaskId === task.id ? 'Uploading...' : 'Upload your solution'}
                                                    </span>
                                                    <input
                                                        type="file"
                                                        className="hidden"
                                                        disabled={uploadingTaskId === task.id}
                                                        onChange={(e) => {
                                                            const file = e.target.files?.[0];
                                                            if (file) {
                                                                handleFileUpload(task.id, file);
                                                            }
                                                        }}
                                                    />
                                                </label>
                                            </div>
                                        )}

                                        {taskReview && taskReview.task_feedback && (
                                            <div className="mt-4 rounded-md bg-yellow-50 border border-yellow-200 p-3">
                                                <div className="flex items-start justify-between">
                                                    <p className="text-sm font-medium text-yellow-900">Feedback:</p>
                                                    {taskReview.score !== null && (
                                                        <span className="text-sm font-semibold text-yellow-900">
                                                            Score: {taskReview.score}
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="mt-1 text-sm text-yellow-800 whitespace-pre-wrap">
                                                    {taskReview.task_feedback}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {homework.status === 'pending' && (
                    <button
                        onClick={handleSubmitHomework}
                        disabled={isSubmitting}
                        className="w-full rounded-md bg-blue-600 px-4 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
                    >
                        {isSubmitting ? 'Submitting...' : 'Submit Homework'}
                    </button>
                )}
            </div>
        </div>
    );
}
