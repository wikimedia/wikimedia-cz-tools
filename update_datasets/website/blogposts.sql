USE datasets_website_p;

DROP TABLE IF EXISTS `blogposts`;

CREATE TABLE IF NOT EXISTS `blogposts` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `guid` varchar(255) NOT NULL,
  `post_date_gmt` datetime NOT NULL,
  `post_title` text NOT NULL,
  `post_name` varchar(255) NOT NULL,
  `post_content` longtext NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO blogposts SELECT ID, guid, post_date_gmt, post_title, post_name, post_content FROM wordpress_multisite.wp_5_posts WHERE post_type="post" AND post_status="publish";
