import { Link, useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { Container } from './layout';
import MobileNav from './MobileNav';

export default function PageHeader({ onMenuClick }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const mainNavItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/poses', label: 'Poses' },
    { path: '/sequences', label: 'Sequences' },
  ];

  return (
    <header className="bg-white border-b border-neutral-200 shadow-sm">
      <Container>
        <div className="py-4 flex items-center justify-between">
          {/* Logo */}
          <h1 className="text-2xl font-bold text-primary-600">YogaFlow</h1>

          {/* Main Navigation - Always visible */}
          <nav className="flex items-center gap-2 sm:gap-4">
            {mainNavItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm sm:text-base font-medium px-2 py-1 sm:px-3 sm:py-2 rounded transition-colors ${
                  isActive(item.path)
                    ? 'text-primary-600 bg-primary-50'
                    : 'text-neutral-700 hover:text-primary-600 hover:bg-neutral-50'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Menu Button */}
          <MobileNav />
        </div>
      </Container>
    </header>
  );
}
