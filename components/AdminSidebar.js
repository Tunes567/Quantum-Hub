import { useRouter } from 'next/router';
import Link from 'next/link';

export default function AdminSidebar() {
  const router = useRouter();
  
  const menuItems = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/users', label: 'Users', icon: '👥' },
    { href: '/messages', label: 'Messages', icon: '✉️' },
    { href: '/payments', label: 'Payments', icon: '💰' },
    { href: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="bg-gray-800 text-white w-64 min-h-screen p-4">
      <div className="text-2xl font-bold mb-8 text-center">
        Admin Panel
      </div>
      <nav>
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`
              flex items-center gap-3 px-4 py-3 rounded-lg mb-2
              ${router.pathname === item.href 
                ? 'bg-blue-600 text-white' 
                : 'hover:bg-gray-700'}
            `}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
} 