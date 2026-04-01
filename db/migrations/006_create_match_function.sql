-- 벡터 유사도 검색 RPC 함수
CREATE OR REPLACE FUNCTION match_game_references(
    query_embedding VECTOR(384),
    match_genre TEXT DEFAULT 'economic_board',
    match_count INT DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    genre TEXT,
    rules_summary TEXT,
    balance_data JSONB,
    strategies JSONB,
    source TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        gr.id,
        gr.name,
        gr.genre,
        gr.rules_summary,
        gr.balance_data,
        gr.strategies,
        gr.source,
        1 - (gr.embedding <=> query_embedding) AS similarity
    FROM game_references gr
    WHERE gr.genre = match_genre
      AND gr.embedding IS NOT NULL
    ORDER BY gr.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
