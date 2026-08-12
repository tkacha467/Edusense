import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { BrainCircuit, Play, BarChart2, ShieldCheck, Loader2 } from 'lucide-react';
import { SkeletonLoader } from '../../components/ui/Feedback';
import { SimpleBarChart } from '../../components/ui/Charts';

export function KnowledgeDecay() {
  const [isPredicting, setIsPredicting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handlePredict = () => {
    setIsPredicting(true);
    setResult(null);
    // Simulate Data Analysis
    setTimeout(() => {
      setIsPredicting(false);
      setResult({
        healthScore: 18,
        features: [
          { name: 'Time Taken on Problem', contribution: 'High Impact' },
          { name: 'Confidence: Concentrating', contribution: 'Medium Impact' },
          { name: 'Total Hint Count', contribution: 'Low Impact' },
        ],
        recommendation: 'Immediate spaced repetition session required for Addition and Fraction Division.',
        graphData: [
          { name: 'Day 1', engagement: 100 },
          { name: 'Day 3', engagement: 85 },
          { name: 'Day 7', engagement: 65 },
          { name: 'Day 14', engagement: 40 },
          { name: 'Day 30', engagement: 18 }, // Current projection
        ]
      });
    }, 2500);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Student Insight Analysis</h1>
        <p className="text-muted-foreground mt-1">Generate deep learning retention insights for individual students.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Assessment Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Student ID</label>
                <Input placeholder="e.g. STU-008" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Skill Module</label>
                <select className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                  <option>Addition</option>
                  <option>Multiplication</option>
                  <option>Fraction Division</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Analysis Engine</label>
                <select className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" disabled>
                  <option>Standard Insights</option>
                </select>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-500" /> Data engine is synced and ready.
                </p>
              </div>
              
              <Button 
                className="w-full mt-4" 
                onClick={handlePredict}
                disabled={isPredicting}
              >
                {isPredicting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Generating Insights...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Run Analysis
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Results Area */}
        <div className="lg:col-span-2">
          {isPredicting ? (
            <Card className="h-full min-h-[400px]">
              <CardHeader>
                <CardTitle>Compiling Student Data...</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <SkeletonLoader className="h-24 w-full" />
                <div className="space-y-2">
                  <SkeletonLoader className="h-4 w-3/4" />
                  <SkeletonLoader className="h-4 w-1/2" />
                  <SkeletonLoader className="h-4 w-5/6" />
                </div>
                <SkeletonLoader className="h-48 w-full mt-6" />
              </CardContent>
            </Card>
          ) : result ? (
            <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
              <Card className="border-red-200 shadow-sm">
                <CardContent className="p-6">
                  <div className="flex items-center gap-6">
                    <div className="relative flex items-center justify-center w-24 h-24 rounded-full bg-red-50 border-8 border-red-100 shrink-0">
                      <span className="text-3xl font-bold text-red-600">{result.healthScore}%</span>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">Critical Learning Gap Identified</h3>
                      <p className="text-gray-600 mb-3">{result.recommendation}</p>
                      <div className="flex gap-2">
                        <Button size="sm">Generate Intervention Plan</Button>
                        <Button size="sm" variant="outline" className="bg-white">Notify Student</Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <BarChart2 className="w-4 h-4" /> Key Performance Factors
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {result.features.map((f: any, i: number) => (
                        <div key={i} className="flex justify-between items-center border-b pb-2 last:border-0">
                          <span className="text-sm font-medium text-gray-700">{f.name}</span>
                          <span className="text-sm font-bold text-gray-600">
                            {f.contribution}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <BrainCircuit className="w-4 h-4" /> Projected Retention Curve
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <SimpleBarChart data={result.graphData} categories={['engagement']} height={200} />
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[400px] border-2 border-dashed rounded-xl flex flex-col items-center justify-center text-center p-8 bg-gray-50/50">
              <div className="bg-white p-4 rounded-full shadow-sm mb-4">
                <BrainCircuit className="w-8 h-8 text-primary/40" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready for Analysis</h3>
              <p className="text-muted-foreground max-w-sm">Select a student and skill module to generate learning retention insights.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
