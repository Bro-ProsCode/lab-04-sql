DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    post_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    content TEXT NOT NULL,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

INSERT INTO users (user_id, username, email) VALUES
(1, 'alex_m', 'alex@example.com'),
(2, 'jordan_p', 'jordan@example.com'),
(3, 'taylor_s', 'taylor@example.com'),
(4, 'morgan_d', 'morgan@example.com'),
(5, 'casey_r', 'casey@example.com'),
(6, 'riley_k', 'riley@example.com'),
(7, 'sam_b', 'sam@example.com'),
(8, 'dakota_h', 'dakota@example.com'),
(9, 'quinn_w', 'quinn@example.com'),
(10, 'reese_c', 'reese@example.com');

INSERT INTO posts (user_id, title, content) VALUES
(1, 'Intro to Systems', 'Starting our exploration into low-level systems.'),
(1, 'Debugging Memory Leaks', 'Valgrind and sanitizers save the day.'),
(2, 'Intro to Databases', 'Why SQL matters in modern data engineering.'),
(3, 'Data Pipelines 101', 'Batch processing vs real-time streaming.'),
(4, 'Network Protocols', 'Understanding TCP, UDP, and raw sockets.'),
(5, 'Computer Vision Basics', 'Frame processing with contours and color masks.'),
(6, 'Audio Signal Processing', 'FFT, spectral analysis, and sample rates.'),
(7, 'Docker Containers', 'Containerizing microservices cleanly.'),
(8, 'Linux Kernel Hooks', 'Exploring BPF and tracepoints.'),
(9, 'Distributed Storage', 'Replication strategies across nodes.');