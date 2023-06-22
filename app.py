from flask import Flask, render_template, request, flash, url_for
from bson.objectid import ObjectId
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates')

DB_URI = "mongodb://localhost:27017/progettoBD2"

client = MongoClient(DB_URI)

db = client.get_database()

app.secret_key = 'secret_key'
restaurant_collection = db.ristoranti
distinct_city = None
distinct_cuisines = None
distinct_currencies = None

restaurant_collection.create_index([("restaurant_name", "text")])
def update_distinct():
    distinct_city = restaurant_collection.distinct('city')
    distinct_cuisines = restaurant_collection.distinct('cuisines')
    distinct_currencies = restaurant_collection.distinct('currency')

    if None in distinct_cuisines:
        distinct_cuisines.remove(None)

    return distinct_city, distinct_cuisines, distinct_currencies

@app.route('/cards')
def cards():
    restaurants = restaurant_collection.find()
    result_count = restaurant_collection.count_documents({})

    return render_template('card.html', restaurants=restaurants, result_count=result_count)


@app.route('/')
def index():
    distinct_city, distinct_cuisines, distinct_currencies = update_distinct()

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines, currencies=distinct_currencies)


@app.route("/query1", methods=['GET', 'POST'])
def query1():
    city = request.form.get("city")
    restaurants_from_query = db.ristoranti.find({"city": city}).sort("aggregate_rating",-1)
    result_count = db.ristoranti.count_documents({"city": city})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query2", methods=['GET', 'POST'])
def query2():
    restaurants_from_query = db.ristoranti.find({"has_table_booking": True}).sort("votes",-1)
    result_count = db.ristoranti.count_documents({"has_table_booking": True})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query3", methods=['GET', 'POST'])
def query3():
    prezzo = request.form.get("prezzo")

    restaurants_from_query = db.ristoranti.find({"$and":[{"average_cost_for_two": {"$gt": 0}}, {"average_cost_for_two": {"$lt": float(prezzo)}}, {"currency": "Dollar($)"}]})
    result_count = db.ristoranti.count_documents({"$and":[{"average_cost_for_two": {"$gt": 0}}, {"average_cost_for_two": {"$lt": float(prezzo)}}, {"currency": "Dollar($)"}]})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query4", methods=['GET', 'POST'])
def query4():
    cuisine = request.form.getlist("cuisine[]")
    query = []

    for i in range(len(cuisine)):
        query.append({"cuisines": cuisine[i]})

    restaurants_from_query = db.ristoranti.find({"$and": query}).sort([("aggregate_rating", -1), ("votes",-1)])
    result_count = db.ristoranti.count_documents({"$and": query})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query5", methods=['GET', 'POST'])
def query5():
    city = request.form.get("city")
    punteggio = request.form.get("punteggio")

    restaurants_from_query = db.ristoranti.find({"$and": [{"city": city}, {"aggregate_rating": {"$gte": float(punteggio)}}, {"has_online_delivery": True}, {"price_range": {"$ne": 1}}]}).sort("votes",-1)
    result_count = db.ristoranti.count_documents({"$and": [{"city": city}, {"aggregate_rating": {"$gte": float(punteggio)}}, {"has_online_delivery": True}, {"price_range": {"$ne": 1}}]})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query6", methods=['GET', 'POST'])
def query6():
    city = request.form.get("city")
    prezzo = request.form.get("prezzo")

    restaurants_from_query = db.ristoranti.find({"$and": [{"city": city}, {"average_cost_for_two": {"$gt": 0, "$lte": float(prezzo)}}, {"has_table_booking": True}]}).sort("restaurant_name",1)
    result_count = db.ristoranti.count_documents({"$and": [{"city": city}, {"average_cost_for_two": {"$gt": 0, "$lte": float(prezzo)}}, {"has_table_booking": True}]})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query7", methods=['GET', 'POST'])
