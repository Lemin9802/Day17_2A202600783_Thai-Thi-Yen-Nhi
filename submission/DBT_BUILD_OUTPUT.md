# dbt Build Output

## Command

```powershell
cd dbt_project
$env:DBT_PROFILES_DIR="."
dbt build
```

## Output

```	ext
04:06:57  Running with dbt=1.11.11
04:06:58  Registered adapter: duckdb=1.10.1
04:06:58  Found 2 models, 1 seed, 7 data tests, 485 macros, 1 unit test
04:06:58  
04:06:58  Concurrency: 1 threads (target='dev')
04:06:58  
04:06:59  1 of 11 START seed file main.raw_orders ........................................ [RUN]
04:06:59  1 of 11 OK loaded seed file main.raw_orders .................................... [INSERT 16 in 0.09s]
04:06:59  2 of 11 START unit_test stg_orders::stg_orders_dedups_on_order_id .............. [RUN]
04:06:59  2 of 11 PASS stg_orders::stg_orders_dedups_on_order_id ......................... [PASS in 0.31s]
04:06:59  3 of 11 START sql view model main.stg_orders ................................... [RUN]
04:06:59  3 of 11 OK created sql view model main.stg_orders .............................. [OK in 0.08s]
04:06:59  4 of 11 START test not_null_stg_orders_amount .................................. [RUN]
04:06:59  4 of 11 PASS not_null_stg_orders_amount ........................................ [PASS in 0.05s]
04:06:59  5 of 11 START test not_null_stg_orders_order_id ................................ [RUN]
04:06:59  5 of 11 PASS not_null_stg_orders_order_id ...................................... [PASS in 0.02s]
04:06:59  6 of 11 START test not_null_stg_orders_user_id ................................. [RUN]
04:06:59  6 of 11 PASS not_null_stg_orders_user_id ....................................... [PASS in 0.02s]
04:06:59  7 of 11 START test unique_stg_orders_order_id .................................. [RUN]
04:06:59  7 of 11 PASS unique_stg_orders_order_id ........................................ [PASS in 0.03s]
04:06:59  8 of 11 START sql table model main.gold_daily_orders ........................... [RUN]
04:06:59  8 of 11 OK created sql table model main.gold_daily_orders ...................... [OK in 0.07s]
04:06:59  9 of 11 START test not_null_gold_daily_orders_order_date ....................... [RUN]
04:06:59  9 of 11 PASS not_null_gold_daily_orders_order_date ............................. [PASS in 0.02s]
04:06:59  10 of 11 START test not_null_gold_daily_orders_revenue ......................... [RUN]
04:06:59  10 of 11 PASS not_null_gold_daily_orders_revenue ............................... [PASS in 0.02s]
04:06:59  11 of 11 START test unique_gold_daily_orders_order_date ........................ [RUN]
04:06:59  11 of 11 PASS unique_gold_daily_orders_order_date .............................. [PASS in 0.02s]
04:06:59  
04:06:59  Finished running 1 seed, 1 table model, 7 data tests, 1 unit test, 1 view model in 0 hours 0 minutes and 0.99 seconds (0.99s).
04:06:59  
04:06:59  Completed successfully
04:06:59  
04:06:59  Done. PASS=11 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=11

```
