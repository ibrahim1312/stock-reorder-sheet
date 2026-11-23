"""Turn an inventory CSV into reorder quantities using lead time, safety stock, and pack sizes."""

import argparse
import json
from decimal import InvalidOperation
from pathlib import Path
import csv
from decimal import Decimal, ROUND_CEILING


def main():
    parser = argparse.ArgumentParser(description='Turn an inventory CSV into reorder quantities using lead time, safety stock, and pack sizes.')
    parser.add_argument("stock", type=Path)
    args = parser.parse_args()
    fields = {"sku", "on_hand", "incoming", "daily_sales", "lead_days", "safety_stock", "pack_size"}
    orders, seen = [], set()
    with args.stock.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if not fields <= set(reader.fieldnames or []):
            raise ValueError(f"Required columns: {', '.join(sorted(fields))}")
        for row in reader:
            sku = row["sku"].strip()
            if not sku or sku in seen:
                raise ValueError(f"Row {reader.line_num}: blank or duplicate SKU")
            seen.add(sku)
            demand = Decimal(row["daily_sales"])
            on_hand = int(row["on_hand"])
            incoming = int(row["incoming"])
            lead_days = int(row["lead_days"])
            safety_stock = int(row["safety_stock"])
            pack = int(row["pack_size"])
            if (not demand.is_finite() or demand < 0 or pack < 1
                    or min(on_hand, incoming, lead_days, safety_stock) < 0):
                raise ValueError(f"Row {reader.line_num}: quantities must be nonnegative and pack_size positive")
            target = int((demand * lead_days).to_integral_value(rounding=ROUND_CEILING)) + safety_stock
            shortage = target - on_hand - incoming
            if shortage > 0:
                units = ((shortage + pack - 1) // pack) * pack
                orders.append({"sku": sku, "order_units": units, "target_units": target,
                               "available_units": on_hand + incoming})
    report = {"orders": sorted(orders, key=lambda order: order["sku"])}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, OverflowError, InvalidOperation, TypeError, csv.Error) as error:
        raise SystemExit(f"Error: {error}") from None
