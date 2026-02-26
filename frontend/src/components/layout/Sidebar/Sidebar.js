"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Sidebar() {
    const pathname = usePathname();

    const menuItems = [
        { name: 'Dashboard', path: '/', icon: 'bi-grid' },
        { name: 'Fonogramas', path: '/fonogramas', icon: 'bi-music-note-beamed' },
        { name: 'Importar Lote', path: '/lote', icon: 'bi-cloud-arrow-up' },
        { name: 'ECAD Envios', path: '/ecad/envios', icon: 'bi-file-earmark-arrow-up' },
        { name: 'Retornos ECAD', path: '/ecad/retornos', icon: 'bi-file-earmark-arrow-down' },
        { name: 'Configurações', path: '/admin/config', icon: 'bi-gear' },
    ];

    return (
        <aside className="w-64 bg-navy-primary text-white flex flex-col h-screen sticky top-0">
            <div className="p-6 border-b border-white/10">
                <h1 className="text-xl font-bold tracking-tight">FONOGRAMAS <span className="text-accent-red italic">CORE</span></h1>
            </div>

            <nav className="flex-1 mt-6 px-4 space-y-1">
                {menuItems.map((item) => {
                    const isActive = pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            href={item.path}
                            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${isActive
                                    ? 'bg-accent-red text-white shadow-lg'
                                    : 'hover:bg-white/5 text-white/70 hover:text-white'
                                }`}
                        >
                            <i className={`bi ${item.icon} text-lg`}></i>
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-white/10">
                <div className="flex items-center gap-3 px-2 py-2">
                    <div className="w-8 h-8 rounded-full bg-accent-red flex items-center justify-center font-bold">
                        P
                    </div>
                    <div>
                        <p className="text-xs text-white/50 uppercase tracking-widest">Usuário</p>
                        <p className="text-sm font-semibold">Patrick Siqueira</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
