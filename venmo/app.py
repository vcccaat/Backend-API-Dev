import json
from flask import Flask, request
import datetime
import db

DB = db.DatabaseDriver()

app = Flask(__name__)
DB = db.DatabaseDriver()

def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

@app.route("/")
@app.route("/api/users/")
def get_users():
    return json.dumps({"users":DB.get_all_users()}), 200

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance")
    balance = balance if balance else 0
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Could not create user.", 400)
    user["transactions"] = []
    return success_response(user, 201)

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user not found!")
    transactions = DB.get_user_transactions(user_id)
    user["transactions"] = transactions
    return success_response(user)

@app.route("/api/trans/")
def get_trans():
    return json.dumps({"users":DB.get_all_trans()}), 200

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user by id
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("user not found!")
    DB.delete_user_by_id(user_id)
    transactions = DB.get_user_transactions(user_id)
    user["transactions"] = transactions
    return success_response(user, 200)

@app.route("/api/transactions/", methods=["POST"])
def send_money():
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")

    sender = DB.get_user_by_id(sender_id)
    if sender is None:
        return failure_response("sender not found!",400)
    receiver = DB.get_user_by_id(receiver_id)
    if receiver is None:
        return failure_response("receiver not found!",400)
    if amount is None:
        return failure_response("empty amount",400)
    if accepted == True:
        if sender["balance"] < amount:
            return failure_response("insufficient balance!",403)

        DB.update_balance(sender_id,sender["balance"]-amount)
        DB.update_balance(receiver_id,receiver["balance"]+amount)

    now = datetime.datetime.now()
    transaction_id = DB.insert_transaction(now, sender_id, receiver_id, amount, message, accepted)
    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return failure_response("Could not create transaction.", 400)
    return success_response(transaction, 201)

@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def update_transaction(transaction_id):
    body = json.loads(request.data)
    accepted = body.get("accepted")
    now = datetime.datetime.now()
    
    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return failure_response("Could not find transaction.", 400)
    
    if transaction["accepted"] != None:
        return failure_response("cannot change transaction's accepted field",403)

    if accepted == True:
        sender_id = transaction["sender_id"]
        receiver_id = transaction["receiver_id"]
        amount = transaction['amount']
        sender = DB.get_user_by_id(sender_id)
        receiver = DB.get_user_by_id(receiver_id)
        if sender["balance"] < amount:
            return failure_response("insufficient balance!",403)
        else:
            DB.update_transaction(transaction_id, now, accepted)

        DB.update_balance(sender_id,sender["balance"]-amount)
        DB.update_balance(receiver_id,receiver["balance"]+amount)
    else:
        DB.update_transaction(transaction_id, now, accepted)  #update to accepted==False
        
    updated_transaction = DB.get_transaction_by_id(transaction_id)
    # updated_transaction["accepted"] = True if updated_transaction["accepted"] else False
    return success_response(updated_transaction, 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
