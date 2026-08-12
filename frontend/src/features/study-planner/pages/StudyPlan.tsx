import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { PlayCircle } from 'lucide-react';
import { Button } from '../../../components/ui/Button';
import { useAuth } from '../../../contexts/AuthContext';
import type { StudentProfile } from '../../../types';

export function StudyPlan() {
  const { currentUser } = useAuth();
  
  if (!currentUser || currentUser.role !== 'student') return null;
  const profile = currentUser as Partial<StudentProfile>;
  const studyPlan = Array.isArray(profile?.studyPlan) ? profile.studyPlan : [];

  return (
    <div className="space-y-6 animate-in fade-in zoom-in-95 duration-300">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Your Study Plan</h1>
        <p className="text-muted-foreground mt-1">Personalized recommendations based on your learning curve.</p>
      </div>

      {studyPlan.length === 0 ? (
        <div className="bg-white border rounded-xl p-12 text-center shadow-sm">
          <h2 className="text-xl font-bold text-gray-900 mb-2">No Study Plan Yet</h2>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            Take your first assessment module to establish your baseline. EduSense AI will generate a personalized study plan for you immediately after.
          </p>
          <Button>Browse Learning Modules</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {studyPlan.map((item, index) => {
            const isUrgent = item.status === 'urgent';
            const isCompleted = item.status === 'completed';
            const color = isCompleted ? 'bg-emerald-500' : (isUrgent ? 'bg-red-500' : 'bg-blue-500');
            const textColor = color.replace('bg-', 'text-');
            
            return (
              <Card key={index} className="overflow-hidden hover:shadow-md transition-shadow">
                <div className={`h-2 w-full ${color}`} />
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg font-bold">{item.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="mb-4">
                    <div className="flex justify-between items-end mb-1">
                      <span className="text-sm font-medium text-gray-500">Status</span>
                      <span className={`text-sm font-bold ${textColor}`}>{item.status.toUpperCase()}</span>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500 mb-6">
                    Type: <span className="font-medium text-gray-900">{item.type}</span> • {item.time}
                  </div>

                  <Button 
                    className="w-full bg-white text-gray-900 border-gray-200 hover:bg-gray-50" 
                    variant="outline"
                    disabled={isCompleted}
                  >
                    <PlayCircle className="w-4 h-4 mr-2 text-primary" /> 
                    {isCompleted ? 'Completed' : 'Practice Module'}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
