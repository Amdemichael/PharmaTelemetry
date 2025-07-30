{{
  config(
    materialized='table'
  )
}}

with messages as (
    select
        message_id,
        channel_name,
        date_scraped,
        telegram_message_id,
        message_date,
        message_text,
        has_media,
        has_image,
        message_length,
        contains_numbers,
        downloaded_image,
        created_at
    from {{ ref('stg_telegram_messages') }}
),

channels as (
    select channel_id, channel_name
    from {{ ref('dim_channels') }}
),

dates as (
    select date_key, year, month, day, day_of_week, day_name, day_type
    from {{ ref('dim_dates') }}
)

select
    m.message_id,
    c.channel_id,
    d.date_key,
    m.telegram_message_id,
    m.message_date,
    m.message_text,
    m.has_media,
    m.has_image,
    m.message_length,
    m.contains_numbers,
    m.downloaded_image,
    m.created_at
from messages m
left join channels c on m.channel_name = c.channel_name
left join dates d on m.date_scraped = d.date_key 