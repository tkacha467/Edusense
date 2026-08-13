import React, { useState } from 'react';
import { useSubjects, useTopics, useSkills } from '../hooks/useLearning';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Skeleton } from '../../../components/ui/Skeleton';
import { BookOpen, Search, ChevronDown, ChevronRight, Layers, LayoutList } from 'lucide-react';

function TopicSkills({ topicId }: { topicId: string }) {
  const { data: skills, isLoading, error } = useSkills(topicId);

  if (isLoading) return <Skeleton className="h-6 w-full mt-2" />;
  if (error) return <div className="text-red-500 text-sm mt-2">Failed to load skills.</div>;
  if (!skills?.length) return <div className="text-gray-500 text-sm mt-2">No skills found.</div>;

  return (
    <div className="mt-2 pl-4 border-l-2 border-gray-200 space-y-2">
      {skills.map(skill => (
        <div key={skill.skill_id || skill.id} className="text-sm flex items-center justify-between bg-gray-50 p-2 rounded">
          <span>{skill.name || `Skill ${skill.skill_id}`}</span>
          {skill.relevance_weight !== undefined && (
            <span className="text-xs text-gray-500">Weight: {skill.relevance_weight}</span>
          )}
        </div>
      ))}
    </div>
  );
}

function SubjectTopics({ subjectId }: { subjectId: string }) {
  const { data: topics, isLoading, error } = useTopics(subjectId);
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);

  if (isLoading) return (
    <div className="mt-4 space-y-3">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
    </div>
  );
  if (error) return <div className="text-red-500 mt-4 p-4 bg-red-50 rounded">Failed to load topics.</div>;
  if (!topics?.length) return <div className="text-gray-500 mt-4 p-4 border rounded border-dashed text-center">No topics available for this subject.</div>;

  return (
    <div className="mt-4 space-y-3">
      {topics.map(topic => {
        const isExpanded = expandedTopic === topic.id;
        return (
          <div key={topic.id} className="border rounded-lg overflow-hidden">
            <button 
              className="w-full text-left p-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
              onClick={() => setExpandedTopic(isExpanded ? null : topic.id)}
            >
              <div className="flex items-center gap-2">
                <LayoutList className="w-4 h-4 text-primary" />
                <span className="font-medium">{topic.name}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500 bg-white px-2 py-1 rounded border">{topic.difficulty_level}</span>
                {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
              </div>
            </button>
            {isExpanded && (
              <div className="p-3 bg-white">
                <p className="text-sm text-gray-600 mb-3">{topic.description}</p>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Skills</h4>
                <TopicSkills topicId={topic.id} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export function LearningHub() {
  const { data: subjects, isLoading, error } = useSubjects();
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSubject, setExpandedSubject] = useState<string | null>(null);

  const filteredSubjects = subjects?.filter(subject => 
    subject.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    subject.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    subject.code.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-primary" />
          Learning Hub
        </h1>
        <p className="text-gray-500 mt-2">Explore subjects, topics, and granular skills in your academic curriculum.</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input 
          type="text" 
          placeholder="Search subjects by name, code, or description..." 
          className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-48 w-full rounded-xl" />
          <Skeleton className="h-48 w-full rounded-xl" />
        </div>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-8 text-center text-red-600">
            <h3 className="font-semibold text-lg mb-2">Error Loading Curriculum</h3>
            <p>Could not retrieve the subjects from the server. Please check your connection and try again.</p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && filteredSubjects.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="p-12 text-center text-gray-500">
            <Layers className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="font-medium text-gray-900 text-lg">No Subjects Found</h3>
            <p className="mt-1">Try adjusting your search criteria.</p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && filteredSubjects.length > 0 && (
        <div className="grid grid-cols-1 gap-6">
          {filteredSubjects.map(subject => {
            const isExpanded = expandedSubject === subject.id;
            
            return (
              <Card key={subject.id} className="overflow-hidden transition-all hover:shadow-md border-gray-200">
                <CardHeader className="cursor-pointer bg-white" onClick={() => setExpandedSubject(isExpanded ? null : subject.id)}>
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">{subject.code}</span>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">{subject.category}</span>
                      </div>
                      <CardTitle className="text-xl">{subject.name}</CardTitle>
                      <p className="text-gray-600 text-sm mt-2 line-clamp-2">{subject.description}</p>
                    </div>
                    <Button variant="ghost" size="sm" className="shrink-0 text-gray-500">
                      {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                    </Button>
                  </div>
                </CardHeader>
                
                {isExpanded && (
                  <CardContent className="bg-gray-50/50 border-t pt-4">
                    <h3 className="font-semibold text-gray-800 mb-2">Curriculum Topics</h3>
                    <SubjectTopics subjectId={subject.id} />
                  </CardContent>
                )}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
