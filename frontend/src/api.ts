import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Types
export interface Session {
    id: string;
    title: string;
    created_at: string;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    created_at: string;
}

export interface Material {
    id: string;
    name: string;
    file_url: string;
    file_type: string;
    size: number;
    session_id: string;
    uploaded_at: string;
}

export interface HomeworkTaskReview {
    id: string;
    task_feedback: string | null;
    score: number | null;
}

export interface HomeworkReview {
    id: string;
    grade: string | null;
    overall_feedback: string | null;
    reviewed_at: string;
    reviewed_by: string | null;
}

export interface HomeworkTask {
    id: string;
    task_number: number;
    description: string;
    uploaded_file_url: string | null;
    reviews: HomeworkTaskReview[];
}

export interface Homework {
    id: string;
    title: string;
    status: 'pending' | 'submitted' | 'graded';
    session_id: string;
    generated_at: string;
    submitted_at: string | null;
    tasks: HomeworkTask[];
    reviews: HomeworkReview[];
}

export interface MindMap {
    id: string;
    title: string;
    content: string;
    created_at: string;
}

// API Methods
export const chatApi = {
    createSession: (title: string) => api.post<Session>('/api/sessions', { title }),
    getSessions: () => api.get<Session[]>('/api/sessions'),
    sendMessage: (sessionId: string, content: string) => api.post<Message>(`/api/sessions/${sessionId}/messages`, { content }),
    getMessages: (sessionId: string) => api.get<Message[]>(`/api/sessions/${sessionId}/messages`),
};

export const materialsApi = {
    upload: (sessionId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post<Material>(`/api/sessions/${sessionId}/materials`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    list: (sessionId: string) => api.get<Material[]>(`/api/sessions/${sessionId}/materials`),
};

export const homeworkApi = {
    create: (sessionId: string, topic: string, difficulty: string, materialIds: string[] = []) =>
        api.post<Homework>(`/api/sessions/${sessionId}/homework`, {
            prompt: `Create homework on topic: ${topic} with difficulty: ${difficulty}`,
            material_ids: materialIds
        }),
    list: (sessionId: string) =>
        api.get<Homework[]>(`/api/sessions/${sessionId}/homework`),
    get: (homeworkId: string) =>
        api.get<Homework>(`/api/homework/${homeworkId}`),
    uploadTaskSolution: (homeworkId: string, taskId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post<HomeworkTask>(`/api/homework/${homeworkId}/tasks/${taskId}/upload`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    submitHomework: (homeworkId: string) =>
        api.post<Homework>(`/api/homework/${homeworkId}/submit`),
};

export const mindMapsApi = {
    generate: (sessionId: string) => api.post<MindMap>(`/api/sessions/${sessionId}/mind-maps`),
    list: (sessionId: string) => api.get<MindMap[]>(`/api/sessions/${sessionId}/mind-maps`),
};

export default api;
