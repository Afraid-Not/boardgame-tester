"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Square, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import type { TrainingJob } from "@/types";

const statusColor: Record<string, string> = {
  queued: "bg-zinc-500",
  running: "bg-purple-500",
  completed: "bg-emerald-500",
  failed: "bg-red-500",
};

const TrainPage = () => {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const gameId = params.id as string;
  const jobId = searchParams.get("jobId");

  const [job, setJob] = useState<TrainingJob | null>(null);
  const [progress, setProgress] = useState(0);

  const pollProgress = useCallback(async () => {
    if (!jobId) return;
    try {
      const data = await api.fetch(`/api/training/${jobId}/progress`);
      setProgress(data.progress ?? 0);
      if (data.status === "completed" || data.status === "failed") {
        // 최종 상태 조회
        const finalJob = await api.getTrainingJob(jobId);
        setJob(finalJob);
      }
    } catch {
      // ignore polling errors
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId) return;
    // 초기 로드
    api.getTrainingJob(jobId).then(setJob);

    const interval = setInterval(pollProgress, 2000);
    return () => clearInterval(interval);
  }, [jobId, pollProgress]);

  const handleStop = async () => {
    if (!jobId) return;
    await api.fetch(`/api/training/${jobId}/stop`, { method: "POST" });
    const updated = await api.getTrainingJob(jobId);
    setJob(updated);
  };

  if (!jobId) {
    return (
      <div className="text-muted-foreground">No training job specified</div>
    );
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">Training</h1>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Training Job</CardTitle>
            {job && (
              <Badge className={statusColor[job.status]}>{job.status}</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {job && (
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-muted rounded-lg">
                <p className="text-xs text-muted-foreground">Algorithm</p>
                <p className="font-semibold">{job.algorithm}</p>
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <p className="text-xs text-muted-foreground">Episodes</p>
                <p className="font-semibold">
                  {job.total_episodes.toLocaleString()}
                </p>
              </div>
            </div>
          )}

          {/* Progress bar */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Progress</span>
              <span className="text-sm text-muted-foreground">{progress}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-4 overflow-hidden">
              <div
                className="bg-purple-500 h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {job?.status === "running" && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                Training in progress...
              </div>
              <Button variant="destructive" size="sm" onClick={handleStop}>
                <Square className="w-3 h-3 mr-1" />
                Stop
              </Button>
            </div>
          )}

          {job?.status === "completed" && (
            <Button
              className="w-full"
              onClick={() =>
                router.push(`/games/${gameId}/report?jobId=${jobId}`)
              }
            >
              View Balance Report
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          )}

          {job?.status === "failed" && (
            <div className="text-center text-red-600 text-sm">
              Training failed or was stopped.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default TrainPage;
