"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Gamepad2, Activity, BarChart3, ArrowRight } from "lucide-react";
import { useGameStore } from "@/stores/game-store";

const statusColor: Record<string, string> = {
  parsing: "bg-yellow-500",
  ready: "bg-blue-500",
  training: "bg-purple-500",
  completed: "bg-emerald-500",
};

const DashboardPage = () => {
  const { games, fetchGames } = useGameStore();

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  const completedGames = games.filter((g) => g.status === "completed");
  const trainingGames = games.filter((g) => g.status === "training");

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Games
            </CardTitle>
            <Gamepad2 className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{games.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              In Training
            </CardTitle>
            <Activity className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trainingGames.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Completed
            </CardTitle>
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedGames.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* 최근 게임 */}
      {games.length > 0 ? (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Games</CardTitle>
              <Link
                href="/games"
                className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
              >
                View all <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="divide-y">
              {games.slice(0, 5).map((game) => (
                <Link
                  key={game.id}
                  href={`/games/${game.id}`}
                  className="flex items-center justify-between py-3 hover:bg-muted/50 -mx-3 px-3 rounded transition-colors"
                >
                  <div>
                    <p className="font-medium">{game.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(game.created_at).toLocaleDateString("ko-KR")}
                    </p>
                  </div>
                  <Badge className={statusColor[game.status]}>
                    {game.status}
                  </Badge>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground space-y-2">
            <p>1. Create a new game and upload your board game rulebook</p>
            <p>2. AI will parse the rules and generate a game environment</p>
            <p>3. Run RL simulations to analyze game balance</p>
            <p>4. Review the balance report and improvement guidelines</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DashboardPage;
