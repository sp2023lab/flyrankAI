from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas import SalesSummary


def _money(value: object) -> str:
    return f"GBP {value:,.2f}"


def _page_footer(canvas, document) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(20 * mm, 12 * mm, "FlyRank Backend AI Engineering")
    canvas.drawRightString(190 * mm, 12 * mm, f"Page {document.page}")
    canvas.restoreState()


def render_sales_report(
    output_path: Path,
    title: str,
    summary: SalesSummary,
    generated_at: datetime,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Shyam Popat",
        subject="Generated sales summary report",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=24,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=6,
            spaceAfter=5,
        )
    )

    elements = [
        Paragraph(title, styles["ReportTitle"]),
        Paragraph(
            f"Generated at {generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            styles["BodyText"],
        ),
        Spacer(1, 6 * mm),
        Paragraph("Executive summary", styles["SectionHeading"]),
    ]

    overview = Table(
        [
            ["Metric", "Value"],
            ["Total orders", f"{summary.total_orders:,}"],
            ["Gross revenue", _money(summary.gross_revenue)],
            ["Average order value", _money(summary.average_order_value)],
        ],
        colWidths=[80 * mm, 80 * mm],
        repeatRows=1,
    )
    overview.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.extend([overview, Spacer(1, 4 * mm)])

    elements.append(Paragraph("Orders by status", styles["SectionHeading"]))
    status_data = [["Status", "Orders", "Revenue"]]
    status_data.extend(
        [
            [metric.status.title(), metric.order_count, _money(metric.revenue)]
            for metric in summary.by_status
        ]
    )
    if len(status_data) == 1:
        status_data.append(["No data", 0, _money(0)])
    status_table = Table(status_data, colWidths=[70 * mm, 35 * mm, 55 * mm], repeatRows=1)
    status_table.setStyle(_standard_table_style())
    elements.extend([status_table, Spacer(1, 4 * mm)])

    elements.append(Paragraph("Daily activity (last 14 days)", styles["SectionHeading"]))
    daily_data = [["Date", "Orders", "Revenue"]]
    daily_data.extend(
        [[metric.date, metric.order_count, _money(metric.revenue)] for metric in summary.daily]
    )
    if len(daily_data) == 1:
        daily_data.append(["No data", 0, _money(0)])
    daily_table = Table(daily_data, colWidths=[70 * mm, 35 * mm, 55 * mm], repeatRows=1)
    daily_table.setStyle(_standard_table_style())
    elements.append(daily_table)

    document.build(elements, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return output_path.stat().st_size


def _standard_table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
