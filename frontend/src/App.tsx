import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';

import { ChatInterface } from './components/chat/ChatInterface';
import { Materials } from './components/materials/Materials';
import { HomeworkList } from './components/homework/HomeworkList';
import { HomeworkDetail } from './components/homework/HomeworkDetail';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

const MindMaps = () => <div className="p-8">Mind Maps Placeholder</div>;

import { SessionProvider } from './contexts/SessionContext';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/" element={
            <ProtectedRoute>
              <SessionProvider>
                <Layout />
              </SessionProvider>
            </ProtectedRoute>
          }>
            <Route index element={<ChatInterface />} />
            <Route path="materials" element={<Materials />} />
            <Route path="homework" element={<HomeworkList />} />
            <Route path="homework/:homeworkId" element={<HomeworkDetail />} />
            <Route path="mind-maps" element={<MindMaps />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
