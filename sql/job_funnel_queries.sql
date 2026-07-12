-- Example SQL queries that mirror the Python analysis.
-- Table name assumed: job_applications

-- Overall funnel metrics
SELECT
  COUNT(*) AS total_applications,
  SUM(CASE WHEN current_status = 'Active' THEN 1 ELSE 0 END) AS active_applications,
  SUM(CASE WHEN stage_reached IN ('Interview', 'Take-home', 'Offer') THEN 1 ELSE 0 END) AS interview_opportunities,
  SUM(CASE WHEN stage_reached = 'Offer' THEN 1 ELSE 0 END) AS offers,
  ROUND(100.0 * SUM(CASE WHEN response_date IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS response_rate_pct,
  ROUND(100.0 * SUM(CASE WHEN stage_reached IN ('Interview', 'Take-home', 'Offer') THEN 1 ELSE 0 END) / COUNT(*), 1) AS interview_rate_pct,
  ROUND(100.0 * SUM(CASE WHEN stage_reached = 'Offer' THEN 1 ELSE 0 END) / COUNT(*), 1) AS offer_rate_pct
FROM job_applications;

-- Source performance
SELECT
  source,
  COUNT(*) AS applications,
  SUM(CASE WHEN response_date IS NOT NULL THEN 1 ELSE 0 END) AS responses,
  SUM(CASE WHEN stage_reached IN ('Interview', 'Take-home', 'Offer') THEN 1 ELSE 0 END) AS interview_opportunities,
  ROUND(100.0 * SUM(CASE WHEN stage_reached IN ('Interview', 'Take-home', 'Offer') THEN 1 ELSE 0 END) / COUNT(*), 1) AS interview_rate_pct
FROM job_applications
GROUP BY source
ORDER BY interview_rate_pct DESC, applications DESC;

-- Weekly application activity
SELECT
  DATE_TRUNC('week', application_date) AS application_week,
  COUNT(*) AS applications
FROM job_applications
GROUP BY DATE_TRUNC('week', application_date)
ORDER BY application_week;
