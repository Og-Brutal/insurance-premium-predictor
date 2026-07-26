from fastapi import FastAPI
from schema.User_Input import UserInput
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from model.predict import predict_Premium,MODEL_VERSION,model
from schema.Prediction_Response import PredictionResponse

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

########################### About Response Model ########################################
# response_model in FastAPI validates and shapes only the OUTGOING data that FastAPI itself
# converts to JSON (a dict, list, or Pydantic model) — it checks types, enforces the schema,
# strips out any extra/undeclared fields (great for security), and auto-documents the response
# in /docs. However, if you manually return a Response object like JSONResponse, HTMLResponse,
# etc., FastAPI treats it as already "finished" and passes it straight through AS-IS — response_model
# validation, filtering, and doc generation are all SKIPPED, so the data can be any shape and no
# error will be raised even if it doesn't match the schema. To get validation while still using
# JSONResponse (e.g. for custom status codes/headers), first build the Pydantic model manually
# (this triggers validation) and then dump it into JSONResponse via .model_dump(), e.g.
# JSONResponse(status_code=200, content=SomeModel(...).model_dump()). If you don't need a custom
# status code or headers, skip JSONResponse entirely and just `return` the Pydantic model/dict
# directly — that's the only way to get FastAPI's full automatic validation + docs behavior.

@app.post("/predict",response_model=PredictionResponse)
def Predict_Premium(userInput : UserInput):

    user_input={
        'bmi': userInput.bmi,
        'age_group': userInput.age_group,
        'lifestyle_risk': userInput.lifestyle_risk,
        'city_tier': userInput.city_tier,
        'income_lpa': userInput.income_lpa,
        'occupation': userInput.occupation
    }
    try :
        prediction=predict_Premium(user_input)

        return {
            "Prediction":prediction,
            
        }
    except Exception as e:

        raise HTTPException(status_code=500,detail={"message":"Server Side ERROR During Prediction."})