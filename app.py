from flask import Flask, render_template
from sqlalchemy import create_engine, URL
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os




# ==========================================================
# FLASK APPLICATION
# ==========================================================

app = Flask(__name__)


# ==========================================================
# MYSQL DATABASE CONNECTION
# ==========================================================

password = "Neeraj@2007"

connection_url = URL.create(
    "mysql+mysqlconnector",
    username="root",
    password=password,
    host="localhost",
    port=3306,
    database="supply_chain_db"
)

engine = create_engine(connection_url)


# ==========================================================
# STATIC FOLDER
# ==========================================================

static_folder = app.static_folder

os.makedirs(static_folder, exist_ok=True)


# ==========================================================
# DASHBOARD ROUTE
# ==========================================================

@app.route("/")
def dashboard():

    # ======================================================
    # 1. KPI SUMMARY
    # ======================================================

    summary_query = """
    SELECT
        SUM(Sales) AS Total_Sales,

        COUNT(*) AS Total_Orders,

        COUNT(DISTINCT Product_ID) AS Total_Products,

        COUNT(DISTINCT Supplier_ID) AS Total_Suppliers,

        SUM(
            CASE
                WHEN Delivery_Status = 'Delayed'
                THEN 1
                ELSE 0
            END
        ) AS Delayed_Orders,

        AVG(Delivery_Days) AS Average_Delivery_Days

    FROM supply_chain;
    """

    summary = pd.read_sql(
        summary_query,
        engine
    )

    total_sales = summary["Total_Sales"].iloc[0]

    total_orders = summary["Total_Orders"].iloc[0]

    total_products = summary["Total_Products"].iloc[0]

    total_suppliers = summary["Total_Suppliers"].iloc[0]

    delayed_orders = summary["Delayed_Orders"].iloc[0]

    average_delivery_days = summary[
        "Average_Delivery_Days"
    ].iloc[0]


    # ======================================================
    # 2. CATEGORY-WISE SALES
    # ======================================================

    category_query = """
    SELECT
        Category,
        SUM(Sales) AS Total_Sales

    FROM supply_chain

    GROUP BY Category

    ORDER BY Total_Sales DESC;
    """

    category_sales = pd.read_sql(
        category_query,
        engine
    )


    plt.figure(figsize=(9, 5))

    plt.bar(
        category_sales["Category"],
        category_sales["Total_Sales"]
    )

    plt.title("Category-wise Sales")

    plt.xlabel("Category")

    plt.ylabel("Total Sales")

    plt.xticks(rotation=20)

    plt.tight_layout()


    category_chart_path = os.path.join(
        static_folder,
        "category_sales.png"
    )

    plt.savefig(
        category_chart_path
    )

    plt.close()


    # ======================================================
    # 3. SUPPLIER ON-TIME DELIVERY RATE
    # ======================================================

    supplier_query = """
    SELECT
        Supplier_Name,

        COUNT(*) AS Total_Orders,

        SUM(
            CASE
                WHEN Delivery_Status = 'On Time'
                THEN 1
                ELSE 0
            END
        ) AS On_Time_Orders,

        ROUND(
            SUM(
                CASE
                    WHEN Delivery_Status = 'On Time'
                    THEN 1
                    ELSE 0
                END
            ) * 100.0 / COUNT(*),
            2
        ) AS On_Time_Rate

    FROM supply_chain

    GROUP BY Supplier_Name

    ORDER BY On_Time_Rate DESC;
    """

    supplier_performance = pd.read_sql(
        supplier_query,
        engine
    )


    plt.figure(figsize=(9, 5))

    plt.bar(
        supplier_performance["Supplier_Name"],
        supplier_performance["On_Time_Rate"]
    )

    plt.title(
        "Supplier On-Time Delivery Rate"
    )

    plt.xlabel("Supplier")

    plt.ylabel("On-Time Rate (%)")

    plt.xticks(rotation=25)

    plt.ylim(0, 100)

    plt.tight_layout()


    supplier_chart_path = os.path.join(
        static_folder,
        "supplier_on_time_rate.png"
    )

    plt.savefig(
        supplier_chart_path
    )

    plt.close()


    # ======================================================
    # 4. LOW STOCK PRODUCTS
    # ======================================================

    low_stock_query = """
    SELECT
        Product_Name,
        Stock,
        Reorder_Level

    FROM supply_chain

    WHERE Stock < Reorder_Level

    ORDER BY Stock ASC

    LIMIT 15;
    """

    low_stock = pd.read_sql(
        low_stock_query,
        engine
    )


    low_stock_records = low_stock.to_dict(
        orient="records"
    )


    # ======================================================
    # 5. MONTHLY SALES TREND
    # ======================================================

    monthly_sales_query = """
    SELECT
        MONTH(Order_Date) AS Month_Number,

        MONTHNAME(Order_Date) AS Month_Name,

        SUM(Sales) AS Total_Sales

    FROM supply_chain

    GROUP BY
        MONTH(Order_Date),
        MONTHNAME(Order_Date)

    ORDER BY
        Month_Number;
    """

    monthly_sales = pd.read_sql(
        monthly_sales_query,
        engine
    )


    plt.figure(figsize=(10, 5))

    plt.plot(
        monthly_sales["Month_Name"],
        monthly_sales["Total_Sales"],
        marker="o"
    )

    plt.title(
        "Monthly Sales Trend"
    )

    plt.xlabel("Month")

    plt.ylabel("Total Sales")

    plt.xticks(rotation=30)

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()


    monthly_chart_path = os.path.join(
        static_folder,
        "monthly_sales.png"
    )

    plt.savefig(
        monthly_chart_path
    )

    plt.close()


    # ======================================================
    # 6. DELAYED ORDERS BY SUPPLIER
    # ======================================================

    delayed_supplier_query = """
    SELECT
        Supplier_Name,

        COUNT(*) AS Delayed_Orders

    FROM supply_chain

    WHERE Delivery_Status = 'Delayed'

    GROUP BY Supplier_Name

    ORDER BY Delayed_Orders DESC;
    """

    delayed_supplier = pd.read_sql(
        delayed_supplier_query,
        engine
    )


    plt.figure(figsize=(9, 5))

    plt.bar(
        delayed_supplier["Supplier_Name"],
        delayed_supplier["Delayed_Orders"]
    )

    plt.title(
        "Delayed Orders by Supplier"
    )

    plt.xlabel("Supplier")

    plt.ylabel("Number of Delayed Orders")

    plt.xticks(rotation=25)

    plt.tight_layout()


    delayed_supplier_chart_path = os.path.join(
        static_folder,
        "delayed_orders_supplier.png"
    )

    plt.savefig(
        delayed_supplier_chart_path
    )

    plt.close()


    # ======================================================
    # 7. DELAYED ORDERS BY MONTH
    # ======================================================

    delayed_month_query = """
    SELECT
        MONTH(Order_Date) AS Month_Number,

        MONTHNAME(Order_Date) AS Month_Name,

        COUNT(*) AS Delayed_Orders

    FROM supply_chain

    WHERE Delivery_Status = 'Delayed'

    GROUP BY
        MONTH(Order_Date),
        MONTHNAME(Order_Date)

    ORDER BY
        Month_Number;
    """

    delayed_month = pd.read_sql(
        delayed_month_query,
        engine
    )


    plt.figure(figsize=(10, 5))

    plt.plot(
        delayed_month["Month_Name"],
        delayed_month["Delayed_Orders"],
        marker="o"
    )

    plt.title(
        "Delayed Orders by Month"
    )

    plt.xlabel("Month")

    plt.ylabel("Delayed Orders")

    plt.xticks(rotation=30)

    plt.grid(
        True,
        alpha=0.3
    )

    plt.tight_layout()


    delayed_month_chart_path = os.path.join(
        static_folder,
        "delayed_orders_month.png"
    )

    plt.savefig(
        delayed_month_chart_path
    )

    plt.close()


    # ======================================================
    # 8. SEND DATA TO HTML
    # ======================================================

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


# ==========================================================
# RUN FLASK APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

