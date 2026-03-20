def format_eod(payload: dict) -> str:
    """Format EOD report payload into thermal ESC/POS text."""
    template = payload.get("print_template", {})
    summary = payload.get("summary", {})
    waiter_rows = payload.get("waiter_rows", [])

    # We assume 80mm width which is ~42 characters for basic font
    width = 42
    
    # EOD Flags
    show_payment = template.get("eod_show_payment", True)
    show_items = template.get("eod_show_items", True)
    show_waiters = template.get("eod_show_waiters", True)

    def center(text: str) -> str:
        if not text: return ""
        padding = max(0, width - len(text))
        return " " * (padding // 2) + text + " " * (padding - padding // 2)

    def left_right(left: str, right: str) -> str:
        if not left: return right
        if not right: return left
        space = max(1, width - len(left) - len(right))
        return left + " " * space + right

    def divider(char: str) -> str:
        return char * width

    def inr(paise: int) -> str:
        return f"{paise / 100:,.2f}"

    lines = []
    
    # Top Padding
    top_pad = template.get("top_padding", 0)
    for _ in range(top_pad):
        lines.append("")

    # Header
    lines.append(center("*** EOD REPORT ***"))
    hotel_name = template.get("restaurant_name", "EOD Report")
    lines.append(left_right(hotel_name, summary.get("date", "")))
    lines.append(divider("="))
    
    # KPI Section
    lines.append(left_right("Total Bills", str(summary.get("bill_count", 0))))
    lines.append(left_right("Total Revenue", inr(summary.get("total_paise", 0))))
    lines.append(left_right("Discounts", inr(summary.get("discount_paise", 0))))
    lines.append(left_right("Voids", str(summary.get("void_count", 0))))
    lines.append(divider("="))

    # Payment Summary
    if show_payment and summary.get("payment_breakdown"):
        lines.append(center("PAYMENT SUMMARY"))
        lines.append(divider("-"))
        pb = summary["payment_breakdown"]
        for method, amt in pb.items():
            lines.append(left_right(method.capitalize(), inr(amt)))
        lines.append(divider("~"))
        total_revenue = sum(pb.values())
        lines.append(left_right(f"Total ({summary.get('bill_count', 0)} bills)", inr(total_revenue)))
        lines.append(divider("="))

    # Items Sold
    if show_items and summary.get("top_items"):
        lines.append(center("ITEMS SOLD"))
        lines.append(divider("-"))
        for item in summary["top_items"]:
            # Max item name length ~34 chars
            n = item["name"][:34]
            lines.append(left_right(n, f"x{item['qty']}"))
        lines.append(divider("="))

    # Waiter Performance
    if show_waiters and waiter_rows:
        lines.append(center("WAITER PERFORMANCE"))
        lines.append(divider("-"))
        for w in waiter_rows:
            name = w["waiter_name"][:12]
            bills = f"{w['bill_count']} bills"
            rev = inr(w['revenue_paise'])
            
            # Left align name (12), center bills, right align rev
            # Name..........18 bills........8,000.00
            space1 = " " * max(1, (width - len(name) - len(bills) - len(rev)) // 2)
            space2 = " " * max(1, width - len(name) - len(space1) - len(bills) - len(rev))
            lines.append(f"{name}{space1}{bills}{space2}{rev}")
        lines.append(divider("="))

    # Footer
    footer = template.get("footer_message", "")
    if footer:
        lines.append(center(footer))
        
    lines.append(center("End of report"))

    # Bottom Padding
    bottom_pad = template.get("bottom_padding", 2)
    for _ in range(bottom_pad):
        lines.append("")

    return "\n".join(lines)
