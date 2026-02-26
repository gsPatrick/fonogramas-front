import './globals.css';
import Sidebar from '@/components/layout/Sidebar/Sidebar';
import Navbar from '@/components/layout/Navbar/Navbar';

export const metadata = {
  title: 'Fonogramas Core | SBACEM',
  description: 'Sistema Moderno de Gestão de Fonogramas e Direitos Conexos',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" />
      </head>
      <body>
        <div className="layout-root">
          <Sidebar />
          <div className="flex-1 flex flex-col min-h-screen">
            <Navbar />
            <main className="main-content">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
