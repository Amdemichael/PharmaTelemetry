{{
  config(
    materialized='table'
  )
}}

WITH image_detections AS (
  SELECT 
    message_id,
    detected_object_class,
    confidence_score,
    detection_timestamp,
    image_path,
    channel_name,
    message_date
  FROM {{ ref('stg_image_detections') }}
  WHERE detected_object_class IS NOT NULL
)

SELECT 
  md5(concat(message_id, detected_object_class, detection_timestamp)) as detection_id,
  message_id,
  detected_object_class,
  confidence_score,
  detection_timestamp,
  image_path,
  channel_name,
  message_date,
  CASE 
    WHEN confidence_score >= 0.8 THEN 'high'
    WHEN confidence_score >= 0.6 THEN 'medium'
    ELSE 'low'
  END as confidence_level
FROM image_detections 