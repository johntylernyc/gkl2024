CREATE OR REPLACE TABLE `python-sandbox-381204.gkl2024.batter_stats_agg` AS
SELECT 
  IDfg,
  Name,
  AVG(AB) AS avg_ab,
  AVG(R) AS avg_r,
  AVG(H) AS avg_h,
  AVG(_3B) as avg_3b,
  AVG(HR) as avg_hr, 
  AVG(RBI) as avg_rbi,
  AVG(SB) as avg_sb,
  SUM(H) AS total_hits,
  SUM(AB) AS total_at_bats,
  IF(SUM(AB) > 0, SUM(H) / SUM(AB), NULL) AS avg_avg, 
  SUM(BB) as total_walks,
  SUM(HBP) as total_hbp,
  SUM(PA) as total_pa, 
  SUM(SF) as total_sf,
  IF(SUM(PA) > 0, (SUM(H)+SUM(BB)+SUM(HBP)+SUM(SF))/ SUM(PA), NULL) as avg_obp, 
  SUM(_2B) as total_2b, 
  SUM(_3B) as total_3b, 
  SUM(HR) as total_hr, 
  IF(SUM(AB) > 0, (SUM(_1B)+(SUM(_2B)*2)+(SUM(_3B)*3)+(SUM(HR)*4)) / SUM(AB), NULL) as avg_slg,
  STDDEV_SAMP(AB) AS stddev_AB,
  STDDEV_SAMP(R) AS stddev_R,
  STDDEV_SAMP(H) AS stddev_H,
  STDDEV_SAMP(_3B) AS stddev_3B,
  STDDEV_SAMP(HR) AS stddev_HR,
  STDDEV_SAMP(RBI) AS stddev_RBI,
  STDDEV_SAMP(SB) AS stddev_SB,
  STDDEV_SAMP(`AVG`) AS stddev_AVG,
  STDDEV_SAMP(OBP) AS stddev_OBP,
  STDDEV_SAMP(SLG) AS stddev_SLG,
  COUNT(DISTINCT Season) AS SeasonsPlayed,
  MAX(Age) AS LatestAge, 
  eligible_positions
FROM 
  `python-sandbox-381204.gkl2024.batter_stats`
WHERE 
  Season BETWEEN 2021 AND 2023
GROUP BY 
  IDfg, Name, eligible_positions;