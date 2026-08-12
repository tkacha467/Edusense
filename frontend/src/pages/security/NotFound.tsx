import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Search, Home } from 'lucide-react';
import { Button } from '../../components/ui/Button';

export function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center">
      <div className="bg-orange-100 p-4 rounded-full mb-6 text-orange-600">
        <AlertCircle className="w-12 h-12" />
      </div>
      <h1 className="text-4xl sm:text-6xl font-extrabold text-gray-900 tracking-tight mb-4">404</h1>
      <h2 className="text-2xl font-semibold text-gray-700 mb-6">Page not found</h2>
      <p className="text-muted-foreground max-w-md mx-auto mb-10 leading-relaxed">
        We couldn't find the page you're looking for. It might have been removed, had its name changed, or is temporarily unavailable.
      </p>
      
      <div className="flex flex-col sm:flex-row gap-4 w-full max-w-sm">
        <Button onClick={() => navigate('/dashboard')} className="flex-1 h-12 text-base">
          <Home className="w-4 h-4 mr-2" />
          Go to Dashboard
        </Button>
        <Button variant="outline" onClick={() => navigate(-1)} className="flex-1 h-12 text-base bg-white">
          <Search className="w-4 h-4 mr-2" />
          Go Back
        </Button>
      </div>
    </div>
  );
}
