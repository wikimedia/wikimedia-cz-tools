USE datasets_website_p;

DROP TABLE IF EXISTS `news_tags`;

CREATE TABLE `news_tags` (
  `post_id` bigint(20) unsigned NOT NULL DEFAULT 0,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `slug` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO news_tags

SELECT
        object_id,
        name,
        slug
FROM wordpress_multisite.wp_6_term_relationships
JOIN wordpress_multisite.wp_6_term_taxonomy ON wp_6_term_taxonomy.term_taxonomy_id=wp_6_term_relationships.term_taxonomy_id
JOIN wordpress_multisite.wp_6_terms ON wp_6_term_taxonomy.term_id=wp_6_terms.term_id
WHERE taxonomy="post_tag";
