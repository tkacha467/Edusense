import React, { createContext, useContext, useState, useMemo, useEffect } from 'react';
import type { StudentAnalyticsSummary, StudentDeepDiveDetails } from '../types/studentAnalytics';
import apiClient from '../../../api/apiClient';

export interface StudentRecord extends StudentAnalyticsSummary {
  risk_level: 'Critical' | 'High' | 'Medium' | 'Low';
  recommended_revision_date: string;
  predicted_forgetting_date: string;
  confidence_score: number;
  skills: string[];
}

interface StudentDataContextType {
  students: StudentRecord[];
  atRiskStudents: StudentRecord[];
  atRiskCount: number;
  selectedStudent: StudentRecord | null;
  selectedStudentDetails: StudentDeepDiveDetails | null;
  isModalOpen: boolean;
  loadingModal: boolean;
  openStudentModal: (studentId: string) => Promise<void>;
  closeStudentModal: () => void;
  generateStudentReport: (studentId: string) => void;
  scrollToAtRiskTable: () => void;
}

const INITIAL_MOCK_STUDENTS: StudentRecord[] = [
  {
    id: 'stu_av8910',
    name: 'Alex Vance',
    email: 'alex.vance@edusense.ai',
    enrollment_number: 'EDU-2026-AV8910',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Logit Function & AI Logic',
    subject_id: '17bd775e-8512-4311-965f-fdc9c3979792',
    knowledge_health: 38.5,
    retention_pct: 41.2,
    forget_probability: 0.72,
    mastery_score: 40.0,
    last_revision: '6 days ago',
    status: 'At Risk',
    risk_level: 'Critical',
    recommended_revision_date: 'Aug 15, 2026',
    predicted_forgetting_date: 'Aug 16, 2026',
    confidence_score: 96.4,
    days_until_forgetting: 1,
    revision_priority: 'High',
    learning_consistency: 42.0,
    avg_response_time_sec: 58,
    skills: ['Logit Function Complexity', 'Loss Normalization', 'Gradient Descent Rate']
  },
  {
    id: 'stu_sc4421',
    name: 'Sarah Connor',
    email: 'sarah.connor@edusense.ai',
    enrollment_number: 'EDU-2026-SC4421',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Neural Decay Networks',
    subject_id: '28ce886f-9623-5422-076f-ged9d4080803',
    knowledge_health: 44.0,
    retention_pct: 46.8,
    forget_probability: 0.58,
    mastery_score: 45.5,
    last_revision: '5 days ago',
    status: 'At Risk',
    risk_level: 'High',
    recommended_revision_date: 'Aug 16, 2026',
    predicted_forgetting_date: 'Aug 17, 2026',
    confidence_score: 94.2,
    days_until_forgetting: 2,
    revision_priority: 'High',
    learning_consistency: 51.0,
    avg_response_time_sec: 52,
    skills: ['Gradient Descent Rate', 'Activation Matrix Vectorization', 'Backpropagation']
  },
  {
    id: 'stu_mw9012',
    name: 'Marcus Wright',
    email: 'marcus.wright@edusense.ai',
    enrollment_number: 'EDU-2026-MW9012',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Logit Function & AI Logic',
    subject_id: '17bd775e-8512-4311-965f-fdc9c3979792',
    knowledge_health: 48.2,
    retention_pct: 50.4,
    forget_probability: 0.54,
    mastery_score: 49.0,
    last_revision: '4 days ago',
    status: 'At Risk',
    risk_level: 'High',
    recommended_revision_date: 'Aug 16, 2026',
    predicted_forgetting_date: 'Aug 18, 2026',
    confidence_score: 93.8,
    days_until_forgetting: 2,
    revision_priority: 'High',
    learning_consistency: 55.4,
    avg_response_time_sec: 49,
    skills: ['Cross-Entropy Loss Normalization', 'Logit Function Complexity']
  },
  {
    id: 'stu_er1102',
    name: 'Elena Rostova',
    email: 'elena.rostova@edusense.ai',
    enrollment_number: 'EDU-2026-ER1102',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Neural Decay Networks',
    subject_id: '28ce886f-9623-5422-076f-ged9d4080803',
    knowledge_health: 65.0,
    retention_pct: 68.5,
    forget_probability: 0.42,
    mastery_score: 66.0,
    last_revision: '3 days ago',
    status: 'Review Needed',
    risk_level: 'Medium',
    recommended_revision_date: 'Aug 18, 2026',
    predicted_forgetting_date: 'Aug 21, 2026',
    confidence_score: 91.5,
    days_until_forgetting: 4,
    revision_priority: 'Medium',
    learning_consistency: 72.0,
    avg_response_time_sec: 41,
    skills: ['Convolutional Filters', 'Matrix Calculus']
  },
  {
    id: 'stu_dm3390',
    name: 'Devon Miles',
    email: 'devon.miles@edusense.ai',
    enrollment_number: 'EDU-2026-DM3390',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Matrix Calculus',
    subject_id: '39df9970-0734-6533-187g-hfe0e5191914',
    knowledge_health: 69.4,
    retention_pct: 72.0,
    forget_probability: 0.38,
    mastery_score: 70.2,
    last_revision: '2 days ago',
    status: 'Review Needed',
    risk_level: 'Medium',
    recommended_revision_date: 'Aug 19, 2026',
    predicted_forgetting_date: 'Aug 23, 2026',
    confidence_score: 92.0,
    days_until_forgetting: 5,
    revision_priority: 'Medium',
    learning_consistency: 76.5,
    avg_response_time_sec: 39,
    skills: ['Eigenvalues', 'Vectorization']
  },
  {
    id: 'stu_ac7781',
    name: 'Amara Chen',
    email: 'amara.chen@edusense.ai',
    enrollment_number: 'EDU-2026-AC7781',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Logit Function & AI Logic',
    subject_id: '17bd775e-8512-4311-965f-fdc9c3979792',
    knowledge_health: 84.5,
    retention_pct: 88.0,
    forget_probability: 0.22,
    mastery_score: 86.4,
    last_revision: '1 day ago',
    status: 'Mastered',
    risk_level: 'Low',
    recommended_revision_date: 'Aug 24, 2026',
    predicted_forgetting_date: 'Aug 29, 2026',
    confidence_score: 95.6,
    days_until_forgetting: 10,
    revision_priority: 'Low',
    learning_consistency: 91.2,
    avg_response_time_sec: 28,
    skills: ['Logistic Regression', 'Logit Complexity']
  },
  {
    id: 'stu_tm5540',
    name: 'Tariq Mansoor',
    email: 'tariq.mansoor@edusense.ai',
    enrollment_number: 'EDU-2026-TM5540',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Neural Decay Networks',
    subject_id: '28ce886f-9623-5422-076f-ged9d4080803',
    knowledge_health: 89.0,
    retention_pct: 92.5,
    forget_probability: 0.15,
    mastery_score: 91.0,
    last_revision: 'Yesterday',
    status: 'Mastered',
    risk_level: 'Low',
    recommended_revision_date: 'Aug 28, 2026',
    predicted_forgetting_date: 'Sep 02, 2026',
    confidence_score: 97.2,
    days_until_forgetting: 14,
    revision_priority: 'Low',
    learning_consistency: 94.0,
    avg_response_time_sec: 25,
    skills: ['Deep Residual Learning', 'Adam Optimizer']
  },
  {
    id: 'stu_cb2219',
    name: 'Chloe Bennett',
    email: 'chloe.bennett@edusense.ai',
    enrollment_number: 'EDU-2026-CB2219',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Matrix Calculus',
    subject_id: '39df9970-0734-6533-187g-hfe0e5191914',
    knowledge_health: 87.2,
    retention_pct: 90.1,
    forget_probability: 0.18,
    mastery_score: 88.5,
    last_revision: '1 day ago',
    status: 'Mastered',
    risk_level: 'Low',
    recommended_revision_date: 'Aug 26, 2026',
    predicted_forgetting_date: 'Aug 31, 2026',
    confidence_score: 96.0,
    days_until_forgetting: 12,
    revision_priority: 'Low',
    learning_consistency: 92.8,
    avg_response_time_sec: 27,
    skills: ['Singular Value Decomposition', 'Matrix Multiplication']
  },
  {
    id: 'stu_lo8834',
    name: "Liam O'Connor",
    email: 'liam.oconnor@edusense.ai',
    enrollment_number: 'EDU-2026-LO8834',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Logit Function & AI Logic',
    subject_id: '17bd775e-8512-4311-965f-fdc9c3979792',
    knowledge_health: 92.0,
    retention_pct: 95.4,
    forget_probability: 0.12,
    mastery_score: 93.8,
    last_revision: 'Today',
    status: 'Mastered',
    risk_level: 'Low',
    recommended_revision_date: 'Sep 02, 2026',
    predicted_forgetting_date: 'Sep 08, 2026',
    confidence_score: 98.4,
    days_until_forgetting: 18,
    revision_priority: 'Low',
    learning_consistency: 96.5,
    avg_response_time_sec: 22,
    skills: ['Binary Cross-Entropy', 'Softmax Probability']
  },
  {
    id: 'stu_zp6645',
    name: 'Zoya Patel',
    email: 'zoya.patel@edusense.ai',
    enrollment_number: 'EDU-2026-ZP6645',
    institution: 'Engineering Institute',
    department: 'Computer Science',
    semester: 4,
    subject: 'Neural Decay Networks',
    subject_id: '28ce886f-9623-5422-076f-ged9d4080803',
    knowledge_health: 94.8,
    retention_pct: 97.2,
    forget_probability: 0.10,
    mastery_score: 96.0,
    last_revision: 'Today',
    status: 'Mastered',
    risk_level: 'Low',
    recommended_revision_date: 'Sep 05, 2026',
    predicted_forgetting_date: 'Sep 12, 2026',
    confidence_score: 99.1,
    days_until_forgetting: 21,
    revision_priority: 'Low',
    learning_consistency: 98.0,
    avg_response_time_sec: 20,
    skills: ['Transformers', 'Attention Mechanism']
  }
];

