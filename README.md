# Stock Reorder Sheet

Turn an inventory CSV into reorder quantities using lead time, safety stock, and pack sizes.

## Quick start

Requires Python 3.11 or later. Uses the standard library and runs locally.

```bash
python3 tool.py stock.csv
```

Output is formatted JSON on standard output. Invalid inputs report an error on standard error and exit with status 1. Run the tool with --help for all arguments.

Target stock is daily sales × lead days rounded up, plus safety stock. Incoming stock counts toward availability. Order quantities round up to whole packs.

## Example input

**stock.csv**

```
sku,on_hand,incoming,daily_sales,lead_days,safety_stock,pack_size
A,2,1,1.2,5,2,4
B,20,0,1,5,2,1
```

## Example output

```json
{
  "orders": [
    {
      "sku": "A",
      "order_units": 8,
      "target_units": 8,
      "available_units": 3
    }
  ]
}
```

## License

[MIT](LICENSE).
