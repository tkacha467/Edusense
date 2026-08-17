import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { studentOnboardingSchema } from '../../../utils/validations';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '../../../components/ui/Form';
import { Button } from '../../../components/ui/Button';
import { 
  BrainCircuit, 
  BookOpen, 
  GraduationCap, 
  CheckCircle2, 
  ChevronRight, 
  ArrowLeft,
  Sparkles,
  Award,
  Layers,
  Code,
  Database,
  Cpu,
  Lock,
  Zap,
  Play
} from 'lucide-react';
import { z } from 'zod';
import { useAuth } from '../../../contexts/AuthContext';
import apiClient from '../../../api/apiClient';

// Academic Hierarchy Catalog Data
const UG_STREAMS = [
  { id: 'BCA', name: 'BCA (Bachelor of Computer Applications)', icon: Code, desc: 'Software Development, Web Apps, Database Systems' },
  { id: 'B.Sc. Data Science', name: 'B.Sc. Data Science', icon: Database, desc: 'Python, Applied Statistics, Data Visualization' },
  { id: 'B.Sc. Computer Science', name: 'B.Sc. Computer Science', icon: Cpu, desc: 'C/C++, Operating Systems, Computer Architecture' },
  { id: 'Computer Engineering', name: 'B.Tech / B.E. Computer Engineering', icon: BrainCircuit, desc: 'Pipelining, System Design, Embedded Systems' },
  { id: 'B.Sc. Information Technology', name: 'B.Sc. Information Technology', icon: Layers, desc: 'Networking, Cyber Security Fundamentals, Web APIs' },
];

const PG_STREAMS = [
  { id: 'MCA', name: 'MCA (Master of Computer Applications)', icon: Code, desc: 'Advanced Java, Spring Boot, Microservices, Cloud DevOps' },
  { id: 'M.Sc. Data Science', name: 'M.Sc. Data Science', icon: Database, desc: 'Machine Learning, Deep Neural Networks, PySpark Big Data' },
  { id: 'M.Sc. Cyber Security', name: 'M.Sc. Cyber Security', icon: Lock, desc: 'Ethical Hacking, Cryptography, Network Defense' },
  { id: 'M.Sc. Computer Science', name: 'M.Sc. Computer Science', icon: Cpu, desc: 'Advanced Algorithms, Distributed Systems, AI Logic' },
  { id: 'M.Tech Computer Engineering', name: 'M.Tech Computer Engineering', icon: BrainCircuit, desc: 'Parallel Computing, High Performance GPU Systems' },
];

const SCHOOL_GRADE_OPTIONS = {
  middle_school: [
    { value: '6', label: '6th Grade' },
    { value: '7', label: '7th Grade' },
    { value: '8', label: '8th Grade' },
  ],
  high_school: [
    { value: '9', label: '9th Std (Freshman)' },
    { value: '10', label: '10th Std (Board Exams)' },
    { value: '11', label: '11th Std (Junior)' },
    { value: '12', label: '12th Std (Senior / Board Exams)' },
  ],
};

