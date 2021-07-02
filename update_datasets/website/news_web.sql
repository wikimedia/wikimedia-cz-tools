USE datasets_website_p;

DROP TABLE IF EXISTS `news_web`;

CREATE TABLE `news_web` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `guid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `post_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `post_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `post_content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO news_web SELECT ID, guid, post_date_gmt, post_title, post_name, post_content FROM wordpress_multisite.wp_6_posts WHERE post_type="post" AND post_status="publish";
