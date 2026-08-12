import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { studentOnboardingSchema } from '../../../utils/validations';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '../../../components/ui/Form';
import { Button } from '../../../components/ui/Button';
import { BrainCircuit, BookOpen, GraduationCap, CheckCircle2, ChevronRight } from 'lucide-react';
import { z } from 'zod';
import { useAuth } from '../../../contexts/AuthContext';
import apiClient from '../../../api/apiClient';

const AVAILABLE_SKILLS = [
  { id: 'addition', label: 'Addition & Subtraction', category: 'Math' },
  { id: 'multiplication', label: 'Multiplication & Division', category: 'Math' },
  { id: 'fraction-division', label: 'Fraction Division', category: 'Math' },
  { id: 'algebra', label: 'Algebraic Equations', category: 'Math' },
  { id: 'geometry', label: 'Geometry', category: 'Math' },
  { id: 'physics-kinematics', label: 'Kinematics', category: 'Science' },
  { id: 'chemistry-bonds', label: 'Chemical Bonds', category: 'Science' },
];

export function Onboarding() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  const form = useForm<z.infer<typeof studentOnboardingSchema>>({
    resolver: zodResolver(studentOnboardingSchema),
    defaultValues: {
      grade: '',
      schoolType: 'high_school',
      skillsToTrack: [],
    },
  });

  const { updateProfile } = useAuth();

  const onSubmit = async (values: z.infer<typeof studentOnboardingSchema>) => {
    try {
      // 1. You could call /api/v1/onboarding/institution etc. here if needed.
      // 2. Call complete onboarding endpoint
      await apiClient.post('/onboarding/complete');
      
      // Update local profile state to prevent 403 Forbidden
      await updateProfile({ onboardingCompleted: true });
      
      // Save profile and redirect to dashboard
      navigate('/student/dashboard');
    } catch (e) {
      console.error('Onboarding failed', e);
      // Fallback redirect just in case
      navigate('/student/dashboard');
    }
  };

  const nextStep = async () => {
    const fieldsToValidate = step === 1 ? ['grade', 'schoolType'] : ['skillsToTrack'];
    const isValid = await form.trigger(fieldsToValidate as any);
    if (isValid) setStep(2);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top Bar */}
      <div className="w-full bg-white border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold tracking-tight">EduSense</span>
        </div>
        <div className="flex gap-2">
          <div className={`h-2 w-12 rounded-full ${step >= 1 ? 'bg-primary' : 'bg-gray-200'}`} />
          <div className={`h-2 w-12 rounded-full ${step >= 2 ? 'bg-primary' : 'bg-gray-200'}`} />
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-2xl bg-white rounded-2xl shadow-sm border p-8 md:p-12">
          
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-gray-900 mb-3">
              {step === 1 ? "Tell us about your education" : "What do you want to master?"}
            </h1>
            <p className="text-gray-500">
              {step === 1 
                ? "This helps us personalize your learning retention curve." 
                : "Select the subjects and skills you want EduSense to track for knowledge decay."}
            </p>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              
              {step === 1 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <FormField
                    control={form.control}
                    name="schoolType"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base">School Type</FormLabel>
                        <FormControl>
                          <div className="grid grid-cols-2 gap-4">
                            {[
                              { id: 'middle_school', label: 'Middle School', icon: BookOpen },
                              { id: 'high_school', label: 'High School', icon: GraduationCap },
                              { id: 'college', label: 'College / Uni', icon: GraduationCap },
                              { id: 'other', label: 'Other', icon: CheckCircle2 }
                            ].map((type) => (
                              <button
                                key={type.id}
                                type="button"
                                onClick={() => field.onChange(type.id)}
                                className={`flex flex-col items-center justify-center p-6 rounded-xl border-2 transition-all ${
                                  field.value === type.id 
                                    ? 'border-primary bg-primary/5 text-primary' 
                                    : 'border-gray-100 hover:border-primary/30 text-gray-600'
                                }`}
                              >
                                <type.icon className="w-8 h-8 mb-3" />
                                <span className="font-semibold">{type.label}</span>
                              </button>
                            ))}
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="grade"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-base">Current Grade / Year</FormLabel>
                        <FormControl>
                          <select 
                            className="flex h-12 w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
                            {...field}
                          >
                            <option value="">Select your grade...</option>
                            <option value="6">6th Grade</option>
                            <option value="7">7th Grade</option>
                            <option value="8">8th Grade</option>
                            <option value="9">Freshman (9th)</option>
                            <option value="10">Sophomore (10th)</option>
                            <option value="11">Junior (11th)</option>
                            <option value="12">Senior (12th)</option>
                            <option value="college_1">College Freshman</option>
                          </select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button type="button" className="w-full h-12 text-lg" onClick={nextStep}>
                    Continue <ChevronRight className="w-5 h-5 ml-2" />
                  </Button>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
                  
                  <FormField
                    control={form.control}
                    name="skillsToTrack"
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {AVAILABLE_SKILLS.map((skill) => {
                              const isSelected = field.value?.includes(skill.id);
                              return (
                                <button
                                  key={skill.id}
                                  type="button"
                                  onClick={() => {
                                    const current = new Set(field.value || []);
                                    if (current.has(skill.id)) {
                                      current.delete(skill.id);
                                    } else {
                                      current.add(skill.id);
                                    }
                                    field.onChange(Array.from(current));
                                  }}
                                  className={`flex items-start text-left p-4 rounded-xl border-2 transition-all ${
                                    isSelected
                                      ? 'border-primary bg-primary/5'
                                      : 'border-gray-100 hover:border-gray-200 bg-white'
                                  }`}
                                >
                                  <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 mr-3 ${isSelected ? 'bg-primary border-primary text-white' : 'border-gray-300'}`}>
                                    {isSelected && <CheckCircle2 className="w-3 h-3" />}
                                  </div>
                                  <div>
                                    <div className={`font-semibold ${isSelected ? 'text-primary' : 'text-gray-900'}`}>{skill.label}</div>
                                    <div className="text-xs text-gray-500 mt-1">{skill.category}</div>
                                  </div>
                                </button>
                              );
                            })}
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <div className="flex gap-4">
                    <Button type="button" variant="outline" className="w-1/3 h-12" onClick={() => setStep(1)}>
                      Back
                    </Button>
                    <Button type="submit" className="w-2/3 h-12 text-lg">
                      Complete Setup <CheckCircle2 className="w-5 h-5 ml-2" />
                    </Button>
                  </div>
                </div>
              )}

            </form>
          </Form>
        </div>
      </div>
    </div>
  );
}
