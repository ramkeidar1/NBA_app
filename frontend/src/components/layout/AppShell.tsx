import type { ReactNode } from 'react';
import TopBar from './TopBar';

interface AppShellProps {
  children: ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <TopBar />
      {children}
    </div>
  );
}
