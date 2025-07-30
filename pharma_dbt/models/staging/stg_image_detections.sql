{{
  config(
    materialized='view'
  )
}}

-- This staging model reads from raw.image_detections table
-- populated by the YOLO enrichment process

SELECT
  message_id,
  detected_object_class,
  confidence_score,
  created_at as detection_timestamp,
  image_path,
  channel_name,
  message_date::date as message_date
FROM {{ source('raw', 'image_detections') }}
WHERE detected_object_class IS NOT NULL 