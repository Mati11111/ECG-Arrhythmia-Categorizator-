# DATA PROCESSING
This folder contains the workflow for processing new data.

### DATA FILES <hr/>
- **getNewData**: Retrieves JSON data from the backend.
- **formatRawData**: Filters the data and segments it into chunks of 187 columns.
- **trainNewData**: Uses the new data to re-train the current model.
- **loadNewModel**: Uploads the trained model and scaler values to an external API (Cloudinary).

### WORKFLOW <hr/>

```plaintext
         NEW DATA FROM BACKEND
                   ⬇
            BACKEND/NEWDATA
                   ⬇
              TRAIN DATA?
             /          \
           YES          NO
            |            |
     FORMAT RAW DATA     DO
            |          NOTHING
     TRAIN THE MODEL
            |
     UPLOAD THE MODEL