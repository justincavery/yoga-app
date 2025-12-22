import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, LogOut, Home, BookOpen, Layers, User, BarChart3, History } from 'lucide-react';
import { Button } from './ui';
import useAuthStore from '../store/authStore';

export default function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    setIsOpen(false);
    navigate('/login');
  };

  const handleNavigation = (path) => {
    setIsOpen(false);
    navigate(path);
  };

  const navItems = [
    { path: '/history', label: 'History', icon: History },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  return (
    <>
      {/* Menu Button - Always visible */}
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 text-neutral-700 hover:text-primary-600 transition-colors"
        aria-label="Open menu"
      >
        <Menu size={24} />
      </button>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Slide-out Menu */}
      <div
        className={`fixed top-0 right-0 bottom-0 w-72 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-neutral-200">
          <h2 className="text-xl font-bold text-primary-600">YogaFlow</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 text-neutral-700 hover:text-primary-600 transition-colors"
            aria-label="Close navigation menu"
          >
            <X size={24} />
          </button>
        </div>

        {/* User Info */}
        {user && (
          <div className="p-4 bg-neutral-50 border-b border-neutral-200">
            <p className="text-sm font-medium text-neutral-900">{user.name}</p>
            <p className="text-xs text-neutral-600">{user.email}</p>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path}>
                  <button
                    onClick={() => handleNavigation(item.path)}
                    className="w-full flex items-center gap-3 px-4 py-3 text-neutral-700 hover:bg-primary-50 hover:text-primary-600 rounded-lg transition-colors"
                  >
                    <Icon size={20} />
                    <span className="font-medium">{item.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-neutral-200">
          <Button
            variant="outline"
            onClick={handleLogout}
            icon={<LogOut size={20} />}
            fullWidth
          >
            Logout
          </Button>
        </div>
      </div>
    </>
  );
}
