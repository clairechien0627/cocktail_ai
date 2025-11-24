import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Wine, MessageCircle, BookOpen, User, LogOut } from 'lucide-react';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <Wine className="w-8 h-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900">AI 酒保</span>
          </Link>

          {/* 導航連結 */}
          {isAuthenticated && (
            <div className="flex items-center space-x-6">
              <Link
                to="/chat"
                className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition-colors"
              >
                <MessageCircle className="w-5 h-5" />
                <span>AI 對話</span>
              </Link>

              <Link
                to="/cocktails"
                className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition-colors"
              >
                <BookOpen className="w-5 h-5" />
                <span>調酒瀏覽</span>
              </Link>

              <Link
                to="/profile"
                className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition-colors"
              >
                <User className="w-5 h-5" />
                <span>{user?.username}</span>
              </Link>

              <button
                onClick={handleLogout}
                className="flex items-center space-x-1 text-gray-700 hover:text-red-600 transition-colors"
              >
                <LogOut className="w-5 h-5" />
                <span>登出</span>
              </button>
            </div>
          )}

          {!isAuthenticated && (
            <div className="flex items-center space-x-4">
              <Link to="/login" className="text-gray-700 hover:text-primary-600 transition-colors">
                登入
              </Link>
              <Link
                to="/register"
                className="btn-primary"
              >
                註冊
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
