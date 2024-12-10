from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

from modules.function import generate_unique_id

app = Flask(__name__)

CORS(app, resources={r"/grosify/*": {"origins": "http://localhost:3000"}}, 
    headers=["Content-Type"])

MONGODB_HOST="mongodb://localhost:27017/"
DB_NAME="Learnings"

client = MongoClient(MONGODB_HOST)
db = client[DB_NAME]

data_store = {}

# CREATE DATA
# --- create master data
@app.route('/grosify/addMaster', methods=['POST'])
def create_grocery_master():

    if not request.json['masterName']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Master Name Not Found'}), 400

    data = request.json

    if data:
        try:
            master_data = { 
                'masterUniqueId' : generate_unique_id(),
                'masterName' : request.json['masterName'],
                'masterCreatedAt' : datetime.now().strftime('%d-%b-%Y %I:%M %p')
            }

            db.Groceries_master_db.insert_one(master_data)

            return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Inserted Successfully'}), 200
        except Exception as e:
            return jsonify({'success' : False, 'status' : 'Not Success','description' : str(e)}), 400
    else:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Unable to Update the data'}), 400

# --- create grocery data
@app.route('/grosify/addItems', methods=['POST'])
def create_item():

    if not request.json['itemName']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item Name Not Found'}), 400
    
    if not request.json['itemBrand']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item Brand Not Found'}), 400
    
    if not request.json['itemCurrentPrice']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item Current Price Not Found'}), 400
    
    if not request.json['itemQuantity']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item Quantity Not Found'}), 400

    master_data = db.Groceries_master_db.find_one({'masterName' : request.json['itemBrand']})
    groceries_Data = db.Groceries_details_db.find_one({'itemName' : request.json['itemName'],'itemBrand' : request.json['itemBrand'],'itemCurrentPrice' : request.json['itemCurrentPrice'],'itemQuantity' : request.json['itemQuantity']})

    if not master_data:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Brand Name Not in Master Please Update'}), 400
    
    if groceries_Data:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Data Already Found'}), 400
    
    data = request.json

    if data:
        try:
            grocery_data = { 
                'itemUniqueId' : generate_unique_id(),
                'itemName' : request.json['itemName'],
                'itemBrandID' : master_data['masterUniqueId'],
                'itemBrand' : request.json['itemBrand'],
                'itemCurrentPrice' : request.json['itemCurrentPrice'],
                'itemQuantity' : request.json['itemQuantity'],
                'itemCreatedAt' : datetime.now().strftime('%d-%b-%Y %I:%M %p'),
                'itemUpdatedAt' : ''
            }

            db.Groceries_details_db.insert_one(grocery_data)

            return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Inserted Successfully'}), 200
        except Exception as e:
            return jsonify({'success' : False, 'status' : 'Not Success','description' : str(e)}), 400
    else:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Unable to Update the data'}), 400


# GET DATA
@app.route('/grosify/getAllItems', methods=['POST'])
def get_items():

    if not request.json['option']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Option is not Found'}), 400

    options = request.json['option']

    query = {}

    # All data
    if options == 'All':
        query = {}
    
    # Brand data
    elif options == 'Brand':

        if not request.json['itemBrand']:
            return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Brand is not Found'}), 400

        brand_list = request.json['itemBrand']
        query = {'itemBrand': {'$in': [brand.strip() for brand in brand_list.split(',')]}}
    
    # Individual data
    elif options == 'Item':

        if not request.json['itemUniqueId']:
            return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item UniqueId is not Found'}), 400

        item = request.json['itemUniqueId']
        query = {'itemUniqueId': item}


    grocery_data = list(db.Groceries_details_db.find(query, {"_id": 0}))

    if grocery_data and grocery_data != []:
        return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Retrive Successfully', 'data' : grocery_data }), 200
    else:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'No Items Found'}), 400


@app.route('/grosify/getAllBrands', methods=['POST'])
def get_brands():

    if not request.json['option']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Option is not Found'}), 400

    options = request.json['option']

    query = {}

    # All data
    if options == 'All':
        query = {}

    brand_data = list(db.Groceries_master_db.find(query, {"_id": 0}))
    if brand_data and brand_data != []:
        return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Retrive Successfully', 'data' : brand_data }), 200
    else:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'No Items Found'}), 400
    

@app.route('/grosify/getAllDeletedItems', methods=['POST'])
def get_deleted_Items():

    if not request.json['option']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Option is not Found'}), 400

    options = request.json['option']

    query = {}

    # All data
    if options == 'All':
        query = {}

    deleted_item_data = list(db.Groceries_deleted_details_db.find(query, {"_id": 0}))
    if deleted_item_data and deleted_item_data != []:
        return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Retrive Successfully', 'data' : deleted_item_data }), 200
    else:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'No Items Found'}), 400

# UPDATE DATA
@app.route('/grosify/updateItems', methods=['PUT'])
def update_item():
    try: 
        if not request.json['itemUniqueId']:
            return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item UniqueId is not Found'}), 400

        grocery_data = db.Groceries_details_db.find_one({'itemUniqueId':  request.json['itemUniqueId']})
        
        updateItems = {}

        if grocery_data:

            price = request.json.get('itemCurrentPrice','')
            quantity = request.json.get('itemQuantity','')

            if price != '' and quantity != '':
                updateItems = { 'itemQuantity' : quantity ,'itemCurrentPrice' : price }

            elif quantity != '': 
                updateItems = { 'itemQuantity' : quantity }

            elif price != '':
                updateItems = { 'itemCurrentPrice' : price }

            # check if the updated data already presents!
            isAlreadyPresents = all(grocery_data.get(key) == value for key, value in updateItems.items())

            if isAlreadyPresents:
                return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Same data already presents'}), 200

            updateItems['itemUpdatedAt'] = datetime.now().strftime('%d-%b-%Y %I:%M %p')

            db.Groceries_details_db.update_one(
                {'itemUniqueId' : request.json['itemUniqueId']},
                {
                    "$set": updateItems
                }
            )
            return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Updated Successfully'}), 200

        else:
            return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item Not Found'}), 200
    except Exception as e :
        raise e


# DELETE DATA
@app.route('/grosify/deleteItem', methods=['DELETE'])
def delete_item():
    print("RESPONSE --",request.json)
    if not request.json['itemUniqueId']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Item UniqueId is not Found'}), 400
    
    if not request.json['reason']:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Reason is not Found'}), 400


    grocery_data = db.Groceries_details_db.find_one({'itemUniqueId':  request.json['itemUniqueId']}, {"_id": 0})

    if grocery_data:

        db.Groceries_details_db.delete_one({'itemUniqueId':  request.json['itemUniqueId']})

        grocery_data['reason'] = request.json['reason']
        grocery_data['deletedAt'] = datetime.now().strftime('%d-%b-%Y %I:%M %p')

        db.Groceries_deleted_details_db.insert_one(grocery_data)

        return jsonify({'success' : True, 'status' : 'Success','description' : 'Data Successfully Deleted'}), 400
    
    else:
        return jsonify({'success' : False, 'status' : 'Not Success','description' : 'Unable to delete'}), 400


if __name__ == '__main__':
    app.run(debug=True)

