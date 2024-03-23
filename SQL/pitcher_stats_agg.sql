CREATE OR REPLACE TABLE `python-sandbox-381204.gkl2024.pitcher_stats_agg` AS

WITH AvgQs AS (
  SELECT 
    IDfg,
    AVG(GREATEST(CASE 
                   WHEN IP IS NOT NULL AND ERA IS NOT NULL AND GS IS NOT NULL 
                   THEN ((IP / (32 * 6.15)) - (0.11 * ERA)) * GS 
                   ELSE 0 
                 END, 0)) AS avg_qs
  FROM 
    `python-sandbox-381204.gkl2024.pitcher_stats`
  WHERE 
    Season BETWEEN 2021 AND 2023
  GROUP BY 
    IDfg
)

SELECT 
  ps.IDfg,
  Name,
  AVG(IP) AS avg_ip,
  AVG(G) AS avg_app,
  AVG(W) AS avg_w,
  AVG(SV) AS avg_sv,
  AVG(SO) AS avg_k,
  AVG(HLD) AS avg_hld,
  AVG(aqs.avg_qs) AS avg_qs, -- Use AVG here to avoid the grouping error
  (SUM(ER) * 9) / NULLIF(SUM(IP), 0) AS avg_era,
  (SUM(BB) + SUM(H)) / NULLIF(SUM(IP), 0) AS avg_whip,
  AVG(CASE WHEN BB > 0 THEN SO / BB ELSE NULL END) AS avg_k_bb,
  SUM(IP) AS total_ip,
  COUNT(*) AS total_app,
  SUM(W) AS total_w,
  SUM(SV) AS total_sv,
  SUM(SO) AS total_k,
  SUM(HLD) AS total_hld,
  SUM(BB) AS total_bb,
  SUM(H) AS total_h,
  SUM(ER) AS total_er,
  STDDEV_SAMP(IP) AS stddev_ip,
  STDDEV_SAMP(G) AS stddev_app,
  STDDEV_SAMP(W) AS stddev_w,
  STDDEV_SAMP(SV) AS stddev_sv,
  STDDEV_SAMP(SO) AS stddev_k,
  STDDEV_SAMP(HLD) AS stddev_hld,
  STDDEV_SAMP(aqs.avg_qs) AS stddev_qs, -- Aggregate stddev_qs here as well
  STDDEV_SAMP(ERA) as stddev_era,
  STDDEV_SAMP(WHIP) as stddev_whip,
  STDDEV_SAMP(K_BB) as stddev_k_bb,
  COUNT(DISTINCT Season) AS SeasonsPlayed,
  MAX(Age) AS LatestAge,
  eligible_positions
  
FROM 
  `python-sandbox-381204.gkl2024.pitcher_stats` ps
JOIN 
  AvgQs aqs ON ps.IDfg = aqs.IDfg
WHERE 
  Season BETWEEN 2021 AND 2023
GROUP BY 
  ps.IDfg, Name, eligible_positions;
