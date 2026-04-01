"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Play, FileJson, ArrowRight } from "lucide-react";
import { useGameStore } from "@/stores/game-store";

const statusColor: Record<string, string> = {
  parsing: "bg-yellow-500",
  ready: "bg-blue-500",
  training: "bg-purple-500",
  completed: "bg-emerald-500",
};

const GameDetailPage = () => {
  const params = useParams();
  const router = useRouter();
  const gameId = params.id as string;
  const { currentGame, loading, error, fetchGame, startTraining } =
    useGameStore();

  useEffect(() => {
    fetchGame(gameId);
  }, [gameId, fetchGame]);

  const handleStartTraining = async () => {
    try {
      const job = await startTraining(gameId);
      router.push(`/games/${gameId}/train?jobId=${job.id}`);
    } catch {
      // error handled by store
    }
  };

  if (loading && !currentGame) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    );
  }

  if (!currentGame) {
    return <div className="text-muted-foreground">Game not found</div>;
  }

  const parsed = currentGame.parsed_structure;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">{currentGame.name}</h1>
          <p className="text-muted-foreground capitalize mt-1">
            {currentGame.genre.replace("_", " ")}
          </p>
        </div>
        <Badge
          className={`${statusColor[currentGame.status]} text-sm px-3 py-1`}
        >
          {currentGame.status}
        </Badge>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 파싱 결과 */}
        <div className="lg:col-span-2 space-y-6">
          {currentGame.status === "parsing" && !parsed && (
            <Card>
              <CardContent className="py-12 text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Parsing rules with AI... This may take a minute.
                </p>
              </CardContent>
            </Card>
          )}

          {parsed && !("error" in parsed) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileJson className="w-5 h-5" />
                  Parsed Game Structure
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  {(() => {
                    const p = parsed as Record<string, Record<string, unknown>>;
                    const players = p.players as
                      | Record<string, number>
                      | undefined;
                    const components = p.components as
                      | Record<string, unknown>
                      | undefined;
                    const board = components?.board as
                      | Record<string, unknown>
                      | undefined;
                    return (
                      <>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-xs text-muted-foreground">
                            Players
                          </p>
                          <p className="font-semibold">
                            {players ? `${players.min}-${players.max}` : "N/A"}
                          </p>
                        </div>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-xs text-muted-foreground">
                            Board Spaces
                          </p>
                          <p className="font-semibold">
                            {String(board?.total_spaces ?? "N/A")}
                          </p>
                        </div>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-xs text-muted-foreground">
                            Starting Money
                          </p>
                          <p className="font-semibold">
                            {String(components?.starting_money ?? "N/A")}
                          </p>
                        </div>
                        <div className="p-3 bg-muted rounded-lg">
                          <p className="text-xs text-muted-foreground">
                            Win Condition
                          </p>
                          <p className="font-semibold capitalize">
                            {String(p.win_condition ?? "N/A").replace(
                              /_/g,
                              " ",
                            )}
                          </p>
                        </div>
                      </>
                    );
                  })()}
                </div>

                <details className="mt-4">
                  <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
                    View raw JSON
                  </summary>
                  <pre className="mt-2 p-4 bg-muted rounded-lg overflow-auto text-xs max-h-96">
                    {JSON.stringify(parsed, null, 2)}
                  </pre>
                </details>
              </CardContent>
            </Card>
          )}

          {parsed && "error" in parsed && (
            <Card className="border-red-200">
              <CardContent className="py-8 text-center text-red-600">
                <p className="font-medium">Parsing failed</p>
                <p className="text-sm mt-1">{String(parsed.error)}</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 오른쪽: 액션 패널 */}
        <div className="space-y-4">
          {(currentGame.status === "ready" ||
            currentGame.status === "completed") && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Start Training</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Run RL simulation to analyze game balance.
                </p>
                <Button
                  className="w-full"
                  onClick={handleStartTraining}
                  disabled={loading}
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4 mr-2" />
                  )}
                  Start Training (PPO)
                </Button>
              </CardContent>
            </Card>
          )}

          {currentGame.status === "completed" && (
            <Card>
              <CardContent className="pt-6">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => router.push(`/games/${gameId}/report`)}
                >
                  View Balance Report
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameDetailPage;
