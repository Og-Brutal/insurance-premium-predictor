from fastapi import FastAPI
from model.predict import predict_Premium,MODEL_VERSION,model

app=FastAPI()





# for humans telling them what this api will do 
@app.get("/")
def Home():
    return {"message":"Hey it's a Insurance Premium Prediction Model API."}

#for machine learning like when we will deploy our api on aws and use qubernaties or loadbalancer services on it then these services call this api for
#checking that does api is working and in this route we made our database connection or loads our models
@app.get("/health")
def HealthCheck():
    return {
             "status" : "OK",
             "version":MODEL_VERSION,
             "Model-Loaded":model is not None
             }


