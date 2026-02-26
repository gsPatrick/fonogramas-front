"use client";

export default function Navbar() {
    return (
        <header className="h-16 bg-white border-b border-black/10 flex items-center justify-between px-8 sticky top-0 z-10">
            <div className="flex items-center gap-4">
                <span className="text-sm text-gray-500">SBACEM / Sistema de Fonogramas</span>
            </div>

            <div className="flex items-center gap-6">
                <button className="relative text-gray-600 hover:text-navy-primary">
                    <i className="bi bi-bell text-xl"></i>
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-accent-red text-white text-[10px] flex items-center justify-center rounded-full">3</span>
                </button>
                <div className="h-8 w-[1px] bg-gray-200"></div>
                <button className="text-sm font-medium text-gray-700 hover:text-accent-red transition-colors">
                    Sair <i className="bi bi-box-arrow-right ml-1"></i>
                </button>
            </div>
        </header>
    );
}
