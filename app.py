import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"List all available api routes.<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database

    most_recent_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year
    Query=session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= most_recent_year).all()

    session.close()

    # Dict with date as the key and prcp as the value
    precipitation = {date: prcp for date, prcp in Query}
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""

    Query_Station=session.query(func.count(Station.station)).all()


    session.close()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(Query_Station))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    most_recent_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year

    Query_most_active_Station_by_year=session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= most_recent_year).all()


    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(Query_most_active_Station_by_year))

    # Return the results
    return jsonify(temps=temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # start = dt.datetime.strptime(start, "%m/%d/%Y")
        # # calculate TMIN, TAVG, TMAX for dates greater than start
        # results = session.query(*sel).\
        #     filter(Measurement.date >= start).all()
        # # Unravel results into a 1D array and convert to a list
        # temps = list(np.ravel(results))
        # return jsonify(temps)

        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()
