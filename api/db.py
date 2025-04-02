from sqlalchemy import create_engine, insert, ForeignKey, MetaData, Table, Column, Integer, Boolean, VARCHAR, TEXT,select
import sub_hours
from .food_outlets import get_food_outlets
import create_db
import json
from flask import Flask, Blueprint, Response, jsonify
import os
import re

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

# Funtion to merge dictionaries
def merge_dicts(dict1, dict2):
    """
    Recursively merge two dictionaries.
    If a key exists in both dictionaries and the values are dictionaries, merge them recursively.
    Otherwise, keep the value from dict2 (overwrite dict1).
    """
    for key, value in dict2.items():
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            merge_dicts(dict1[key], value)
        else:
            # Otherwise, overwrite dict1's value with dict2's value
            dict1[key] = value
    return dict1

# Function to Normlize outlets names
def normalize_name(name):
    # Convert to lowercase
    name = name.lower()
    
    # Remove any trailing asterisks and whitespace
    name = re.sub(r'\*+$', '', name).strip()
    
    # Standardize apostrophes and quotes
    name = name.replace("’", "'").replace('"', "'")
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Specific case handling
    if "bibliocafe" in name:
        return "bibliocafe"
    
    return name

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

    # Inputing sub food outlets into the DB
    sub_hours_dict = sub_hours.get_sub_hours()
    with engine.connect() as conn:
        for day in sub_hours_dict:
            for name in sub_hours_dict[day]:
                existing_entry = conn.execute(
                    food_outlets.select().where(
                        (food_outlets.c.name == normalize_name(name))
                    )).fetchone()
                if not existing_entry:
                    db_insert = food_outlets.insert().values(name=normalize_name(name), location=sub_hours_dict[day][name]['Building'])
                    conn.execute(db_insert)
        conn.commit()
    
    # Inputing UVic food outlets into the DB
    uvic_hours_dict = get_food_outlets()
    with engine.connect() as conn:
        for day_range in uvic_hours_dict:
            for name in uvic_hours_dict[day_range]:
                existing_entry = conn.execute(
                    food_outlets.select().where(
                        (food_outlets.c.name == normalize_name(name))
                    )).fetchone()
                if not existing_entry:
                    db_insert = food_outlets.insert().values(name=normalize_name(name), location='Unknown')
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
    uvic_hours_dict = get_food_outlets()
    food_outlets = metadata_obj.tables["food_outlets"]
    operating_hours = metadata_obj.tables["operating_hours"]

    # Inputing sub operating hours into the DB
    with engine.connect() as conn:
        for day in sub_hours_dict:
            for name in sub_hours_dict[day]:
                food_outlet_id = conn.execute(
                        select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(name))
                    ).scalar()
                
                existing_entry = conn.execute(
                    operating_hours.select().where(
                        (operating_hours.c.food_outlet_id == food_outlet_id) &
                        (operating_hours.c.day == day)
                    )).fetchone()
                
                if not existing_entry:
                    db_insert = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                    day=day,
                                                                    is_closed=sub_hours_dict[day][name]['isClosed'],
                                                                    display_hours=sub_hours_dict[day][name]['displayHours'])
                    conn.execute(db_insert)
        conn.commit()

    # Inputing uvic operating hours into the DB
    with engine.connect() as conn:
        for day_range in uvic_hours_dict:
            for name in uvic_hours_dict[day_range]:
                if day_range == "Monday - Thursday":
                    #For existing entry purposes, if an entry exists on monday it will exist Monday-Thursday
                    day = 'Monday'
                elif day_range == "Saturday - Sunday":
                    #For existing entry purposes, if an entry exists on saturday it will exist on sunday
                    day = 'Saturday - Sunday'
                else:
                    day = day_range

                food_outlet_id = conn.execute(
                        select(food_outlets.c.id).where(food_outlets.c.name == normalize_name(name))
                    ).scalar()
                
                existing_entry = conn.execute(
                    operating_hours.select().where(
                        (operating_hours.c.food_outlet_id == food_outlet_id) &
                        (operating_hours.c.day == day)
                    )).fetchone()
                
                if not existing_entry:
                    if day_range == "Monday - Thursday":
                        # Insert for monday
                        db_insert_mon = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day='Monday',
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert_mon)

                        # Insert for tuesday
                        db_insert_tue = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day='Tuesday',
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert_tue)

                        # Insert for wednesday
                        db_insert_wed = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day='Wednesday',
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert_wed)

                        # Insert for thursday
                        db_insert_thur = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day='Thursday',
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert_thur)
                    elif day_range == 'Saturday - Sunday':
                        # Insert for saturday
                        db_insert_sat = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day='Saturday',
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert_sat)

                        # Insert for sunday
                        db_insert_sun = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                        day='Sunday',
                                                                        is_closed=uvic_hours_dict[day_range][name]['isClosed'],
                                                                        display_hours=uvic_hours_dict[day_range][name]['displayHours'])
                        conn.execute(db_insert_sun)
                    else:
                        # General Insert, for friday and special days
                        db_insert = operating_hours.insert().values(food_outlet_id=food_outlet_id,
                                                                    day=day,
                                                                    is_closed=uvic_hours_dict[day][name]['isClosed'],
                                                                    display_hours=uvic_hours_dict[day][name]['displayHours'])
                        conn.execute(db_insert)
        conn.commit()

    result = engine.connect().execute(operating_hours.select())
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
    with engine.connect() as conn:
        for day in sub_hours_dict:
            for name in sub_hours_dict[day]:
                # Fetch the food_outlet_id
                food_outlet_id = conn.execute(
                    select(food_outlets.c.id).where(food_outlets.c.name == name)
                ).scalar()

                # Fetch the operating_hours_id for the given food_outlet_id and day
                operating_hours_id = conn.execute(
                    select(operating_hours.c.id).where(
                        (operating_hours.c.food_outlet_id == food_outlet_id) &
                        (operating_hours.c.day == day)
                    )
                ).scalar()

                # If operating_hours_id is not found, you might want to handle that case
                if operating_hours_id is None:
                    print(f"No operating hours found for {name} on {day}")
                    continue

                # Insert into time_slots
                if sub_hours_dict[day][name]['rawHours'] is None:
                    db_insert = time_slots.insert().values(
                        operating_hours_id=operating_hours_id,
                        start_time=None,
                        end_time=None
                    )
                else:
                    db_insert = time_slots.insert().values(
                        operating_hours_id=operating_hours_id,
                        start_time=sub_hours_dict[day][name]['rawHours'][0]['start'],
                        end_time=sub_hours_dict[day][name]['rawHours'][0]['end']
                    )

                conn.execute(db_insert)

        # Commit the transaction
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