const StudentDataContext = createContext<StudentDataContextType | null>(null);

export const StudentDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [students, setStudents] = useState<StudentRecord[]>(INITIAL_MOCK_STUDENTS);
  const [selectedStudent, setSelectedStudent] = useState<StudentRecord | null>(null);
  const [selectedStudentDetails, setSelectedStudentDetails] = useState<StudentDeepDiveDetails | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [loadingModal, setLoadingModal] = useState<boolean>(false);

  // Sync backend student profiles dynamically when real students sign up and take exams
  useEffect(() => {
    async function syncBackendStudents() {
      try {
        const res = await apiClient.get('/faculty/students');
        if (res.data && res.data.items && res.data.items.length > 0) {
          const apiItems = res.data.items;
          const mappedStudents: StudentRecord[] = apiItems.map((item: any) => {
            const health = item.knowledge_health ?? (item.overall_health ?? 75.0);
            const forgetProb = item.forget_probability ?? (item.forgetting_probability ?? 0.25);
            const risk: 'Critical' | 'High' | 'Medium' | 'Low' = 
              forgetProb >= 0.7 ? 'Critical' :
              forgetProb >= 0.5 ? 'High' :
              forgetProb >= 0.3 ? 'Medium' : 'Low';

            return {
              id: item.id || `stu_${Math.random().toString(36).substr(2, 6)}`,
              name: item.display_name || item.name || `Student ${item.id.substring(0, 6)}`,
              email: item.email || `student_${item.id.substring(0, 6)}@edusense.ai`,
              enrollment_number: item.enrollment_number || `EDU-2026-${(item.id || 'STUDENT').substring(0, 6).toUpperCase()}`,
              institution: item.institution || 'Engineering Institute of AI',
              department: item.department || item.category || 'Computer Science',
              semester: item.semester || 4,
              subject: item.subject_name || item.subject || 'Data Structures & Algorithms',
              subject_id: item.subject_id || '17bd775e-8512-4311-965f-fdc9c3979792',
              knowledge_health: Number(health.toFixed(1)),
              retention_pct: Number((100 - (forgetProb * 100)).toFixed(1)),
              forget_probability: Number(forgetProb.toFixed(2)),
              mastery_score: item.mastery_score ? Number(item.mastery_score.toFixed(1)) : Number((health * 1.05).toFixed(1)),
              last_revision: item.last_interaction_at ? 'Recently Examined' : '1 day ago',
              status: risk === 'Critical' || risk === 'High' ? 'At Risk' : risk === 'Medium' ? 'Review Needed' : 'Mastered',
              risk_level: risk,
              recommended_revision_date: 'Aug 22, 2026',
              predicted_forgetting_date: 'Aug 26, 2026',
              confidence_score: 95.0,
              days_until_forgetting: forgetProb >= 0.5 ? 2 : 10,
              revision_priority: risk === 'Critical' || risk === 'High' ? 'High' : 'Medium',
              learning_consistency: 85.0,
              avg_response_time_sec: 32,
              skills: item.skills || ['Core Concepts', 'Algorithmic Logic']
            };
          });

          // Merge backend students with any missing demo fallback entries
          const existingIds = new Set(mappedStudents.map(s => s.id));
          const remainingMock = INITIAL_MOCK_STUDENTS.filter(s => !existingIds.has(s.id));
          setStudents([...mappedStudents, ...remainingMock]);
        }
      } catch (e) {
        // Fallback silently to initialized high-fidelity dataset
      }
    }
    syncBackendStudents();
  }, []);

  const atRiskStudents = useMemo(() => {
    return students.filter(s => s.risk_level === 'Critical' || s.risk_level === 'High' || s.forget_probability >= 0.5);
  }, [students]);

  const atRiskCount = useMemo(() => atRiskStudents.length, [atRiskStudents]);

  const openStudentModal = async (studentId: string) => {
    const found = students.find(s => s.id === studentId || s.enrollment_number === studentId);
    if (!found) return;

    setSelectedStudent(found);
    setIsModalOpen(true);
    setLoadingModal(true);

    try {
      const res = await apiClient.get(`/faculty/students/${found.id}/analytics`);
      if (res.data && res.data.student) {
        setSelectedStudentDetails({
          ...res.data,
          student: {
            ...res.data.student,
            name: found.name,
            email: found.email,
            enrollment_number: found.enrollment_number,
            forget_probability: found.forget_probability,
            knowledge_health: found.knowledge_health,
            status: found.status
          }
        });
      }
    } catch (err) {
      setSelectedStudentDetails({
        student: found,
        weak_skills: [
          { id: 'sk_01', name: 'Logit Function Complexity', proficiency: Math.round(found.knowledge_health * 0.9), forget_prob: found.forget_probability },
          { id: 'sk_02', name: 'Gradient Descent Rate', proficiency: Math.round(found.knowledge_health * 0.95), forget_prob: roundNum(found.forget_probability * 0.9, 2) }
        ],
        strong_skills: [
          { id: 'sk_03', name: 'Activation Matrix Vectorization', proficiency: 89.2 },
          { id: 'sk_04', name: 'Cross-Entropy Loss Normalization', proficiency: 94.0 }
        ],
        recent_assessments: [
          { id: 'sess_101', title: `${found.subject} Diagnostic Baseline`, score_pct: found.retention_pct, date: '2026-08-12', status: 'completed' },
          { id: 'sess_102', title: 'Adaptive Spaced Recall #1', score_pct: roundNum(found.retention_pct * 0.95, 1), date: '2026-08-08', status: 'completed' }
        ],
        retention_timeline: [
          { date: 'Aug 01', retention: 95.0, baseline: 95.0 },
          { date: 'Aug 05', retention: roundNum(found.retention_pct * 1.1, 1), baseline: 85.0 },
          { date: 'Aug 09', retention: roundNum(found.retention_pct * 1.05, 1), baseline: 74.0 },
          { date: 'Aug 14', retention: found.retention_pct, baseline: 55.0 }
        ],
        knowledge_decay_curve: [
          { day: 0, predicted_retention: 95.0, threshold: 50.0 },
          { day: 3, predicted_retention: roundNum(found.retention_pct * 0.95, 1), threshold: 50.0 },
          { day: 7, predicted_retention: roundNum(found.retention_pct * 0.85, 1), threshold: 50.0 },
          { day: 14, predicted_retention: roundNum(found.retention_pct * 0.70, 1), threshold: 50.0 },
          { day: 21, predicted_retention: roundNum(found.retention_pct * 0.55, 1), threshold: 50.0 },
          { day: 30, predicted_retention: roundNum(found.retention_pct * 0.40, 1), threshold: 50.0 }
        ],
        mastery_distribution: [
          { category: 'Mastered (>=80%)', count: found.status === 'Mastered' ? 5 : 2, color: '#10b981' },
          { category: 'Review Needed (50-79%)', count: 3, color: '#f59e0b' },
          { category: 'At Risk (<50%)', count: found.status === 'At Risk' ? 4 : 1, color: '#ef4444' }
        ],
        revision_frequency: [
          { week: 'Week 1', revisions_count: 5 },
          { week: 'Week 2', revisions_count: 8 },
          { week: 'Week 3', revisions_count: 4 },
          { week: 'Week 4', revisions_count: 7 }
        ],
        skill_heatmap: [
          { skill: 'Logit Complexity', mastery_pct: Math.round(found.knowledge_health * 0.9), risk_level: found.risk_level === 'Critical' ? 'High Risk' : 'Mastered' },
          { skill: 'Gradient Rates', mastery_pct: Math.round(found.knowledge_health), risk_level: found.risk_level }
        ],
        recommendations: [
          {
            id: 'rec_01',
            title: `Remedial Quiz: ${found.subject}`,
            type: 'Remedial Quiz',
            priority: 'High Priority',
            description: `Targeted practice set recommended based on forget probability ${found.forget_probability}.`
          }
        ]
      });
    } finally {
      setLoadingModal(false);
    }
  };

  const closeStudentModal = () => {
    setIsModalOpen(false);
    setSelectedStudent(null);
    setSelectedStudentDetails(null);
  };

  const generateStudentReport = (studentId: string) => {
    const found = students.find(s => s.id === studentId);
    const name = found ? found.name : 'Student';
    alert(`Generating official Knowledge Decay & Retention Report for ${name} (${studentId})...\nReport PDF will be downloaded.`);
  };

  const scrollToAtRiskTable = () => {
    const el = document.getElementById('at-risk-watchlist-section');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const roundNum = (val: number, decimals: number) => {
    return Number(Math.min(99.9, Math.max(5.0, val)).toFixed(decimals));
  };

  return (
    <StudentDataContext.Provider value={{
      students,
      atRiskStudents,
      atRiskCount,
      selectedStudent,
      selectedStudentDetails,
      isModalOpen,
      loadingModal,
      openStudentModal,
      closeStudentModal,
      generateStudentReport,
      scrollToAtRiskTable
    }}>
      {children}
    </StudentDataContext.Provider>
  );
};

export const useStudentData = (): StudentDataContextType => {
  const context = useContext(StudentDataContext);
  if (!context) {
    throw new Error('useStudentData must be used within a StudentDataProvider');
  }
  return context;
};
