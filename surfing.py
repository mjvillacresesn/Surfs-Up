from flask import Flask, jsonify
import datetime as dt

import sqlalchemy
import pandas as pd
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, asc
from sqlalchemy import inspect
import pymysql
pymysql.install_as_MySQLdb()
############################################################################
# Database Setup
############################################################################
engine = create_engine("sqlite:///hawaii.sqlite")
inspector = inspect(engine)


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

###########################################################################
# Flask Setup
###########################################################################

app = Flask(__name__)

###########################################################################
# Flask Routes
###########################################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        "<h1><center>WELCOME TO SURF'S UP!</center></h1><br/>"
        "<h2><center>Please plug in the browser any of the available routes:</h2></center><br/>"
        "<h3><center>/api/v1.0/precipitation</h3></center><br/>"
        "<h3><center>/api/v1.0/stations</h3></center><br/>"
        "<h3><center>/api/v1.0/tobs</h3></center><br/>"
        "<h3><center>/api/v1.0/<start></h3></center>"
        "<center>Note: Type the start date in the form of %mm-%dd</center>"
        "<h3><center>/api/v1.0/<start>/<end></h3></center>"
        "<center>Note: API request takes two parameters: Start date / End date</center>"
        "<center>Type dates in the form of %yyyy-%mm-%dd</center>"
        "<br/>"
        "<br/>"
        "<br/>"
        "<center>MJV</center>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session.query(Measurement.date).order_by(Measurement.date.desc()).limit(5).all()
    prcp_data = session.query(Measurement).filter(Measurement.date <= '2017-08-23').\
    filter(Measurement.date >= '2016-08-23')
    precip_df = pd.read_sql_query(prcp_data.statement, session.bind)
    data_index = precip_df[["date", "prcp"]].set_index("date")
    return jsonify(data_index.to_dict())


@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Station.station)
    stations_df = pd.read_sql_query(stations_list.statement, session.bind)
    return jsonify(stations_df.to_dict())


@app.route("/api/v1.0/tobs")
def tobs():
    pstation = session.query(Measurement.tobs, Measurement.date).filter(Measurement.station == 'USC00519281').filter(
    Measurement.date <= '2017-08-23'). \
    filter(Measurement.date >= '2016-08-23')
    popstationdf = pd.read_sql_query(pstation.statement, session.bind)
    return jsonify(popstationdf.to_dict())


@app.route("/api/v1.0/<start>", methods=['GET'])
def daily_normals(start):
    """Daily Normals.
        Args:
            date (str): A date string in the format '%m-%d'
        Returns:
            TMIN, TAVE, and TMAX
    """
    sel = (func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    result = session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == start).all()

    #convert list of tuples into normal list
    all_calculations = list(np.ravel(result))

    return jsonify(all_calculations)

@app.route("/api/v1.0/<start_date>/<end_date>", methods=['GET'])
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    startend_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    #convert list of tuples into normal list
    startend_calculations = list(np.ravel(startend_results))

    return jsonify(startend_calculations)


#####################################################################
# Launch app
#####################################################################
if __name__ == "__main__":
    app.run(debug=True)