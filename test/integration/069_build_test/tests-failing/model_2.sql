{{ config(materialized='table') }}

select * from {{ ref('snap_1') }}