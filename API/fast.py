import pandas as pd
import os
from fastapi import FastAPI

from joblib import load

from code_for_API.preproc import preproc




# Load the trained model
current_directory = os.getcwd()
target_directory = os.path.join(current_directory, 'mlops/training_outputs/models')
model_path = os.path.join(target_directory, 'rff_model.joblib')
print(model_path)
loaded_model = load(model_path)


app = FastAPI()
app.state.model = loaded_model


@app.get("/predict")
def predict(csv_file):      # 1
    """
    Predict if the boat is fishing or not.
    Return dataframe with 'is_fishing' column
    """
    # Check if the uploaded file is a CSV
    if not csv_file.filename.endswith('.csv'):
        return {'error': 'Input file must be in CSV format'}


    #Prepocess data function, return dataframe
    X_processed = preproc(csv_file)


    #Run model
    y_pred = app.state.model.predict(X_processed)

    result = X_processed.copy()
    result['is_fishing'] = y_pred

    return result

@app.get("/sample")
def sample(i):      # 1
    """
    Use one of our sample track data to visualize how our model work.
    our sample range between 1 and 20
    """
    if i not in range(21):
        return {'Range error': 'input filename for sample must be between sample1 to sample20'}

    # Check if the uploaded file is a CSV
    path='mlops/data/sample_data'
    file_name = f'sample{i}'
    df = pd.read_csv(f'../{path}/{file_name}.csv')


    #Prepocess data function, return dataframe
    X_processed = preproc(df)


    #Run model
    y_pred = app.state.model.predict(X_processed)

    result = X_processed.copy()
    result['is_fishing'] = y_pred

    return result



@app.get("/")
def root():
    return {
        'greeting': 'Hello'
    }



# Run the Uvicorn server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


def preproc(df):

    df_fishing = pd.read_csv(csv_file)
    ## round the decimals so that number becomes 0 or 1
    df_fishing.loc[:, ('is_fishing')] = round(df_fishing.loc[:, ('is_fishing')])

    df_fishing.drop(columns = ["type"], inplace = True)
    #Datetime
    df_fishing['timestamp'] = pd.to_datetime(df_fishing['timestamp'], unit='s')
    df_fishing.rename(columns={"timestamp": "date"}, inplace=True)
    df_fishing['hour'] = df_fishing['date'].dt.hour
    df_fishing['month'] = df_fishing['date'].dt.month
    df_fishing['day_of_week'] = df_fishing['date'].dt.day_of_week
    #hour to angular distance
    df_fishing['hour_sin'] = np.sin(df_fishing['hour'] * (2 * np.pi / 7))
    df_fishing['hour_cos'] = np.cos(df_fishing['hour'] * (2 * np.pi / 7))
    # Dropping rows with NAN values
    df_fishing_clean = df_fishing.dropna()
    X = df_fishing_clean.drop(columns=['source','date','hour','is_fishing'])

    return X
