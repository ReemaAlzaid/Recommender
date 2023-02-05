import pandas as pd
import numpy as np
import s3fs
import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, jsonify, request
import json


#declared an empty variable for reassignment
response = ''

#creating the instance of our flask application
app = Flask(__name__)

#route to entertain our post and get request from flutter app
@app.route('/name', methods = ['POST'])
def nameRoute():

    #fetching the global response variable to manipulate inside the function
    global response

    #checking the request type we get from the app 
    if(request.method == 'POST'):
        ProductsHistory = request.data #getting the response data
        
        ProductsHistory_data = json.loads(ProductsHistory.decode('utf-8')) #converting it from json to key value pair


        DataFrameHistory = pd.DataFrame.from_dict(ProductsHistory_data['PurchaseHistory'], orient='index')
        DataFrameProducts = pd.DataFrame.from_dict(ProductsHistory_data['Products'], orient='index')

        DataFrameHistory.reset_index(level=0, inplace=True)
        DataFrameProducts.reset_index(level=0, inplace=True)

        DataFrameHistory.rename(columns = {'Price':'Count'}, inplace = True)
        DataFrameProducts.rename(columns = {'index':'Barcode'}, inplace = True)
        global Products
        Products = DataFrameProducts[['Barcode','SubCategory']].dropna()
        Products=Products.reset_index(drop=True)

        HistoryCart = DataFrameHistory.dropna()

        popular_products = pd.DataFrame(HistoryCart.groupby('SubCategory')['Count'].count())
        popular_products.reset_index(level=0, inplace=True)

        tfidf = TfidfVectorizer(stop_words='english')

        overview_matrix = tfidf.fit_transform(Products['SubCategory'])

        print(popular_products)
        global similarity_matrix
        similarity_matrix = cosine_similarity(overview_matrix,overview_matrix) #Finds all category that matches each other 

        global MostPurchased

        MostPurchased = popular_products.loc[popular_products['Count']. idxmax()]
        print(MostPurchased)
        global mapping
        mapping = pd.Series(Products.index,index = Products['SubCategory'])
        #return "History received"
        return MostPurchased['SubCategory']


if __name__ == "__main__":
    app.run(host='0.0.0.0')

