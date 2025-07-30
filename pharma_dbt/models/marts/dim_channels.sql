{{
  config(
    materialized='table'
  )
}}

with channel_data as (
    select distinct
        channel_name,
        count(*) as total_messages,
        count(case when has_image then 1 end) as total_images,
        count(case when has_media then 1 end) as total_media,
        avg(message_length) as avg_message_length,
        min(date_scraped) as first_seen,
        max(date_scraped) as last_seen
    from {{ ref('stg_telegram_messages') }}
    group by channel_name
)

select
    row_number() over (order by channel_name) as channel_id,
    channel_name,
    total_messages,
    total_images,
    total_media,
    round(avg_message_length, 2) as avg_message_length,
    first_seen,
    last_seen,
    current_timestamp as created_at
from channel_data 