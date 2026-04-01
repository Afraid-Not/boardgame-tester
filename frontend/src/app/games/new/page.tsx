"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Loader2 } from "lucide-react";
import { useGameStore } from "@/stores/game-store";

const NewGamePage = () => {
  const router = useRouter();
  const { createGame, parseGame } = useGameStore();
  const [name, setName] = useState("");
  const [rulesText, setRulesText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    if (!rulesText.trim() && !file) {
      setError("Please provide rules text or upload a rulebook file.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const game = await createGame(name, "economic_board");
      await parseGame(game.id, rulesText || undefined, file || undefined);
      router.push(`/games/${game.id}`);
    } catch (e) {
      setError((e as Error).message);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-8">New Game</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Game Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Game Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg bg-background"
                placeholder="e.g. My Board Game"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Genre</label>
              <select
                className="w-full px-3 py-2 border rounded-lg bg-background"
                disabled
              >
                <option value="economic_board">Economic Board Game</option>
              </select>
              <p className="text-xs text-muted-foreground mt-1">
                Card battle games coming in Phase 2
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Rulebook</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Rules Text
              </label>
              <textarea
                value={rulesText}
                onChange={(e) => setRulesText(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg bg-background min-h-[200px] resize-y font-mono text-sm"
                placeholder="Paste your game rules here..."
              />
            </div>

            <div className="relative flex items-center gap-4">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-muted-foreground">OR</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            <div className="relative">
              <label className="block text-sm font-medium mb-2">
                Upload Rulebook Image/PDF
              </label>
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-zinc-400 transition-colors">
                <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  {file ? file.name : "Click or drag to upload"}
                </p>
                <input
                  type="file"
                  accept="image/*,.pdf"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Button
          type="submit"
          className="w-full"
          disabled={isSubmitting || !name.trim()}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Creating & Parsing...
            </>
          ) : (
            "Create Game & Start Parsing"
          )}
        </Button>
      </form>
    </div>
  );
};

export default NewGamePage;
