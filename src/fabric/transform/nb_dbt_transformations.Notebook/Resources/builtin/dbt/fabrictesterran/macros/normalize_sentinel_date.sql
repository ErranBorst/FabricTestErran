{#
  Operational systems often use a sentinel date (e.g. 1899-12-30, 0001-01-01) to mean "no value"
  instead of a real NULL. Centralize that cleanup here so every silver model treats it the same way.

  <<ADJUST ME>>: the dummy source has no sentinel convention, so this ships with a placeholder
  ('1900-01-01'). Replace it with the real sentinel value(s) for your source system once a real
  entity is added, or pass a different one per call via `sentinel_value`.
#}
{% macro normalize_sentinel_date(column_name, sentinel_value='1900-01-01') %}
    case
        when cast({{ column_name }} as date) = cast('{{ sentinel_value }}' as date) then null
        else {{ column_name }}
    end
{% endmacro %}
