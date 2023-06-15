from flask import Flask, render_template, request, flash, redirect
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates')

DB_URI = "mongodb://localhost:27017/progettoBD2"

client = MongoClient(DB_URI)

db = client.get_database()

app.secret_key = 'secret_key'
restaurant_collection = db.ristoranti
distinct_city = restaurant_collection.distinct('city')

distinct_cuisines = restaurant_collection.distinct('cuisines')
distinct_cuisines.remove(None)

@app.route('/cards')
def cards():

    print(restaurant_collection)
    restaurants = restaurant_collection.find()
    result_count = restaurant_collection.count_documents({})

    return render_template('card.html', restaurants=restaurants, result_count=result_count)


@app.route('/')
def index():
    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines)


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

    restaurants_from_query = db.ristoranti.find({"$and": query})
    result_count = db.ristoranti.count_documents({"$and": query})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)



@app.route("/query5", methods=['GET', 'POST'])
def query5():
    city = request.form.get("city")
    punteggio = request.form.get("punteggio")

    restaurants_from_query = db.ristoranti.find({"$and": [{"city": city}, {"aggregate_rating": {"$gte": float(punteggio)}}, {"has_online_delivery": True}]})
    result_count = db.ristoranti.count_documents({"$and": [{"city": city}, {"aggregate_rating": {"$gte": float(punteggio)}}, {"has_online_delivery": True}]})

    return render_template("card.html", restaurants=restaurants_from_query, result_count=result_count)


@app.route("/query6", methods=['GET', 'POST'])
def query6():
    city = request.form.get("city")
    prezzo = request.form.get("prezzo")

    restaurants_from_query = db.ristoranti.find({"$and": [{"city": city}, {"average_cost_for_two": {"$gt": 0, "$lte": float(prezzo)}}, {"has_table_booking": True}]})
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
    restaurants_from_query = db.ristoranti.find({"restaurant_name": {"$regex": nome, "$options": "i"}})
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
    city_popup = ""
    avg_voti_popup = ""
    for i in return_value:
        city_popup = i["_id"]
        avg_voti_popup = i["avg_voti"]

    flash(f"Per la città: {city_popup}, il numero medio di voti è: {avg_voti_popup}")

    return render_template('index.html', city=distinct_city, cuisines=distinct_cuisines)

if __name__ == '__main__':
    app.run(debug=True)
