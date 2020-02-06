import unittest

import plotly_express as px

class TestPlotlyExpress(unittest.TestCase):
    
    def test_basic_scatter_plot(self):
        gapminder = px.data.gapminder()
        gapminder2007 = gapminder.query("year == 2007")
        px.scatter(gapminder2007, x="gdpPercap", y="lifeExp")
    
    def test_complex_scatter_plot(self):
        gapminder = px.data.gapminder()
        gapminder2007 = gapminder.query("year == 2007")
        px.scatter(gapminder, x="gdpPercap", y="lifeExp",size="pop", size_max=60, color="continent", hover_name="country", 
           animation_frame="year", animation_group="country", log_x=True, range_x=[100,100000], range_y=[25,90],
           labels=dict(pop="Population", gdpPercap="GDP per Capita", lifeExp="Life Expectancy"))

    def test_choropleth_plot(self):
        gapminder = px.data.gapminder()
        gapminder2007 = gapminder.query("year == 2007")
        px.choropleth(gapminder, locations="iso_alpha", color="lifeExp", hover_name="country", animation_frame="year",
            color_continuous_scale=px.colors.sequential.Plasma, projection="natural earth")
    
    def test_violin_plot(self):
        tips = px.data.tips()
        px.scatter(tips, x="total_bill", y="tip", color="smoker", trendline="ols", marginal_x="violin", marginal_y="box")
