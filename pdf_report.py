# pdf_report.py
"""
This blueprint allows you to download a PDF report containing
all six charts (bar, pie, line, forecast, gauge, and scatter).
Make sure you have installed:
  - pdfkit         (pip install pdfkit)
  - wkhtmltopdf    (system-wide install from https://wkhtmltopdf.org/downloads.html)
  - plotly         (pip install plotly)
  - kaleido        (pip install -U kaleido)

Also ensure the path to wkhtmltopdf.exe is correct in pdfkit.configuration().
"""

from flask import Blueprint, render_template, request, make_response
import pdfkit
import plotly.graph_objs as go
import plotly.io as pio
import base64
import math
import pickle

# Create a blueprint
pdf_report_bp = Blueprint("pdf_report", __name__)

# Load your model if needed for forecasts
model = pickle.load(open("Model/model.pkl", "rb"))

@pdf_report_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    # 1) Get data from the form
    city_name    = request.form.get("city_name", "")
    crime_type   = request.form.get("crime_type", "")
    year_str     = request.form.get("year", "")
    crime_status = request.form.get("crime_status", "")
    crime_rate   = float(request.form.get("crime_rate", 0))
    cases        = int(float(request.form.get("cases", 0)))
    population   = float(request.form.get("population", 0))

    # For forecast & scatter: initialize defaults
    city_code_str  = request.form.get("city_code", "")
    crime_code_str = request.form.get("crime_code", "")
    city_code  = None
    crime_code = None

    # Convert year_str to int (handle empty or invalid)
    try:
        year = int(year_str)
    except ValueError:
        year = 2011  # default fallback

    # 2) Create Charts

    # -- 2.1 Bar Chart --
    try:
        bar_fig = go.Figure()
        bar_fig.add_trace(go.Bar(
            x=["Crime Rate", "Estimated Cases", "Population (Lakhs)"],
            y=[crime_rate, cases, population],
            marker=dict(color=["red", "blue", "green"])
        ))
        bar_fig.update_layout(
            title=f"Crime Statistics in {city_name} for {year}",
            xaxis_title="Metrics",
            yaxis_title="Value",
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        bar_img = pio.to_image(bar_fig, format="png")
        bar_chart_base64 = base64.b64encode(bar_img).decode("utf-8")
    except Exception as e:
        print("Bar Chart Error:", e)
        bar_chart_base64 = ""

    # -- 2.2 Pie Chart --
    try:
        pie_fig = go.Figure()
        pie_fig.add_trace(go.Pie(
            labels=[
                "Crime Committed by Juveniles", "Crime against SC", "Crime against ST",
                "Crime against Senior Citizen", "Crime against children", "Crime against women",
                "Cyber Crimes", "Economic Offences", "Kidnapping", "Murder"
            ],
            values=[20, 15, 10, 8, 25, 30, 12, 18, 22, 14],
            textposition="inside"
        ))
        pie_fig.update_layout(
            title="Crime Type Distribution",
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        pie_img = pio.to_image(pie_fig, format="png")
        pie_chart_base64 = base64.b64encode(pie_img).decode("utf-8")
    except Exception as e:
        print("Pie Chart Error:", e)
        pie_chart_base64 = ""

    # -- 2.3 Line Chart (sorted by year) --
    try:
        line_years = [2011, 2013, 2015, 2017, 2019, 2021, year]
        line_rates = [5, 7, 12, 15, 20, 25, crime_rate]

        # Sort the (year, rate) pairs to avoid bending issues
        pairs = sorted(zip(line_years, line_rates), key=lambda x: x[0])
        sorted_years = [p[0] for p in pairs]
        sorted_rates = [p[1] for p in pairs]

        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=sorted_years,
            y=sorted_rates,
            mode="lines+markers",
            line=dict(color="blue", width=2)
        ))
        line_fig.update_layout(
            title=f"Crime Trends in {city_name}",
            xaxis_title="Year",
            yaxis_title="Crime Rate",
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        line_img = pio.to_image(line_fig, format="png")
        line_chart_base64 = base64.b64encode(line_img).decode("utf-8")
    except Exception as e:
        print("Line Chart Error:", e)
        line_chart_base64 = ""

    # -- 2.4 Forecast & 2.6 Scatter Charts --
    forecast_chart_base64 = ""
    scatter_chart_base64  = ""
    try:
        if city_code_str.strip() and crime_code_str.strip():
            city_code  = int(city_code_str)
            crime_code = int(crime_code_str)

            # Forecast for 10 years
            forecast_years = list(range(year, year + 10))
            forecast_rates = []
            forecast_pops  = []
            forecast_cases = []

            for f_yr in forecast_years:
                year_diff = f_yr - year
                f_pop = population * (1 + 0.01 * year_diff)
                f_rate = model.predict([[f_yr, city_code, f_pop, crime_code]])[0]
                forecast_rates.append(f_rate)
                forecast_pops.append(f_pop)
                forecast_cases.append(math.ceil(f_rate * f_pop))

            # Forecast Chart
            forecast_fig = go.Figure()
            forecast_fig.add_trace(go.Scatter(
                x=forecast_years,
                y=forecast_rates,
                mode="lines+markers",
                line=dict(width=2, color="cyan")
            ))
            forecast_fig.update_layout(
                title=f"Future Crime Rate Forecast for {city_name}",
                xaxis_title="Year",
                yaxis_title="Predicted Crime Rate",
                template="plotly_white",
                paper_bgcolor="white",
                plot_bgcolor="white"
            )
            fc_img = pio.to_image(forecast_fig, format="png")
            forecast_chart_base64 = base64.b64encode(fc_img).decode("utf-8")

            # Scatter Chart
            scatter_fig = go.Figure()
            scatter_fig.add_trace(go.Scatter(
                x=forecast_pops,
                y=forecast_cases,
                mode="markers+text",
                text=[str(y) for y in forecast_years],
                textposition='top center'
            ))
            scatter_fig.update_layout(
                title="Forecast: Population vs. Estimated Cases",
                xaxis_title="Population (Lakhs)",
                yaxis_title="Estimated Cases",
                template="plotly_white",
                paper_bgcolor="white",
                plot_bgcolor="white"
            )
            sc_img = pio.to_image(scatter_fig, format="png")
            scatter_chart_base64 = base64.b64encode(sc_img).decode("utf-8")
        else:
            print("Forecast/Scatter skipped: city_code or crime_code is missing.")
    except Exception as e:
        print("Forecast/Scatter Chart Error:", e)

    # -- 2.5 Gauge Chart --
    try:
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=crime_rate,
            number={'font': {'size': 36}},
            gauge={
                'axis': {'range': [0, 20]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 1],  'color': "lightgreen"},
                    {'range': [1, 5],  'color': "green"},
                    {'range': [5, 15], 'color': "orange"},
                    {'range': [15, 20],'color': "red"}
                ]
            }
        ))
        gauge_fig.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        gauge_img = pio.to_image(gauge_fig, format="png")
        gauge_chart_base64 = base64.b64encode(gauge_img).decode("utf-8")
    except Exception as e:
        print("Gauge Chart Error:", e)
        gauge_chart_base64 = ""

    # 3) Render HTML template with all charts and details
    rendered_html = render_template(
        "report_template.html",
        city_name=city_name,
        crime_type=crime_type,
        year=year,
        crime_status=crime_status,
        crime_rate=crime_rate,
        cases=cases,
        population=population,
        bar_chart=bar_chart_base64,
        pie_chart=pie_chart_base64,
        line_chart=line_chart_base64,
        forecast_chart=forecast_chart_base64,
        scatter_chart=scatter_chart_base64,
        gauge_chart=gauge_chart_base64,
        city_code=city_code,       # may be None if missing
        crime_code=crime_code      # may be None if missing
    )

    # 4) Convert HTML to PDF
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdf = pdfkit.from_string(rendered_html, False, configuration=config)

    # 5) Return the PDF as a downloadable file
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=Crime_Report.pdf"
    return response

# For local testing:
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(pdf_report_bp)
    app.run(debug=True)
