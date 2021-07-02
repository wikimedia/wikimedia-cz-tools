TRUNCATE TABLE wmcz_reports_p.short_link_clicks;

INSERT INTO wmcz_reports_p.short_link_clicks SELECT short_url, DATE(clicks.created_at), COUNT(*) FROM shortener.clicks JOIN shortener.links ON links.id=link_id GROUP BY short_url, DATE(clicks.created_at) ORDER BY DATE(clicks.created_at);
