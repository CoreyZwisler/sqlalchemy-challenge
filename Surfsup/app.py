# Import the dependencies.
from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
"""session = Session(engine)"""

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """Welcome to the SurfsUp API"""
    return (
        f"Welcome to my sqlalchemy-challenge API!<br/>"
        f"---------------------------------------------------------------<br/>"
        f"Available routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Tobs: /api/v1.0/tobs<br/>"
        f"Temperature Stats from start date(yyyy-mm-dd): /api/v1.0/<start><br/>"
        f"Temperature from start/end dates(yyyy-mm-dd): /api/v1.0/<start>/<end><br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the past 12 months"""
    session = Session(engine)
    
    #Query percipitation data using date
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    
    session.close()
    
    #Prepare data and jsonify
    all_prcp = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        all_prcp.append(prcp_dict)
        
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    """List of Stations"""
    session = Session(engine)
    
    # Query list of stations
    stations = session.query(Station.station).all()
    
    session.close()
    
    # Prepare data and jsonify
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return most active station tobs data for past 12 months"""
    session = Session(engine)
    
    # Query tobs data for previous year for most active station
    most_active_stat = 'USC00519281'
    
    station_stats = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_stat).\
        filter(Measurement.date >= '2016-08-23').all()
        
    session.close()
    
    # Prepare data and jsonify
    tobs_data = []
    for date, tobs in station_stats:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_data.append(tobs_dict)
        
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    # Query min, max, avg temp for dates past start
    temp_stats_start = session.query(func.min(Measurement.tobs),
                               func.max(Measurement.tobs),
                               func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    
    session.close()
    
    # Prepare data and jsonify
    start_tobs = []
    for min, max, avg in temp_stats_start:
        start_dict = {}
        start_dict['TMIN'] = min
        start_dict['TMAX'] = max
        start_dict['TAVG'] = avg
        start_tobs.append(start_dict)
        
    return jsonify(start_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date (start, end):
    session = Session(engine)
    
    # Query min, max, avg temp for dates between start and end
    temp_stats_start_end = session.query(func.min(Measurement.tobs),
                               func.max(Measurement.tobs),
                               func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    
    # Prepare data and jsonify
    start_end_tobs = []
    for min, max, avg in temp_stats_start_end:
        start_end_dict = {}
        start_end_dict['TMIN'] = min
        start_end_dict['TMAX'] = max
        start_end_dict['TAVG'] = avg
        start_end_tobs.append(start_end_dict)
        
    return jsonify(start_end_tobs)    

if __name__ == "__main__":
    app.run(debug=True)