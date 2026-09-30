from flask import Flask, render_template
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os


# ==========================================
# Paths
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "supply_chain.csv"
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)


# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)


# ==========================================
# Dashboard Route
# ==========================================

@app.route("/")
def home():

    # --------------------------------------
    # Load CSV Dataset
    # --------------------------------------

    df = pd.read_csv(DATA_FILE)

    # Convert date column
    df["Order_Date"] = pd.to_datetime(
        df["Order_Date"],
        errors="coerce"
    )

    # Convert numeric columns
    df["Sales"] = pd.to_numeric(
        df["Sales"],
        errors="coerce"
    )

    df["Delivery_Days"] = pd.to_numeric(
        df["Delivery_Days"],
        errors="coerce"
    )

    df["Stock"] = pd.to_numeric(
        df["Stock"],
        errors="coerce"
    )

    df["Reorder_Level"] = pd.to_numeric(
        df["Reorder_Level"],
        errors="coerce"
    )


    # ======================================
    # KPI Summary
    # ======================================

    total_sales = df["Sales"].sum()

    total_orders = len(df)

    total_products = df["Product_ID"].nunique()

    total_suppliers = df["Supplier_ID"].nunique()

    delayed_orders = (
        df["Delivery_Status"] == "Delayed"
    ).sum()

    average_delivery_days = (
        df["Delivery_Days"].mean()
    )


    # ======================================
    # Category-wise Sales
    # ======================================

    category_sales = (
        df.groupby("Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        category_sales.index,
        category_sales.values
    )

    plt.title("Category-wise Sales")
    plt.xlabel("Category")
    plt.ylabel("Total Sales")
    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            STATIC_DIR,
            "category_sales.png"
        )
    )

    plt.close()


    # ======================================
    # Supplier On-Time Delivery Rate
    # ======================================

    supplier_performance = (
        df.assign(
            On_Time=df["Delivery_Status"]
            .eq("On Time")
            .astype(int)
        )
        .groupby("Supplier_Name")["On_Time"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        supplier_performance.index,
        supplier_performance.values
    )

    plt.title("Supplier On-Time Delivery Rate")
    plt.xlabel("Supplier")
    plt.ylabel("On-Time Rate (%)")
    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            STATIC_DIR,
            "supplier_on_time_rate.png"
        )
    )

    plt.close()


    # ======================================
    # Low Stock Products
    # ======================================

    low_stock = df[
        df["Stock"] < df["Reorder_Level"]
    ][
        [
            "Product_Name",
            "Stock",
            "Reorder_Level"
        ]
    ].sort_values(
        "Stock"
    ).head(15)

    low_stock_records = low_stock.to_dict(
        orient="records"
    )


    # ======================================
    # Monthly Sales Trend
    # ======================================

    monthly_sales = (
        df.dropna(subset=["Order_Date"])
        .assign(
            Month_Number=lambda x:
            x["Order_Date"].dt.month,

            Month_Name=lambda x:
            x["Order_Date"].dt.month_name()
        )
        .groupby(
            ["Month_Number", "Month_Name"]
        )["Sales"]
        .sum()
        .reset_index()
        .sort_values("Month_Number")
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        monthly_sales["Month_Name"],
        monthly_sales["Sales"],
        marker="o"
    )

    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Total Sales")
    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            STATIC_DIR,
            "monthly_sales.png"
        )
    )

    plt.close()


    # ======================================
    # Delayed Orders by Supplier
    # ======================================

    delayed_supplier = (
        df[
            df["Delivery_Status"] == "Delayed"
        ]
        .groupby("Supplier_Name")
        .size()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(8, 5))

    plt.bar(
        delayed_supplier.index,
        delayed_supplier.values
    )

    plt.title("Delayed Orders by Supplier")
    plt.xlabel("Supplier")
    plt.ylabel("Delayed Orders")
    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            STATIC_DIR,
            "delayed_orders_supplier.png"
        )
    )

    plt.close()


    # ======================================
    # Delayed Orders by Month
    # ======================================

    delayed_month = (
        df[
            df["Delivery_Status"] == "Delayed"
        ]
        .dropna(subset=["Order_Date"])
        .assign(
            Month_Number=lambda x:
            x["Order_Date"].dt.month,

            Month_Name=lambda x:
            x["Order_Date"].dt.month_name()
        )
        .groupby(
            ["Month_Number", "Month_Name"]
        )
        .size()
        .reset_index(
            name="Delayed_Orders"
        )
        .sort_values("Month_Number")
    )

    plt.figure(figsize=(8, 5))

    plt.plot(
        delayed_month["Month_Name"],
        delayed_month["Delayed_Orders"],
        marker="o"
    )

    plt.title("Delayed Orders by Month")
    plt.xlabel("Month")
    plt.ylabel("Delayed Orders")
    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            STATIC_DIR,
            "delayed_orders_month.png"
        )
    )

    plt.close()


    # ======================================
    # Send Data to HTML
    # ======================================

    return render_template(
        "index.html",

        total_sales=total_sales,

        total_orders=total_orders,

        total_products=total_products,

        total_suppliers=total_suppliers,

        delayed_orders=delayed_orders,

        average_delivery_days=average_delivery_days,

        low_stock=low_stock_records
    )


# ==========================================
# Run Flask Application
# ==========================================

if __name__ == "__main__":

    port = int(
        os.getenv("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )