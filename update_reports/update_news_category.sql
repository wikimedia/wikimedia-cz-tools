TRUNCATE TABLE wmcz_reports_p.news_category;

INSERT INTO wmcz_reports_p.news_category

SELECT
	object_id,
	name,
	slug
FROM wordpress_multisite.wp_6_term_relationships
JOIN wordpress_multisite.wp_6_term_taxonomy ON wp_6_term_taxonomy.term_taxonomy_id=wp_6_term_relationships.term_taxonomy_id
JOIN wordpress_multisite.wp_6_terms ON wp_6_term_taxonomy.term_id=wp_6_terms.term_id
WHERE taxonomy="category";
