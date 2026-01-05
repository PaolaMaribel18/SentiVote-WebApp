import { Home, HelpCircle, GitCompare } from 'lucide-react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPersonBooth } from "@fortawesome/free-solid-svg-icons";

type ViewType = 'home' | 'how-it-works' | 'compare';

interface NavbarProps {
  activeView: ViewType;
  onNavigate: (view: ViewType) => void;
}

export function Navbar({ activeView, onNavigate }: NavbarProps) {
  const navItems = [
    { id: 'home' as ViewType, label: 'Inicio', icon: <Home className="w-5 h-5" /> },
    { id: 'compare' as ViewType, label: 'Comparar', icon: <GitCompare className="w-5 h-5" /> },
    { id: 'how-it-works' as ViewType, label: 'Cómo Funciona', icon: <HelpCircle className="w-5 h-5" /> }


  ];

  return (
    <nav className="bg-white shadow-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate('home')}>
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
              <FontAwesomeIcon icon={faPersonBooth} className=" text-white" />
            </div>
            <span className="text-gray-900">SentiVote Ec</span>
          </div>

          {/* Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${activeView === item.id
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                  }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="p-2 rounded-lg text-gray-600 hover:bg-gray-100">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-4 grid grid-cols-3 gap-2">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex flex-col items-center gap-1 px-2 py-2 rounded-lg transition-all ${activeView === item.id
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              {item.icon}
              <span className="text-xs">{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}
