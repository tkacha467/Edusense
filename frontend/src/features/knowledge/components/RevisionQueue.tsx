import React from 'react';
import { Calendar, Clock, ArrowRight, BookOpen } from 'lucide-react';
import { useRevisionQueue } from '../hooks/useRevisionQueue';
import { Button } from '../../../components/ui/Button';

export function RevisionQueue() {
  const { data: tasks, isLoading, error } = useRevisionQueue();

  if (isLoading) {
    return (
      <div className="bg-white border p-6 rounded-2xl shadow-sm flex items-center justify-center min-h-[180px]">
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !tasks) {
    return (
      <div className="bg-white border p-6 rounded-2xl shadow-sm text-center text-xs text-red-500">
        Failed to load revision queue.
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-2xl p-6 shadow-sm space-y-4">
      <div className="flex justify-between items-center pb-2 border-b">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-primary" /> Today's Revision Queue
        </h3>
        <span className="text-xs bg-primary/10 text-primary font-bold px-2.5 py-0.5 rounded-full">
          {tasks.length} {tasks.length === 1 ? 'Task' : 'Tasks'}
        </span>
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-xs text-gray-400 space-y-2">
          <BookOpen className="w-8 h-8 mx-auto opacity-40 text-gray-400" />
          <p>Your memory index trace is stable! No revision recommended today.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((task) => (
            <div 
              key={task.id} 
              className="flex justify-between items-center p-4 border rounded-xl hover:border-primary/30 transition-all bg-gray-50/50 hover:bg-white"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    task.priority === 'HIGH' ? 'bg-rose-50 text-rose-600 border border-rose-100' :
                    task.priority === 'MEDIUM' ? 'bg-amber-50 text-amber-600 border border-amber-100' :
                    'bg-gray-50 text-gray-600 border border-gray-100'
                  }`}>
                    {task.priority} Priority
                  </span>
                  <span className="text-xs text-gray-400 font-medium flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> {task.estimated_minutes} mins
                  </span>
                </div>
                <h4 className="font-extrabold text-sm text-gray-800">{task.title}</h4>
              </div>
              
              <Button size="sm" variant="ghost" className="text-primary hover:text-primary hover:bg-primary/5 rounded-xl text-xs gap-1">
                Revise <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
