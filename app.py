from flask import Flask, request, render_template 
# At the top of app.py, after importing Flask, etc.
from pdf_report import pdf_report_bp
import pickle
import math
import plotly.graph_objs as go
import plotly.io as pio

# Load pre-trained model
model = pickle.load(open('Model/model.pkl', 'rb'))

app = Flask(__name__)
app.register_blueprint(pdf_report_bp)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/predict', methods=['POST'])
def predict_result():
    # Dictionaries for mapping codes to names and base populations (in Lakhs)
    city_names = {
        '0': 'Ahmedabad', '1': 'Bengaluru', '2': 'Chennai', '3': 'Coimbatore',
        '4': 'Delhi', '5': 'Ghaziabad', '6': 'Hyderabad', '7': 'Indore',
        '8': 'Jaipur', '9': 'Kanpur', '10': 'Kochi', '11': 'Kolkata',
        '12': 'Kozhikode', '13': 'Lucknow', '14': 'Mumbai', '15': 'Nagpur',
        '16': 'Patna', '17': 'Pune', '18': 'Surat'
    }
    
    crimes_names = {
        '0': 'Crime Committed by Juveniles', '1': 'Crime against SC',
        '2': 'Crime against ST', '3': 'Crime against Senior Citizen',
        '4': 'Crime against children', '5': 'Crime against women',
        '6': 'Cyber Crimes', '7': 'Economic Offences', '8': 'Kidnapping',
        '9': 'Murder'
    }
    
    population = {
        '0': 63.50, '1': 85.00, '2': 87.00, '3': 21.50, '4': 163.10, '5': 23.60,
        '6': 77.50, '7': 21.70, '8': 30.70, '9': 29.20, '10': 21.20, '11': 141.10,
        '12': 20.30, '13': 29.00, '14': 184.10, '15': 25.00, '16': 20.50, '17': 50.50,
        '18': 45.80
    }
    
    # Get form inputs
    city_code = request.form["city"]
    crime_code = request.form["crime"]
    year = request.form["year"]
    base_pop = population[city_code]
    
    # Adjust population based on the year (assume 1% increase per year since 2011)
    year_diff = int(year) - 2011
    pop = base_pop * (1 + 0.01 * year_diff)
    
    # Predict crime rate using the model
    crime_rate = model.predict([[int(year), int(city_code), pop, int(crime_code)]])[0]
    
    # Map codes to names for display
    city_name = city_names[city_code]
    crime_type = crimes_names[crime_code]
    
    # Determine crime status based on the predicted rate
    if crime_rate <= 1:
        crime_status = "Very Low Crime Area"
    elif crime_rate <= 5:
        crime_status = "Low Crime Area"
    elif crime_rate <= 15:
        crime_status = "High Crime Area"
    else:
        crime_status = "Very High Crime Area"
    
    # Calculate estimated number of cases
    cases = math.ceil(crime_rate * pop)

    # ---- Bar Chart: Crime Statistics ----
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        x=["Crime Rate", "Estimated Cases", "Population (Lakhs)"],
        y=[crime_rate, cases, pop],
        marker=dict(color=['red', 'blue', 'green'])
    ))
    bar_fig.update_layout(
        title=f"Crime Statistics in {city_name} for {year}",
        xaxis_title="Metrics",
        yaxis_title="Value",
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=40)
    )
    plotly_div = pio.to_html(bar_fig, full_html=False, config={"responsive": True})

    # ---- Pie Chart: Crime Type Distribution ----
    pie_chart = go.Figure()
    pie_chart.add_trace(go.Pie(
        labels=list(crimes_names.values()),
        values=[20, 15, 10, 8, 25, 30, 12, 18, 22, 14],
        textposition='inside',
        insidetextorientation='auto',
        textfont=dict(size=12)
    ))
    pie_chart.update_layout(
        legend=dict(
            orientation='h',
            x=0.5,
            y=-0.2,
            xanchor='center',
            yanchor='top',
            font=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=20, b=100),
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True
    )
    pie_chart_div = pio.to_html(pie_chart, full_html=False, config={"responsive": True})

    # ---- Line Chart: Crime Trends ----
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(
        x=[2011, 2013, 2015, 2017, 2019, 2021, 2023],
        y=[5, 7, 12, 15, 20, 25, crime_rate],
        mode='lines+markers',
        line=dict(color='blue', width=2)
    ))
    line_chart.update_layout(
        title=f"Crime Rate Trends in {city_name}",
        xaxis_title="Year",
        yaxis_title="Crime Rate",
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    line_chart_div = pio.to_html(line_chart, full_html=False, config={"responsive": True})

    # ---- Forecast Chart: Future Crime Rate Forecast ----
    forecast_years = list(range(int(year), int(year) + 10))
    forecast_crime_rates = []
    forecast_pops = []
    forecast_cases = []
    for f_year in forecast_years:
        f_year_diff = f_year - 2011
        f_pop = base_pop * (1 + 0.01 * f_year_diff)
        f_rate = model.predict([[f_year, int(city_code), f_pop, int(crime_code)]])[0]
        forecast_crime_rates.append(f_rate)
        forecast_pops.append(f_pop)
        forecast_cases.append(math.ceil(f_rate * f_pop))
    
    forecast_chart = go.Figure()
    forecast_chart.add_trace(go.Scatter(
        x=forecast_years,
        y=forecast_crime_rates,
        mode='lines+markers',
        line=dict(width=2, color='cyan')
    ))
    forecast_chart.update_layout(
        title=f"Future Crime Rate Forecast for {city_name}",
        xaxis_title="Year",
        yaxis_title="Predicted Crime Rate",
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    forecast_chart_div = pio.to_html(forecast_chart, full_html=False, config={"responsive": True})

    # ---- Gauge Chart: Current Crime Rate Gauge ----
    gauge_chart = go.Figure(go.Indicator(
        mode="gauge+number",
        value=crime_rate,
        number={'font': {'size': 36}},
        gauge={
            'axis': {'range': [0, 20]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 1], 'color': "lightgreen"},
                {'range': [1, 5], 'color': "green"},
                {'range': [5, 15], 'color': "orange"},
                {'range': [15, 20], 'color': "red"}
            ]
        }
    ))
    gauge_chart.update_layout(
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    gauge_chart_div = pio.to_html(gauge_chart, full_html=False, config={"responsive": True})

    # ---- Scatter Chart: Forecast Population vs. Estimated Cases ----
    scatter_chart = go.Figure()
    scatter_chart.add_trace(go.Scatter(
        x=forecast_pops,
        y=forecast_cases,
        mode='markers+text',
        text=[str(y) for y in forecast_years],
        textposition='top center'
    ))
    scatter_chart.update_layout(
        title="Forecast: Population vs. Estimated Cases",
        xaxis_title="Population (Lakhs)",
        yaxis_title="Estimated Cases",
        template="plotly_white",
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    scatter_chart_div = pio.to_html(scatter_chart, full_html=False, config={"responsive": True})

    # Render the result page with all charts and prediction details
    return render_template(
        'result.html',
        city_name=city_name,
        crime_type=crime_type,
        year=year,
        crime_status=crime_status,
        crime_rate=crime_rate,
        cases=cases,
        population=pop,
        plotly_div=plotly_div,
        pie_chart_div=pie_chart_div,
        line_chart_div=line_chart_div,
        forecast_chart_div=forecast_chart_div,
        gauge_chart_div=gauge_chart_div,
        scatter_chart_div=scatter_chart_div
    )

if __name__ == '__main__':
    app.run(debug=False)
