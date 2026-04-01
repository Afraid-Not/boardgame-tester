"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Loader2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { api } from "@/lib/api";
import type { BalanceReport } from "@/types";

const severityConfig = {
  good: { color: "bg-emerald-500", icon: CheckCircle, label: "Good" },
  warning: { color: "bg-yellow-500", icon: AlertTriangle, label: "Warning" },
  critical: { color: "bg-red-500", icon: XCircle, label: "Critical" },
};

const COLORS = ["#8b5cf6", "#06b6d4", "#f59e0b", "#ef4444", "#10b981"];

const ReportPage = () => {
  const params = useParams();
  const searchParams = useSearchParams();
  const gameId = params.id as string;
  const jobId = searchParams.get("jobId");

  const [report, setReport] = useState<BalanceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [revalidating, setRevalidating] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    setLoading(true);
    api
      .getReport(jobId)
      .then(setReport)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [jobId]);

  const handleRevalidate = async () => {
    if (!jobId) return;
    setRevalidating(true);
    try {
      await api.fetch(`/api/reports/${jobId}/revalidate`, { method: "POST" });
      // 재검증은 백그라운드 — 폴링
      const poll = setInterval(async () => {
        const updated = await api.getReport(jobId);
        setReport(updated);
        const guidelines = updated.guidelines || [];
        const hasReval = guidelines.some(
          (g: Record<string, unknown>) => "revalidation" in g,
        );
        if (hasReval) {
          clearInterval(poll);
          setRevalidating(false);
        }
      }, 5000);
    } catch {
      setRevalidating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-muted-foreground">
        No report found. Train the game first.
      </div>
    );
  }

  const sev = severityConfig[report.severity] || severityConfig.warning;
  const SevIcon = sev.icon;

  // 차트 데이터 준비
  const winRateData = Object.entries(report.win_rates).map(
    ([player, rate]) => ({
      player: `Player ${player}`,
      winRate: Math.round((rate as number) * 100),
    }),
  );

  const allGuidelines = (report.guidelines || []) as Record<string, unknown>[];
  const guidelines = allGuidelines.filter((g) => !("revalidation" in g));
  const revalResult = allGuidelines.find((g) => "revalidation" in g);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Balance Report</h1>
        <Button
          variant="outline"
          onClick={handleRevalidate}
          disabled={revalidating || guidelines.length === 0}
        >
          {revalidating ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          Revalidate
        </Button>
      </div>

      {/* 밸런스 스코어 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="pt-6 text-center">
            <div className="text-5xl font-bold mb-2">
              {report.balance_score}
            </div>
            <p className="text-sm text-muted-foreground">Balance Score / 100</p>
            <Badge className={`${sev.color} mt-3`}>
              <SevIcon className="w-3 h-3 mr-1" />
              {sev.label}
            </Badge>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Win Rates</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={winRateData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="player" />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip formatter={(v) => `${v}%`} />
                <Bar dataKey="winRate" radius={[4, 4, 0, 0]}>
                  {winRateData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* 지배 전략 */}
      {report.dominant_strategies.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-base">Dominant Strategies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(report.dominant_strategies as Record<string, string>[]).map(
                (s, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-3 bg-muted rounded-lg"
                  >
                    <Badge
                      variant="outline"
                      className={
                        s.impact === "high"
                          ? "border-red-300 text-red-600"
                          : "border-yellow-300 text-yellow-600"
                      }
                    >
                      {s.impact}
                    </Badge>
                    <div>
                      <p className="font-medium text-sm">{s.name}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {s.description}
                      </p>
                      <p className="text-xs text-muted-foreground italic mt-0.5">
                        {s.evidence}
                      </p>
                    </div>
                  </div>
                ),
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 가이드라인 */}
      {guidelines.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-base">Improvement Guidelines</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {guidelines.map((g: Record<string, unknown>, i: number) => (
                <div key={i} className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline">P{String(g.priority)}</Badge>
                    <Badge variant="secondary">{String(g.category)}</Badge>
                    <span className="font-medium text-sm">
                      {String(g.title)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">
                    {String(g.description)}
                  </p>
                  {Array.isArray(g.changes) && g.changes.length > 0 && (
                    <div className="bg-muted rounded-lg p-3 space-y-1">
                      {(g.changes as Record<string, string>[]).map(
                        (c, j: number) => (
                          <p key={j} className="text-xs font-mono">
                            <span className="text-muted-foreground">
                              {c.target}:
                            </span>{" "}
                            <span className="text-red-500 line-through">
                              {c.from}
                            </span>{" "}
                            → <span className="text-emerald-600">{c.to}</span>
                          </p>
                        ),
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 재검증 결과 (Before/After) */}
      {revalResult && (
        <Card className="border-blue-200">
          <CardHeader>
            <CardTitle className="text-base">
              Revalidation Result (Before / After)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const reval = revalResult.revalidation as Record<string, unknown>;
              const comparison = reval.comparison as Record<string, unknown>;
              const scoreChange = comparison.score_change as number;
              return (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-xs text-muted-foreground">Before</p>
                      <p className="text-2xl font-bold">
                        {String(comparison.score_before)}
                      </p>
                    </div>
                    <div className="p-3 bg-muted rounded-lg flex flex-col items-center justify-center">
                      <p className="text-xs text-muted-foreground">Change</p>
                      <p
                        className={`text-2xl font-bold ${scoreChange > 0 ? "text-emerald-600" : "text-red-600"}`}
                      >
                        {scoreChange > 0 ? "+" : ""}
                        {scoreChange}
                      </p>
                    </div>
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-xs text-muted-foreground">After</p>
                      <p className="text-2xl font-bold">
                        {String(comparison.score_after)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center gap-2">
                    {scoreChange > 0 ? (
                      <Badge className="bg-emerald-500">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Balance Improved
                      </Badge>
                    ) : (
                      <Badge className="bg-red-500">
                        <XCircle className="w-3 h-3 mr-1" />
                        Balance Not Improved
                      </Badge>
                    )}
                  </div>
                </div>
              );
            })()}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ReportPage;
