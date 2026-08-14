import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StudentDataProvider } from '../features/faculty/context/StudentDataContext';

export function AppLayout() {
  return (
    <StudentDataProvider>
      <div className="flex h-screen overflow-hidden bg-gray-50/50">
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto outline-none" tabIndex={-1}>
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 h-full">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </StudentDataProvider>
  );
}
