SELECT 
	m.id,
	m.created_at 'Message was created on',
    m.message,
    u.first_name,
    u.last_name
    
FROM messages AS m
JOIN users AS u
ON  m.user_id = u.id
ORDER BY m.created_at DESC