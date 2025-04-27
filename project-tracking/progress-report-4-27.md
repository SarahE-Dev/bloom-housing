# Progress Report - Housing Risk Prediction Model  
**Date**: April 27, 2025  

## Current Status  
- **Model**: XGBoost regressor trained on mock data (features: rent, income, household size) with ~94% accuracy on the mock test set. Bryan is still working on training a new model using the AHS 2023 dataset.  
- **API**: Flask `model-service` with `/predict` endpoint accepting JSON inputs (e.g., `{"rent": 1000, "income": 30000, "household_size": 2}`). Integrated with the Nest.js backend via `/applications/submit`.  
- **Frontend**: PRs that were blocking progress have now been reviewed. Sarah will move forward with implementing the full form functionality, and Ryan will work on setting up the basic UI to display the risk score returned from the model.  
- **Documentation**: Darien added new documentation for the model service; merge conflicts are being resolved currently.  
- **Data**: Nashid is looking into sourcing additional real-world data for future model improvements.

## Feedback from Progress Presentation  
- No specific technical concerns were raised.  
- General suggestion to ensure that any tables and visualizations in the pitch deck accurately reflect current model performance and integration status.

## Next Steps  
- Bryan to finish training the new model on AHS 2023 data by next Friday.  
- Sarah to complete the full form integration with the backend.  
- Ryan to build out the basic UI for displaying the risk score prediction.  
- Nashid to continue exploring additional datasets.  
- Darien to continue updating and refining the documentation.  

