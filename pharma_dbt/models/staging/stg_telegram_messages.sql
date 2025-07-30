{{
  config(
    materialized='view'
  )
}}

with source as (
    select * from {{ source('raw', 'telegram_messages') }}
),

cleaned as (
    select
        id as message_id,
        channel_name,
        date_scraped,
        message_data->>'id' as telegram_message_id,
        message_data->>'date' as message_date,
        message_data->>'message' as message_text,
        message_data->>'from_id' as from_id,
        message_data->>'peer_id' as peer_id,
        message_data->>'reply_to' as reply_to,
        message_data->>'media' as media_info,
        message_data->>'reply_markup' as reply_markup,
        message_data->>'entities' as entities,
        message_data->>'views' as views,
        message_data->>'forwards' as forwards,
        message_data->>'replies' as replies,
        message_data->>'edit_date' as edit_date,
        message_data->>'post_author' as post_author,
        message_data->>'grouped_id' as grouped_id,
        message_data->>'restriction_reason' as restriction_reason,
        message_data->>'ttl_period' as ttl_period,
        message_data->>'downloaded_image' as downloaded_image,
        created_at,
        -- Derived fields
        case when message_data->>'media' is not null then true else false end as has_media,
        case when message_data->>'downloaded_image' is not null then true else false end as has_image,
        length(message_data->>'message') as message_length,
        case when message_data->>'message' ~ '.*[0-9].*' then true else false end as contains_numbers
    from source
)

select * from cleaned 