{{
  config(
    materialized='table'
  )
}}

with date_spine as (
    select distinct date_scraped as date_key
    from {{ ref('stg_telegram_messages') }}
),

date_attributes as (
    select
        date_key,
        extract(year from date_key) as year,
        extract(month from date_key) as month,
        extract(day from date_key) as day,
        extract(dow from date_key) as day_of_week,
        extract(doy from date_key) as day_of_year,
        to_char(date_key, 'Month') as month_name,
        to_char(date_key, 'Day') as day_name,
        case when extract(dow from date_key) in (0, 6) then 'Weekend' else 'Weekday' end as day_type
    from date_spine
)

select * from date_attributes 