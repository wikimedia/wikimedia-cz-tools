TRUNCATE TABLE wmcz_web_posts_p.news_web;

INSERT INTO wmcz_web_posts_p.news_web SELECT ID, guid, post_date_gmt, post_title, post_name, post_content FROM wordpress_multisite.wp_6_posts WHERE post_type="post" AND post_status="publish";
