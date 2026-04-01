"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Loader2 } from "lucide-react";
import { useGameStore } from "@/stores/game-store";

const statusColor: Record<string, string> = {
  parsing: "bg-yellow-500",
  ready: "bg-blue-500",
  training: "bg-purple-500",
  completed: "bg-emerald-500",
};

const GamesPage = () => {
  const { games, loading, error, fetchGames } = useGameStore();

  useEffect(() => {
    fetchGames();
  }, [fetchGames]);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Games</h1>
        <Link href="/games/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Game
          </Button>
        </Link>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        </div>
      ) : games.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <p>No games yet. Create your first game to get started.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {games.map((game) => (
            <Link key={game.id} href={`/games/${game.id}`}>
              <Card className="hover:border-zinc-400 transition-colors cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{game.name}</CardTitle>
                    <Badge className={statusColor[game.status]}>
                      {game.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground capitalize">
                    {game.genre.replace("_", " ")}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(game.created_at).toLocaleDateString("ko-KR")}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default GamesPage;
