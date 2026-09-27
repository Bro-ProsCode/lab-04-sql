SELECT 
    u.username,
    u.email,
    p.title,
    p.published_at
FROM users u
INNER JOIN posts p ON u.user_id = p.user_id
WHERE p.user_id <= 5
ORDER BY p.published_at DESC;