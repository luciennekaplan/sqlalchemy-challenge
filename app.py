import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.station, Measurement.date, Measurement.prcp)
    precipitation_info = []
    for station, date, prcp in results:
        precip_dict = {}
        precip_dict["station"] = station
        precip_dict[date] = prcp
        precipitation_info.append(precip_dict)

    return jsonify(precipitation_info)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    station_names = list(np.ravel(results))
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").all()
    session.close()
    temp_obvs = list(np.ravel(results))
    return jsonify(temp_obvs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start = None, end = None):
    session = Session(engine)
    
    dates = session.query(Measurement.date).all()
    not_available = ""
    for date in dates:
        if date[0] >= start:
            not_available = "Dates not available"
        
    if not_available != "":


        if not end:
            results = session.query(func.max(Measurement.tobs), \
                func.min(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
            temp_obvs = list(np.ravel(results))
            return jsonify(temp_obvs)
        results = session.query(func.max(Measurement.tobs), \
                func.min(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start)\
                    .filter(Measurement.date <= end).all()
        temp_obvs = list(np.ravel(results))
        return jsonify(temp_obvs)
    else:
        return "Dates not available"


if __name__ == "__main__":
    app.run(debug=True)