def query7():
    punteggio = request.form.get("punteggio")
    voti = request.form.get("voti")

    restaurants_from_query = db.ristoranti.find({"$and": [{"votes": {"$gte": float(voti)}}, {"aggregate_rating": {"$gte": float(punteggio)}}]}).sort("aggregate_rating",-1)
    result_count = db.ristoranti.count_documents({"$and": [{"votes": {"$gte": float(voti)}}, {"aggregate_rating": {"$gte": float(punteggio)}}]})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query8", methods=['GET', 'POST'])
def query8():
    nome = request.form.get("nome")
    restaurants_from_query = db.ristoranti.find({"restaurant_name": {"$regex": nome, "$options": "i"}}).sort("aggregate_rating",-1)
    result_count = db.ristoranti.count_documents({"restaurant_name": {"$regex": nome, "$options": "i"}})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query9", methods=['GET', 'POST'])
def query9():
    cuisine = request.form.getlist("cuisine[]")
    punteggio = request.form.get("punteggio")
    range_prezzo = request.form.get("range_prezzo")
    query = []

    for i in range(len(cuisine)):
        query.append({"cuisines": cuisine[i]})

    query.append({"aggregate_rating": {"$gte": float(punteggio)}})
    query.append({"price_range": float(range_prezzo)})
    query.append({"has_table_booking": True})
    query.append({"has_online_delivery": True})
    query.append({"votes": {"$gte": 100}})

    restaurants_from_query = db.ristoranti.find({"$and": query})
    result_count = db.ristoranti.count_documents({"$and": query})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query10", methods=['GET', 'POST'])
def query10():
    city = request.form.get("city")
    pipeline = [{"$match": {"city": city}}, {"$group": {"_id": "$city", "avg_voti": {"$avg": "$votes"}}}]

    return_value = db.ristoranti.aggregate(pipeline)
    tmp_value=return_value.next()
    city_popup = tmp_value["_id"]
    avg_voti_popup = tmp_value["avg_voti"]

    flash(f"Per la città: {city_popup}, il numero medio di voti è: {avg_voti_popup}")

    distinct_city, distinct_cuisines, distinct_currencies = update_distinct()

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines, currencies=distinct_currencies)

@app.route("/query11", methods=['GET', 'POST'])
def query11():
    currency = request.form.get("currency")
    pipeline = [{"$match": {"currency": currency}}, {"$group": {"_id": "$currency", "sum_voti": {"$sum": "$votes"}}}]

    return_value = db.ristoranti.aggregate(pipeline)
    tmp_value=return_value.next()
    currency_popup = tmp_value["_id"]
    sum_voti_popup = tmp_value["sum_voti"]

    flash(f"Per i ristoranti che utilizzano la valuta: {currency_popup}, la somma dei voti è: {sum_voti_popup}")

    distinct_city, distinct_cuisines, distinct_currencies = update_distinct()

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines, currencies=distinct_currencies)

@app.route("/query12", methods=['GET', 'POST'])
def query12():
    nome = request.form.get("nome")
    restaurants_from_query = db.ristoranti.find({"$text": {"$search": nome}}).sort("aggregate_rating", -1)
    result_count = db.ristoranti.count_documents({"$text": {"$search": nome}})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)

@app.route("/query13", methods=['GET', 'POST'])
def query13():
    range = request.form.get("range_prezzo")
    restaurants_from_query = db.ristoranti.find({"$and": [{"price_range": int(range)}, {"$or": [{"has_online_delivery": True}, {"has_table_booking": True}]}]}).sort("votes",-1)
    result_count = db.ristoranti.count_documents({"$and": [{"price_range": int(range)}, {"$or": [{"has_online_delivery": True}, {"has_table_booking": True}]}]})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/modify", methods=['GET', 'POST'])
