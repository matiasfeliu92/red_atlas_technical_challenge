{{ config(materialized='incremental', schema='stage') }}

with staging_props as (
  select
    regexp_extract(replace(filename, '\\', '/'), '(for_rent|for_sale)', 1) as path,
    regexp_extract(replace(filename, '\\', '/'), '([0-9]{8})\.json', 1) as fecha_raw,
    case
      when regexp_extract(replace(filename, '\\', '/'), '([0-9]{8})\.json', 1) = '' then null
      else strptime(regexp_extract(replace(filename, '\\', '/'), '([0-9]{8})\.json', 1), '%Y%m%d')::DATE
    end as fecha,
    json as raw_json,
    json_extract(raw_json, '$.zpid') as zpid,
    filename
  from read_json_objects_auto('../data/**/*.json')
)

select
  path,
  fecha,
  raw_json,
  zpid
from staging_props
{% if is_incremental() %}
where zpid not in (select distinct zpid from {{ this }})
{% endif %}
