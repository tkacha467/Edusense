import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Users, ArrowRight } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight mb-4">
          Welcome to EduSense
        </h1>
        <p className="text-lg text-gray-600 max-w-xl mx-auto">
          Choose your portal to begin. Are you here to master new skills or guide student success?
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">
        {/* Student Card */}
        <button
          onClick={() => navigate('/student/login')}
          className="group relative flex flex-col items-center text-center bg-white p-10 rounded-3xl shadow-sm border border-gray-100 hover:shadow-xl hover:border-emerald-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-50 rounded-full blur-3xl -z-10 translate-x-1/3 -translate-y-1/3 group-hover:bg-emerald-100 transition-colors" />
          
          <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <BookOpen className="w-10 h-10" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Student Portal</h2>
          <p className="text-gray-500 mb-8">
            Learn, Practice, Track Progress. Master your subjects and defeat the forgetting curve.
          </p>
          
          <div className="mt-auto flex items-center text-emerald-600 font-semibold">
            Continue as Student <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>

        {/* Faculty Card */}
        <button
          onClick={() => navigate('/faculty/login')}
          className="group relative flex flex-col items-center text-center bg-white p-10 rounded-3xl shadow-sm border border-gray-100 hover:shadow-xl hover:border-blue-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden"
        >
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl -z-10 -translate-x-1/3 translate-y-1/3 group-hover:bg-blue-100 transition-colors" />
          
          <div className="w-20 h-20 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
            <Users className="w-10 h-10" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Faculty Portal</h2>
          <p className="text-gray-500 mb-8">
            Manage Students, Analytics, Predictions. Guide your class to success with data-driven insights.
          </p>
          
          <div className="mt-auto flex items-center text-blue-600 font-semibold">
            Continue as Faculty <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>
      </div>
    </div>
  );
};
