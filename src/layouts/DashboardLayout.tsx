import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Megaphone,
  Bot,
  History,
  Users,
  CreditCard,
  ShieldCheck,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bell,
  Search,
  User,
  Phone
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

export default function DashboardLayout() {
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  let user = null;
  try {
    const userString = localStorage.getItem('user');
    user = userString ? JSON.parse(userString) : null;
  } catch (e) {
    console.error("Failed to parse user from localStorage", e);
  }

  React.useEffect(() => {
    if (!localStorage.getItem('access_token')) {
      navigate('/login');
    }
  }, [navigate]);

  const menuItems = [
    { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Campaigns', href: '/dashboard/campaigns', icon: Megaphone },
    { name: 'AI Agent Builder', href: '/dashboard/agent-builder', icon: Bot },
    { name: 'Call Logs', href: '/dashboard/call-logs', icon: History },
    { name: 'Contacts', href: '/dashboard/contacts', icon: Users },
    { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
    { name: 'Admin Panel', href: '/dashboard/admin', icon: ShieldCheck },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ];

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: isCollapsed ? 80 : 260 }}
        className="relative bg-card border-r border-border flex flex-col z-20"
      >
        <div className="p-6 flex items-center justify-between">
          {!isCollapsed && (
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded flex items-center justify-center neon-glow">
                <Phone className="text-black w-5 h-5" />
              </div>
              <span className="text-xl font-bold font-display tracking-tight">Beraxis</span>
            </Link>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center mx-auto neon-glow">
              <Phone className="text-black w-5 h-5" />
            </div>
          )}
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto no-scrollbar">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all group",
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                )}
              >
                <item.icon className={cn("w-5 h-5 shrink-0", isActive ? "text-primary" : "group-hover:text-primary")} />
                {!isCollapsed && <span className="text-sm font-medium">{item.name}</span>}
                {isCollapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-card border border-border rounded text-xs opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
                    {item.name}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <button
            onClick={handleLogout}
            className={cn(
              "flex items-center space-x-3 px-3 py-2.5 w-full rounded-lg text-muted-foreground hover:bg-red-500/10 hover:text-red-500 transition-all group"
            )}
          >
            <LogOut className="w-5 h-5 shrink-0" />
            {!isCollapsed && <span className="text-sm font-medium">Logout</span>}
          </button>
        </div>

        {/* Collapse Toggle */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute -right-3 top-20 w-6 h-6 bg-card border border-border rounded-full flex items-center justify-center hover:bg-muted transition-colors z-30"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </motion.aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-8 z-10">
          <div className="flex items-center space-x-4 flex-1 max-w-xl">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search anything..."
                className="w-full bg-muted/50 border border-border rounded-full pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary transition-all"
              />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button className="p-2 text-muted-foreground hover:text-primary transition-colors relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-primary rounded-full neon-glow"></span>
            </button>
            <div className="h-8 w-px bg-border mx-2"></div>
            <div className="flex items-center space-x-3 cursor-pointer group">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium group-hover:text-primary transition-colors">{user?.full_name || 'User'}</p>
                <p className="text-xs text-muted-foreground">{user?.role === 'owner' ? 'Admin Account' : 'Agent Account'}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center group-hover:border-primary transition-all">
                <User className="w-6 h-6 text-primary" />
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-8 no-scrollbar">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
