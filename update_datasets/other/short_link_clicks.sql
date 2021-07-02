USE datasets_other_p;

DROP TABLE IF EXISTS `short_link_clicks`;
CREATE TABLE IF NOT EXISTS `short_link_clicks` (
  `short_url` varchar(250) CHARACTER SET utf8 NOT NULL,
  `date` date NOT NULL,
  `link_hits` int(11) NOT NULL,
  PRIMARY KEY (`short_url`,`date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO short_link_clicks SELECT short_url, DATE(clicks.created_at), COUNT(*) FROM shortener.clicks JOIN shortener.links ON links.id=link_id GROUP BY short_url, DATE(clicks.created_at) ORDER BY DATE(clicks.created_at);
