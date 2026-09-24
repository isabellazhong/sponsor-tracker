import { Navigate, Route, Routes } from 'react-router-dom';

import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { WorkspacesPage } from './pages/WorkspacesPage';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/workspaces" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/workspaces" element={<WorkspacesPage />} />
      <Route path="/w/:workspaceId" element={<WorkspacePage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
