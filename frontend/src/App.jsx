import { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';

// Eager load auth pages (small, needed immediately)
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

// Lazy load main app pages (code splitting)
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Poses = lazy(() => import('./pages/Poses'));
const PoseDetail = lazy(() => import('./pages/PoseDetail'));
const Sequences = lazy(() => import('./pages/Sequences'));
const PracticePrep = lazy(() => import('./pages/PracticePrep'));
const PracticeSession = lazy(() => import('./pages/PracticeSession'));
const PracticeComplete = lazy(() => import('./pages/PracticeComplete'));
const History = lazy(() => import('./pages/History'));
const Statistics = lazy(() => import('./pages/Statistics'));
const Profile = lazy(() => import('./pages/Profile'));

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
      <p className="text-gray-600">Loading...</p>
    </div>
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/poses"
          element={
            <ProtectedRoute>
              <Poses />
            </ProtectedRoute>
          }
        />
        <Route
          path="/poses/:id"
          element={
            <ProtectedRoute>
              <PoseDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/sequences"
          element={
            <ProtectedRoute>
              <Sequences />
            </ProtectedRoute>
          }
        />
        <Route
          path="/practice/prep/:sequenceId"
          element={
            <ProtectedRoute>
              <PracticePrep />
            </ProtectedRoute>
          }
        />
        <Route
          path="/practice/:sequenceId"
          element={
            <ProtectedRoute>
              <PracticeSession />
            </ProtectedRoute>
          }
        />
        <Route
          path="/practice/complete"
          element={
            <ProtectedRoute>
              <PracticeComplete />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />
        <Route
          path="/stats"
          element={
            <ProtectedRoute>
              <Statistics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

            {/* 404 fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
