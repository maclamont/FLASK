# Adding a comment here so that I can check it in to the repo...

from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime

import numpy as np
import pandas as pd

# For Visualization
from bokeh.plotting import figure, gridplot, output_file, show, save
from bokeh.charts import Bar


app = Flask(__name__)

app.vars={}

token = "7EX4yTkXfXEXbVn3V6iR"

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
	if request.method == 'GET':
		return render_template('./index.html')
	else:
		#REQUEST WAS A POST
		app.vars['stock'] = request.form['stock_stocks']
		app.vars['type'] = request.form['stock_type']
		app.vars['length'] = request.form['stock_length']
		print app.vars['stock']
		print app.vars['type']
		print app.vars['length']

		urlname, status = GetURL()

		if status == 200:
			df = GetData(urlname)
			PlotData(df)
			return render_template('datetime.html')

		else:
			return render_template('error.html')

def GetURL():

	print "GetURL"

	# Get the span from the website
	span = app.vars['length']
	days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	end = datetime.now()

	if span == "onemonth":
		if end.month == 1:
			start = datetime(end.year-1,end.month+11,end.day)
		else:
			if end.day > days[end.month-2]:
				start = datetime(end.year,end.month-1,days[end.month-2])
			else:
				start = datetime(end.year,end.month-1,end.day)

	if span == "sixmonths":
		if end.month < 7:
			if end.day > days[end.month+5]:
				start = datetime(end.year-1,end.month+6,days[end.month+5])
			else:
				start = datetime(end.year-1,end.month+6,end.day)
		else:
			if end.day > days[end.month-7]:
				start = datetime(end.year,end.month-6,days[end.month-7])
			else:
				start = datetime(end.year,end.month-6,end.day)

	elif span == "oneyear":
		start = datetime(end.year-1,end.month,end.day)


	# Get the stock
	Stock = app.vars['stock']

	starttime = start.strftime('%Y-%m-%d')
	endtime = end.strftime('%Y-%m-%d')

	GetStock = "WIKI/"+Stock

	urlname = 'https://www.quandl.com/api/v3/datasets/'
	urlname = urlname + GetStock + '.csv?'
	urlname = urlname + "api_key=" + token
	#urlname = urlname + GetStock + '.json'
	urlname = urlname + '&order=asc&exclude_headers=true'
	urlname = urlname + '&start_date='
	urlname = urlname + starttime
	urlname = urlname + '&end_date='
	urlname = urlname + endtime

	print urlname

	r = requests.get(urlname)

	return urlname, r.status_code
	
def GetData(urlname):

	print "In GetData()"

	df = pd.read_csv(urlname)

	print "len(df) =", len(df)
	#df = df['dataset'] # - needed if using json...

	return df


def PlotData(quandl_data):

	print "In PlotData"

	# Quandl ouput
	output_file("templates/datetime.html")

	# Now for the plot
	y_max = 1.2*(np.floor(quandl_data[app.vars['type']].max()))
	y_min = 0.8*(np.floor(quandl_data[app.vars['type']].min()))

	PlotLegend = app.vars['stock']

	dates = list(quandl_data["Date"])

	for i in range(len(dates)):
		dates[i] = datetime.strptime(dates[i],'%Y-%m-%d')

	if app.vars['type'] == "Close":
		Title = "Plot of Closing Price for " + app.vars['stock']
		Label = "Closing Price"
	elif app.vars['type'] == "High":
		Title = "Plot of High Price for " + app.vars['stock']
		Label = "High Price"
	else:
		Title = "Plot of Volume of Shares sold for " + app.vars['stock']
		Label = "Volume"

	p = figure(
   		#tools="pan,box_zoom,reset,save",
   		y_range=[y_min, y_max], title=Title, x_axis_type="datetime", 
   		x_axis_label='Date', y_axis_label=Label)

	p.line(dates, quandl_data[app.vars['type']], legend=PlotLegend)


	save(p)



if __name__ == '__main__':
  app.run(port=33507)
