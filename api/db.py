from sqlalchemy import create_engine, insert, ForeignKey, MetaData, Table, Column, Integer, Boolean, VARCHAR, TEXT
import sub_hours
import create_db
import json
from flask import Flask, Blueprint, Response, jsonify
import os

db_blueprint = Blueprint('db', __name__)
app = Flask(__name__)

# Main DB Route
@db_blueprint.route('/db')
def db_main():
    return jsonify("Welcome to the VikeEats Database :)")

# Route that creates DB
@db_blueprint.route('/db/create')
def db_create():
    create_db.create_database()
    return jsonify("Database Created :)")

'''
Updates FoodOutlets in DB
Composed of 2 functions
-db_ufor: Update food outlets route
-db_ufo: Update food outlets
First function calls required update functions
and returns json to be displayed

Second Function actually updates the db
did it this way, so it can be called by
other update functions that depend on this
table
'''
@db_blueprint.route('/db/update/food_outlets')
def db_ufor():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        return jsonify(db_ufo())
def db_ufo():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    food_outlets = metadata_obj.tables["food_outlets"]
    operating_hours = metadata_obj.tables["operating_hours"]
    time_slots = metadata_obj.tables["time_slots"]

    # Inputing sub food outlets into the DB
    sub_hours_dict = sub_hours.get_sub_hours()
    for name in sub_hours_dict['Monday']:
        db_insert = food_outlets.insert().values(name=name, location=sub_hours_dict['Monday'][name]['Building'])
        with engine.connect() as conn:
            conn.execute(db_insert)
            conn.commit()

    # Inputing sub operating hours into the DB
    for day in sub_hours_dict:
        for name in sub_hours_dict[day]:
            with engine.connect() as conn:
                food_outlet_id = conn.execute(food_outlets.select().where(food_outlets.c.name == name)).scalar()
                db_insert = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                             day=day,
                                                             is_closed=sub_hours_dict[day][name]['isClosed'],
                                                             display_hours=sub_hours_dict[day][name]['displayHours'])
                conn.execute(db_insert)
                conn.commit()

    # Inputing sub timeslots into the DB
    for day in sub_hours_dict:
        for name in sub_hours_dict[day]:
            with engine.connect() as conn:
                operating_hours_id = conn.execute(operating_hours.select().where(operating_hours.c.food_outlet_id == food_outlets.c.id)).scalar()
                if sub_hours_dict[day][name]['rawHours'][0]['start'] is None:
                    db_insert = time_slots.insert().values(operating_hours_id=operating_hours_id,
                                                           start_time='None',
                                                           end_time='None')
                else:
                    db_insert = time_slots.insert().values(operating_hours_id=operating_hours_id,
                                                           start_time=sub_hours_dict[day][name]['rawHours'][0]['start'],
                                                           end_time=sub_hours_dict[day][name]['rawHours'][0]['end'])
                conn.execute(db_insert)
                conn.commit()

    result = engine.connect().execute(food_outlets.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return row_dict

'''
Updates Opperating Hours in DB
Composed of 2 functions
-db_uohr: Update Opperating Hours route
-db_uoh: Update Opperating Hours
First function calls required update functions
and returns json to be displayed

Second Function actually updates the db
did it this way, so it can be called by
other update functions that depend on this
table
'''
@db_blueprint.route('/db/update/operating_hours')
def db_uohr():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        db_ufo()
        return jsonify(db_uoh())
def db_uoh():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    sub_hours_dict = sub_hours.get_sub_hours()
    food_outlets = metadata_obj.tables["food_outlets"]
    operating_hours = metadata_obj.tables["operating_hours"]

    # Inputing sub operating hours into the DB
    for day in sub_hours_dict:
        for name in sub_hours_dict[day]:
            with engine.connect() as conn:
                food_outlet_id = conn.execute(food_outlets.select().where(food_outlets.c.name == name)).scalar()
                db_insert = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                             day=day,
                                                             is_closed=sub_hours_dict[day][name]['isClosed'],
                                                             display_hours=sub_hours_dict[day][name]['displayHours'])
                conn.execute(db_insert)
                conn.commit()

    result = engine.connect().execute(food_outlets.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return row_dict

'''
Updates Time Slots in DB
Composed of 2 functions
-db_utsr: Update Time Slots route
-db_uts: Update Time Slots
First function calls required update functions
and returns json to be displayed

Second Function actually updates the db
did it this way, so it can be called by
other update functions that depend on this
table
'''
@db_blueprint.route('/db/update/time_slots')
def db_utsr():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        db_ufo()
        db_uoh()
        return jsonify(db_uts())
def db_uts():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    sub_hours_dict = sub_hours.get_sub_hours()
    food_outlets = metadata_obj.tables["food_outlets"]
    operating_hours = metadata_obj.tables["operating_hours"]
    time_slots = metadata_obj.tables["time_slots"]

    # Inputing sub timeslots into the DB
    for day in sub_hours_dict:
        for name in sub_hours_dict[day]:
            with engine.connect() as conn:
                operating_hours_id = conn.execute(operating_hours.select().where(operating_hours.c.food_outlet_id == food_outlets.c.id)).scalar()
                if sub_hours_dict[day][name]['rawHours'][0]['start'] is None:
                    db_insert = time_slots.insert().values(operating_hours_id=operating_hours_id,
                                                           start_time='None',
                                                           end_time='None')
                else:
                    db_insert = time_slots.insert().values(operating_hours_id=operating_hours_id,
                                                           start_time=sub_hours_dict[day][name]['rawHours'][0]['start'],
                                                           end_time=sub_hours_dict[day][name]['rawHours'][0]['end'])
                conn.execute(db_insert)
                conn.commit()

    result = engine.connect().execute(time_slots.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return row_dict

# Displays FoodOutlets Currently saved in DB
@db_blueprint.route('/db/food_outlets')
def db_fo():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    food_outlets = metadata_obj.tables["food_outlets"]

    result = engine.connect().execute(food_outlets.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return jsonify(row_dict)

# Displays operating hours Currently saved in DB
@db_blueprint.route('/db/operating_hours')
def db_oh():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    operating_hours = metadata_obj.tables["operating_hours"]

    result = engine.connect().execute(operating_hours.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return jsonify(row_dict)

# Displays time slots Currently saved in DB
@db_blueprint.route('/db/time_slots')
def db_ts():
    if not os.path.exists('vikeeats.db'):
        return jsonify("Database not found, create it at /api/db/create")
    else:
        engine = create_engine("sqlite:///vikeeats.db", echo=True)
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    time_slots = metadata_obj.tables["time_slots"]

    result = engine.connect().execute(time_slots.select())
    row_dict = {idx + 1: str(row) for idx, row in enumerate(result)}
    return jsonify(row_dict)
