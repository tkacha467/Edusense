export interface StudentAnalyticsSummary {
  id: string;
  name: string;
  email: string;
  enrollment_number: string;
  institution: string;
  department: string;
  semester: number;
  subject: string;
  subject_id: string;
  knowledge_health: number;
  retention_pct: number;
  forget_probability: number;
  mastery_score: number;
  last_revision: string;
  status: 'Mastered' | 'Review Needed' | 'At Risk';
  days_until_forgetting: number;
  revision_priority: 'High' | 'Medium' | 'Low';
  learning_consistency: number;
  avg_response_time_sec: number;
}

export interface WeakSkillItem {
  id: string;
  name: string;
  proficiency: number;
  forget_prob: number;
}

export interface StrongSkillItem {
  id: string;
  name: string;
  proficiency: number;
}

export interface RecentAssessmentItem {
  id: string;
  title: string;
  score_pct: number;
  date: string;
  status: string;
}

export interface RetentionTimelinePoint {
  date: string;
  retention: number;
  baseline: number;
}

export interface KnowledgeDecayPoint {
  day: number;
  predicted_retention: number;
  threshold: number;
}

export interface MasteryDistributionCategory {
  category: string;
  count: number;
  color: string;
}

export interface RevisionFrequencyPoint {
  week: string;
  revisions_count: number;
}

export interface SkillHeatmapPoint {
  skill: string;
  mastery_pct: number;
  risk_level: string;
}

export interface StudentRecommendationItem {
  id: string;
  title: string;
  type: string;
  priority: string;
  description: string;
}

export interface StudentDeepDiveDetails {
  student: StudentAnalyticsSummary;
  weak_skills: WeakSkillItem[];
  strong_skills: StrongSkillItem[];
  recent_assessments: RecentAssessmentItem[];
  retention_timeline: RetentionTimelinePoint[];
  knowledge_decay_curve: KnowledgeDecayPoint[];
  mastery_distribution: MasteryDistributionCategory[];
  revision_frequency: RevisionFrequencyPoint[];
  skill_heatmap: SkillHeatmapPoint[];
  recommendations: StudentRecommendationItem[];
}
