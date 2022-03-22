UPDATE
    levels
SET level_rating=(
                     SELECT ROUND(CAST(AVG(comment_rating) FILTER (WHERE comment_rating > 0) AS NUMERIC), 2)
                     FROM comments
                     WHERE level_id =%(level_id)s
    )
WHERE level_id =%(level_id)s;