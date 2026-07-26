import pandas as pd
import pickle as pk

with open('model/model.pkl', 'rb') as f:
    model = pk.load(f)

MODEL_VERSION="1.0.0"

# getting all output labels
CLASS_LABELS=model.classes_.tolist()

def predict_Premium(userInput : dict) -> str:

    user_input_as_df=pd.DataFrame([userInput])
    predicted_label=model.predict(user_input_as_df)[0]

    #getting probabilities of each output label
    probabilities_of_labels=model.predict_proba(user_input_as_df)[0]

    #finding prob of predicted label
    confidence=max(probabilities_of_labels)
    #making dict of classes infront of their confidence like {class1:confidence}
    class_prob=dict(zip(CLASS_LABELS,map(lambda p:round(p,4),probabilities_of_labels)))

    return {
        "Predicted_class":predicted_label,
        "Confidence_Score":confidence,
        "Class_Probabilities":class_prob
    } 