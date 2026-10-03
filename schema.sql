CREATE DATABASE IF NOT EXISTS primeflix;
USE primeflix;

CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 email VARCHAR(150) NOT NULL UNIQUE,
 phone VARCHAR(20) NOT NULL,
 password_hash VARCHAR(255) NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS titles (
 id INT AUTO_INCREMENT PRIMARY KEY,
 title VARCHAR(180) NOT NULL,
 description TEXT NOT NULL,
 genre VARCHAR(100),
 language VARCHAR(60),
 year INT,
 duration VARCHAR(30),
 rating DECIMAL(3,1) DEFAULT 0.0,
 poster VARCHAR(600),
 backdrop VARCHAR(600),
 featured TINYINT(1) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS watchlist (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NOT NULL,
 title_id INT NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 UNIQUE KEY unique_watch(user_id,title_id),
 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 FOREIGN KEY (title_id) REFERENCES titles(id) ON DELETE CASCADE
);

INSERT INTO titles(title,description,genre,language,year,duration,rating,poster,backdrop,featured) VALUES
('The Last Horizon','A former astronaut discovers a signal beyond the edge of the solar system and returns to space to uncover its source.','Sci-Fi • Adventure','English',2026,'2h 18m',8.7,'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=700&q=85','https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1800&q=85',1),
('Shadow Protocol','An intelligence analyst races against time after a classified operation is exposed.','Action • Thriller','English',2026,'2h 05m',8.3,'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=700&q=85','https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=1800&q=85',1),
('The Family Table','Three generations return to their hometown for a celebration that changes all of them.','Drama • Family','Tamil',2025,'1h 58m',8.1,'https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=700&q=85','https://images.unsplash.com/photo-1478145046317-39f10e56b5e9?auto=format&fit=crop&w=1800&q=85',0),
('Midnight Run','Two unlikely friends take one night-long road trip that turns into a hilarious adventure.','Comedy','Hindi',2025,'1h 49m',7.9,'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=700&q=85','https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1800&q=85',0),
('Wild Earth','A cinematic journey through forests, oceans and remote landscapes.','Documentary','English',2026,'1h 35m',9.0,'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=700&q=85','https://images.unsplash.com/photo-1473445361085-b9a07f55608b?auto=format&fit=crop&w=1800&q=85',0),
('Champions','An underdog team gets one final chance to change its story.','Sports • Drama','English',2025,'2h 02m',8.0,'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=700&q=85','https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1800&q=85',0);