def modify():
    restaurant_id = request.form.get("restaurant_data")
    restaurant = db.ristoranti.find({"_id": ObjectId(restaurant_id)}).next()

    if restaurant["cuisines"] is not None:
        cuisines = ", ".join(restaurant["cuisines"])
    else:
        cuisines = ""

    return render_template("modify.html", restaurant=restaurant, cuisines=cuisines)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    restaurant_id = request.form.get("restaurant_data")

    print(restaurant_id)
    db.ristoranti.delete_one({"_id": ObjectId(restaurant_id)})

    flash("Ristorante cancellato con successo!")

    distinct_city, distinct_cuisines, distinct_currencies = update_distinct()

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines, currencies=distinct_currencies)


@app.route("/insert")
def insert():
    return render_template("insert.html")


@app.route("/add_restaurant", methods=['GET', 'POST'])
def add_restaurant():
    max_id_restaurant = db.ristoranti.find().sort("restaurant_id", -1).limit(1)
    max_id_obj = max_id_restaurant.next()
    max_id = int(max_id_obj["restaurant_id"])
    max_id += 1

    nome = request.form.get("nome")
    city = request.form.get("city").title()
    address = request.form.get("address").title()
    prezzo = request.form.get("prezzo")
    if prezzo == "":
        prezzo = None
    else:
        prezzo = int(prezzo)
    cuisines = request.form.get("cuisines").title()
    if cuisines == "":
        cuisines = None
    else:
        cuisines = cuisines.split(",")
        cuisines = list(map(str.strip, cuisines))
    currency = request.form.get("currency").title()
    if currency == "":
        currency = None
    table = request.form.get("table")
    if(table == "Sì"):
        table = True
    else:
        table = False
    delivery = request.form.get("delivery")
    if (delivery == "Sì"):
        delivery = True
    else:
        delivery = False
    voti = int(request.form.get("voti"))
    punteggio = float(request.form.get("punteggio"))
    range_prezzo = int(request.form.get("range_prezzo"))

    new_restaurant = {"restaurant_id": max_id, "restaurant_name": nome, "city": city, "address": address,
                      "locality": address, "cuisines": cuisines, "average_cost_for_two": prezzo,
                      "currency": currency, "has_table_booking": table, "has_online_delivery": delivery,
                      "price_range": range_prezzo, "aggregate_rating": punteggio, "votes": voti}

    db.ristoranti.insert_one(new_restaurant)

    flash("Ristorante inserito con successo!")

    distinct_city, distinct_cuisines, distinct_currencies = update_distinct()

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines, currencies=distinct_currencies)


@app.route("/modify_restaurant", methods=['GET', 'POST'])
def modify_restaurant():
    _id = request.form.get("_id")
    nome = request.form.get("nome")
    city = request.form.get("city").title()
    address = request.form.get("address").title()
    prezzo = request.form.get("prezzo")
    if prezzo == "":
        prezzo = None
    else:
        prezzo = int(prezzo)
    cuisines = request.form.get("cuisines").title()
    if cuisines == "":
        cuisines = None
    else:
        cuisines = cuisines.split(",")
        cuisines = list(map(str.strip, cuisines))
    currency = request.form.get("currency").title()
    if currency == "":
        currency = None
    table = request.form.get("table")
    if (table == "Sì"):
        table = True
    else:
        table = False
    delivery = request.form.get("delivery")
    if (delivery == "Sì"):
        delivery = True
    else:
        delivery = False
    voti = int(request.form.get("voti"))
    punteggio = float(request.form.get("punteggio"))
    range_prezzo = int(request.form.get("range_prezzo"))

    query = {"_id": ObjectId(_id)}
    update_values={"$set": {"restaurant_name": nome, "city": city, "address": address,
                      "locality": address, "cuisines": cuisines, "average_cost_for_two": prezzo, "currency": currency,
                      "has_table_booking": table, "has_online_delivery": delivery, "price_range": range_prezzo, "aggregate_rating": punteggio, "votes": voti}}

    db.ristoranti.update_one(query, update_values)

    flash("Ristorante modificato con successo!")

    distinct_city, distinct_cuisines, distinct_currencies = update_distinct()

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines, currencies=distinct_currencies)


if __name__ == '__main__':
    app.run(debug=True)
