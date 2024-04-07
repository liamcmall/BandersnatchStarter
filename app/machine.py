import joblib
from sklearn.metrics import mean_squared_error, r2_score
import unittest
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from app.data2 import Database
from datetime import datetime

db = Database()
df = db.dataframe()

class Machine:

    @staticmethod
    def preprocess_data(df):
        """Preprocess the data and return the training and testing data and the preprocessor."""
        X = df[["clone_type", "rank", "assigned_general"]]  # Input features
        y = df["success_percentage"].astype(float)          # Target variable
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # Setup preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(handle_unknown='ignore'), [0, 1, 2])  # Transform categorical features
            ],
            remainder='passthrough'
        )

        return X_train, X_test, y_train, y_test, preprocessor

    @staticmethod
    def train_and_tune(X_train, y_train, preprocessor):
        """Train and tune the LinearRegression model and return the best model."""
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])

        params = {
            'regressor__fit_intercept': [True, False]
        }

        clf = GridSearchCV(pipeline, params, cv=2, scoring='neg_mean_squared_error')
        clf.fit(X_train, y_train)
        best_model = clf.best_estimator_
        print(f"Best parameters for Linear Regression: {clf.best_params_}")

        return best_model

    @staticmethod
    def evaluate_model(model, X_test, y_test):
        """Evaluate the model using MSE and R^2 scores and return the results."""
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        results = {'MSE': mse, 'R2': r2}
        print(f"Linear Regression - MSE: {mse}, R2: {r2}")

        return results

    def __init__(self, df):
        X_train, X_test, y_train, y_test, preprocessor = self.preprocess_data(df)
        self.model = self.train_and_tune(X_train, y_train, preprocessor)
        self.df = df
        self.model_info = self.evaluate_model(self.model, X_test, y_test)
        self.timestamp = datetime.now()

    def __call__(self, feature_basis):
        """Take in a DataFrame of feature data and return a prediction."""
        prediction = self.model.predict(feature_basis)
        return prediction

    def save(self, filepath):
        """Save the machine learning model to the specified filepath using joblib."""
        joblib.dump(self.model, filepath)

    @classmethod
    def open(cls, filepath):
        """Load a saved machine learning model from the specified filepath using joblib."""
        try:
            model = joblib.load(filepath)
            machine = cls.__new__(cls)
            machine.model = model
            machine.timestamp = datetime.now()  # Add this line to set the timestamp attribute
            return machine
        except FileNotFoundError:
            print(f"Error: No model found at {filepath}")
            return None
        


    def info(self):
        """Return a string with the name of the base model and the timestamp of when it was initialized."""
        base_model_name = type(self.model.named_steps['regressor']).__name__
        info_string = f"Base model: {base_model_name}, Initialized at: {self.timestamp}"
        return info_string


class TestMachine(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'clone_type': ['Commando', 'ARC Trooper', 'Recon', 'Standard'],
            'rank': ['Commander', 'Captain', 'Lieutenant', 'Private'],
            'assigned_general': ['General Kenobi', 'General Mace Windu', 'General Yoda', 'General Skywalker'],
            'success_percentage': [0.1, 0.2, 0.3, 0.4]
        })
        self.machine = Machine(self.df)  # Pass the DataFrame to the Machine class

    def test_preprocess_data(self):
        X_train, X_test, y_train, y_test, preprocessor = self.machine.preprocess_data(self.df)
        self.assertEqual(X_train.shape[1], 3)  # Check if the number of features is correct
        self.assertEqual(X_test.shape[1], 3)   # Check if the number of features is correct
        self.assertEqual(len(y_train), len(X_train))  # Check if the number of samples in X_train and y_train match
        self.assertEqual(len(y_test), len(X_test))    # Check if the number of samples in X_test and y_test match

    def test_save_and_open(self):
        self.machine.save('test_model.joblib')
        self.assertTrue(os.path.exists('test_model.joblib'))  # Check if the file exists
        machine = Machine.open('test_model.joblib')
        self.assertIsInstance(machine, Machine)  # Check if the returned object is an instance of Machine
        os.remove('test_model.joblib')  # Clean up

    def test_info(self):
        info_string = self.machine.info()
        self.assertIn('Base model: ', info_string)  # Check if the info string contains 'Base model: '
        self.assertIn('Initialized at: ', info_string)  # Check if the info string contains 'Initialized at: '

if __name__ == '__main__':
    unittest.main()