export function Onboarding() {
  const navigate = useNavigate();
  const { updateProfile } = useAuth();
  
  // Step State: 1 = Education Tier, 2 = Degree Stream Selection, 3 = Subject & Topic Selection
  const [step, setStep] = useState<number>(1);
  const [degreeLevel, setDegreeLevel] = useState<'UG' | 'PG'>('UG');
  const [selectedStream, setSelectedStream] = useState<string>('BCA');
  
  // Real Backend Subject & Topic Items
  const [backendSubjects, setBackendSubjects] = useState<any[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<any | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<any | null>(null);
  const [loadingSubjects, setLoadingSubjects] = useState<boolean>(false);

  const form = useForm<z.infer<typeof studentOnboardingSchema>>({
    resolver: zodResolver(studentOnboardingSchema),
    defaultValues: {
      schoolType: 'college',
      grade: '',
      degreeLevel: 'UG',
      stream: 'BCA',
      skillsToTrack: [],
    },
  });

  const watchSchoolType = form.watch('schoolType');

  // Load backend subjects matching selected stream/department
  useEffect(() => {
    async function fetchSubjects() {
      setLoadingSubjects(true);
      try {
        const res = await apiClient.get('/learning/subjects');
        if (res.data && Array.isArray(res.data)) {
          setBackendSubjects(res.data);
        }
      } catch (e) {
        console.error('Failed to load subjects from API', e);
      } finally {
        setLoadingSubjects(false);
      }
    }
    fetchSubjects();
  }, []);

  // Filter subjects for the selected degree stream
  const filteredSubjects = useMemo(() => {
    if (!backendSubjects || backendSubjects.length === 0) return [];
    return backendSubjects.filter(subj => {
      const cat = (subj.category || '').toLowerCase();
      const code = (subj.code || '').toLowerCase();
      const str = selectedStream.toLowerCase();
      return cat.includes(str) || code.includes(str) || str.includes(cat);
    });
  }, [backendSubjects, selectedStream]);

  // Handle Complete Onboarding & Save
  const onSubmit = async () => {
    try {
      await apiClient.post('/onboarding/complete');
      await updateProfile({ onboardingCompleted: true });

      // Navigate to Assessment if topic selected, else dashboard
      if (selectedSubject) {
        navigate('/assessment', { state: { subjectId: selectedSubject.id, topicId: selectedTopic?.id } });
      } else {
        navigate('/student/dashboard');
      }
    } catch (e) {
      console.error('Onboarding submit error', e);
      navigate('/student/dashboard');
    }
  };

  const handleNextStep = () => {
    if (step === 1) {
      if (watchSchoolType === 'college') {
        setStep(2);
      } else {
        setStep(3);
      }
    } else if (step === 2) {
      setStep(3);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <div className="w-full bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="h-6 w-6 text-indigo-400" />
          <span className="text-xl font-bold tracking-tight text-white">EduSense AI</span>
        </div>
        <div className="flex gap-2">
          <div className={`h-2 w-12 rounded-full ${step >= 1 ? 'bg-indigo-500' : 'bg-slate-800'}`} />
          <div className={`h-2 w-12 rounded-full ${step >= 2 ? 'bg-indigo-500' : 'bg-slate-800'}`} />
          <div className={`h-2 w-12 rounded-full ${step >= 3 ? 'bg-indigo-500' : 'bg-slate-800'}`} />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-3xl bg-slate-900 rounded-2xl shadow-2xl border border-slate-800 p-6 md:p-10">
          
          {/* Header Title */}
          <div className="text-center mb-8">
            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full border border-indigo-500/20">
              Personalized Learning Onboarding
            </span>
            <h1 className="text-2xl md:text-3xl font-bold text-white mt-3">
              {step === 1 && "Tell us about your education"}
              {step === 2 && "Select your Degree & Academic Stream"}
              {step === 3 && "Choose Course Subject & Exam Topic"}
            </h1>
            <p className="text-slate-400 text-xs md:text-sm mt-1.5">
              {step === 1 && "Filters subjects and personalized Ebbinghaus retention decay curves."}
              {step === 2 && "Choose your exact UG/PG degree program for targeted exam assessment."}
              {step === 3 && "Select a course subject to initialize customized retrieval practice."}
            </p>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              {/* STEP 1: School Type & Filtered Grade Options */}
              {step === 1 && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <FormField
                    control={form.control}
                    name="schoolType"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xs text-slate-300 font-semibold uppercase tracking-wider">Education Level</FormLabel>
                        <FormControl>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {[
                              { id: 'middle_school', label: 'Middle School (6th - 8th)', icon: BookOpen, desc: 'Foundational Maths & Basic Science' },
                              { id: 'high_school', label: 'High School (9th - 12th Std)', icon: GraduationCap, desc: 'Board Exams, PCM/PCB, Science' },
                              { id: 'college', label: 'College / University (UG & PG)', icon: GraduationCap, desc: 'BCA, MCA, B.Sc, M.Sc Data Science, Engineering' },
                              { id: 'other', label: 'Competitive Exams / Other', icon: CheckCircle2, desc: 'GATE, GRE, Technical Certifications' }
                            ].map((type) => (
                              <button
                                key={type.id}
                                type="button"
                                onClick={() => {
                                  field.onChange(type.id);
                                  if (type.id === 'college') {
                                    form.setValue('degreeLevel', 'UG');
                                    form.setValue('stream', 'BCA');
                                  }
                                }}
                                className={`flex flex-col text-left p-5 rounded-xl border transition-all ${
                                  field.value === type.id 
                                    ? 'border-indigo-500 bg-indigo-600/10 text-white shadow-lg' 
                                    : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                                }`}
                              >
                                <div className="flex items-center space-x-3 mb-2">
                                  <type.icon className="w-5 h-5 text-indigo-400" />
                                  <span className="font-bold text-sm text-white">{type.label}</span>
                                </div>
                                <p className="text-[11px] text-slate-400">{type.desc}</p>
                              </button>
                            ))}
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Filtered Grade Dropdown for Middle / High School */}
                  {watchSchoolType !== 'college' && watchSchoolType !== 'other' && (
                    <FormField
                      control={form.control}
                      name="grade"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-xs text-slate-300 font-semibold uppercase tracking-wider">
                            Current Standard / Grade Level
                          </FormLabel>
                          <FormControl>
                            <select 
                              className="flex h-11 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 cursor-pointer"
                              {...field}
                            >
                              <option value="">Select relevant grade...</option>
                              {watchSchoolType === 'middle_school' && SCHOOL_GRADE_OPTIONS.middle_school.map(g => (
                                <option key={g.value} value={g.value}>{g.label}</option>
                              ))}
                              {watchSchoolType === 'high_school' && SCHOOL_GRADE_OPTIONS.high_school.map(g => (
                                <option key={g.value} value={g.value}>{g.label}</option>
                              ))}
                            </select>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}

                  <Button type="button" className="w-full h-11 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl shadow-lg" onClick={handleNextStep}>
                    Continue to Stream Selection <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              )}

              {/* STEP 2: College UG / PG Degree Stream Selection */}
              {step === 2 && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  {/* UG vs PG Toggle */}
                  <div className="flex items-center justify-center space-x-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800 max-w-sm mx-auto">
                    <button
                      type="button"
                      onClick={() => {
                        setDegreeLevel('UG');
                        setSelectedStream('BCA');
                      }}
                      className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                        degreeLevel === 'UG' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Undergraduate (UG)
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setDegreeLevel('PG');
                        setSelectedStream('MCA');
                      }}
                      className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                        degreeLevel === 'PG' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Postgraduate (PG)
                    </button>
                  </div>

                  {/* Degree Stream Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {(degreeLevel === 'UG' ? UG_STREAMS : PG_STREAMS).map((st) => (
                      <button
                        key={st.id}
                        type="button"
                        onClick={() => setSelectedStream(st.id)}
                        className={`flex flex-col text-left p-4 rounded-xl border transition-all ${
                          selectedStream === st.id 
                            ? 'border-indigo-500 bg-indigo-600/10 text-white shadow-lg' 
                            : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                        }`}
                      >
                        <div className="flex items-center space-x-3 mb-1.5">
                          <st.icon className="w-4 h-4 text-indigo-400" />
                          <span className="font-bold text-xs text-white">{st.name}</span>
                        </div>
                        <p className="text-[11px] text-slate-400">{st.desc}</p>
                      </button>
                    ))}
                  </div>

                  <div className="flex items-center space-x-3 pt-2">
                    <Button type="button" variant="outline" className="h-11 text-xs border-slate-800 text-slate-300" onClick={() => setStep(1)}>
                      <ArrowLeft className="w-4 h-4 mr-2" /> Back
                    </Button>
                    <Button type="button" className="flex-1 h-11 text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl shadow-lg" onClick={handleNextStep}>
                      View {selectedStream} Course Subjects <ChevronRight className="w-4 h-4 ml-2" />
                    </Button>
                  </div>
                </div>
              )}

              {/* STEP 3: Subject & Exam Topic Selection */}
              {step === 3 && (
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="space-y-3">
                    <label className="text-xs text-slate-300 font-semibold uppercase tracking-wider">
                      Course Subjects ({selectedStream})
                    </label>

                    {loadingSubjects ? (
                      <div className="p-8 text-center text-xs text-slate-400">Loading course subjects from database...</div>
                    ) : filteredSubjects.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {filteredSubjects.map(sub => (
                          <div
                            key={sub.id}
                            onClick={() => {
                              setSelectedSubject(sub);
                              setSelectedTopic(sub.topics && sub.topics.length > 0 ? sub.topics[0] : null);
                            }}
                            className={`p-4 rounded-xl border cursor-pointer transition-all ${
                              selectedSubject?.id === sub.id
                                ? 'border-indigo-500 bg-indigo-600/10 text-white shadow-lg'
                                : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                            }`}
                          >
                            <span className="text-[10px] font-mono text-indigo-400 font-bold uppercase">{sub.code}</span>
                            <h4 className="text-xs font-bold text-white mt-0.5">{sub.name}</h4>
                            <span className="text-[10px] text-slate-400 mt-1 block">Semester {sub.semester} • {sub.category}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-6 bg-slate-950 border border-slate-800 rounded-xl text-center text-xs text-slate-400">
                        Showing standard subjects for {selectedStream}.
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 pt-4">
                    <Button type="button" variant="outline" className="h-11 text-xs border-slate-800 text-slate-300" onClick={() => setStep(watchSchoolType === 'college' ? 2 : 1)}>
                      <ArrowLeft className="w-4 h-4 mr-2" /> Back
                    </Button>
                    <Button type="submit" className="flex-1 h-11 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl shadow-lg flex items-center justify-center space-x-2">
                      <Play className="w-4 h-4" />
                      <span>Start Adaptive Assessment Examination</span>
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

export default Onboarding;
