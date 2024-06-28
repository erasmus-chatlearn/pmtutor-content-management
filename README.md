# Erasmus+ ChatLearn PMTutor Content Management Tool Set
The tool set contains scripts for managing content of PMTutor: mainly parsers and uploaders for parsing and uploading 
Excel configurations of learning topics, case studies, and self-assessment surveys.

## Prerequisites 
* Python 3.10
* Python virtualenv package
* IBM Cloudant service

## For Windows
### Create a virtual environment and install requirements
It is a good practice to work on a Python project in its own virtual environment, 
so installing and uninstalling of packages do not interfere with other Python projects in the same machine.

For the first time, navigate to the tool's root folder and create a virtual environment in a command prompt or similar tool:
```
python -m venv env
```

### Activate the virtual environment
```
env\Scripts\activate
```

After successfully activating the environment, you should see "(env)" appeared as below in the command prompt:
```
(env) C:\your\path\to\the\tool>
```

### Install requirements
``` 
pip install -r requirements.txt
```

### Before using the scripts
* Create an "output" directory in the project's root level, the parsed result will be stored there.
* Create a ".env" file in the project's root level with the following key-value pairs:
```
CLOUDANT_URL="<You can find it from the Cloudant service instance > Service credential>"
CLOUDANT_APIKEY="<You can find it from the Cloudant service instance > Service credential>"
DATABASE_NAME="<The name of an existing target database, remember to check it before uploading your content!>"
```

### Creating a cloudant database for uploading the configurations of learning topics, case studies, and self-assessment surveys
If you do not have any topic databases or want to create a new one (e.g., for testing purpose), use this script.
```
# Replace "new-database-name" with your intended name
python src\create_learning_content_database.py "new-database-name"
```
The script will return an error message and abort if the name exists already.
If the name is valid and has not been used by other databases, it will create a new database accordingly and print the new database information after creation.

### Parsing a Topic Configuration Excel file to JSON
Once setup, you can parse a valid topic configuration file into a required JSON object with the command below:
```
python src\learning_topic_parser.py <path\file_name>.xlsx
```

The parsed result will be stored in the output folder you created.

### Upload a parsed Topic Configuration JSON to Topic database
Having the parsed result ready, you can upload it to the database. It will check if there are existing documents using the
same partition key, e.g., 'uo-evm'. If there are existing documents, it will ask you if you want to replace them or abort
the uploading.

For documents which are not selfAssessmentStatement, it replaces the documents by first deleting them and creating them again.
For documents which are selfAssessmentStatement, it either creates new documents if they do not exist in the database or 
update the documents.

Nothing will change if you wish to abort the process.

```
python src\learning_topic_uploader.py output\parsed-result.json
```

### Parsing a Survey Excel file to JSON
Once setup, you can parse a valid survey file into a required JSON object with the command below:
```
python src\survey_parser.py <path\file_name>.xlsx
```

The parsed result will be stored in the output folder you created.

### Upload a parsed Survey JSON to Topic database
Having the parsed result ready, you can upload it to the database. It will check if there are existing documents using the
same partition key, e.g., 'chatlearn-preUsageSurvey'. If there is no documents using the partition key, it will ask you
if you want to create a new survey document. If there is a document with the same id, it will ask you if you want to update
the document. If there is an active survey of different id, it will ask you if you want to create a new one or update the
current active one.

Nothing will change if you wish to abort the process.

```
python src\survey_uploader.py output\parsed-survey.json
```

### Parsing a Case Study Configuration Excel file to JSON
Once setup, you can parse a valid case study configuration file into a required JSON object with the command below:
```
python src\case_study_parser.py <path\file_name>.xlsx
```

The parsed result will be stored in the output folder you created.

### Uploading a Case Study JSON to Topic database
Once successfully parsed the case study into a json consists of documents, 
you can run the command below to upload the json to the database.
```
python src\case_study_uploader.py output\parsed-case-study-docs.json
```

ATTENTION: 
- Since only minimal validation has been made to the uploader, 
make sure only use the json file parsed from the case study parser!
- Create and use a development database e.g., 'topics-sandbox' for development and testing


### Deactivate the virtual environment
It is a good practice to exit the virtual environment after you have done with the tool. Simply type in the console:
```
deactivate
```
The "(env)" will disappear.

## For Ubuntu
### Installation
Install requirements:
``` 
pip install -r requirements.txt
```

### Before using the scripts
* Create an "output" directory in the project's root level, the parsed result will be stored there.
* Create a ".env" file in the project's root level with the following key-value pairs:
```
CLOUDANT_URL="<You can find it from the Cloudant service instance > Service credential>"
CLOUDANT_APIKEY="<You can find it from the Cloudant service instance > Service credential>"
DATABASE_NAME="<The name of an existing target database, remember to check it before uploading your content!>"
```

### Creating a cloudant database for uploading the configurations of learning topics, case studies, and self-assessment surveys
If you do not have any topic databases or want to create a new one (e.g., for testing purpose), use this script.
```
# Replace "new-database-name" with your intended name
python src/create_learning_content_database.py "new-database-name"
```
The script will return an error message and abort if the name exists already.
If the name is valid and has not been used by other databases, it will create a new database accordingly and print the new database information after creation. 

### Parsing a Topic Configuration Excel file to JSON
Once setup, you can parse a valid template into a required JSON object with the command below:

If you have python3 set as default:
```
python src/learning_topic_parser.py <path/file_name>.xlsx
```
else:
```
python3 src/learning_topic_parser.py <path/file_name>.xlsx
```
The parsed result will be stored in the output folder.

### Upload a parsed Topic Configuration JSON to Topic database
Having the parsed result ready, you can upload it to the database. It will check if there are existing documents using the
same partition key, e.g., 'uo-evm'. If there are existing documents, it will ask you if you want to replace them or abort
the uploading.

For documents which are not selfAssessmentStatement, it replaces the documents by first deleting them and creating them again.
For documents which are selfAssessmentStatement, it either creates new documents if they do not exist in the database or
update the documents.

Nothing will change if you wish to abort the process.

If you have python3 set as default:
```
python src/learning_topic_uploader.py output/parsed_result.json
```
else:
```
python3 src/learning_topic_uploader.py output/parsed_result.json
```

### Parsing a Survey Excel file to JSON
Once setup, you can parse a valid survey file into a required JSON object with the command below:
```
python src/survey_parser.py <path/file_name>.xlsx
```

The parsed result will be stored in the output folder you created.

### Upload a parsed Survey JSON to Topic database
Having the parsed result ready, you can upload it to the database. It will check if there are existing documents using the
same partition key, e.g., 'chatlearn-preUsageSurvey'. If there is no documents using the partition key, it will ask you
if you want to create a new survey document. If there is a document with the same id, it will ask you if you want to update
the document. If there is an active survey of different id, it will ask you if you want to create a new one or update the
current active one.

Nothing will change if you wish to abort the process.

```
python src/survey_uploader.py output/parsed-survey.json
```

### Parsing a Case Study Configuration Excel file to JSON
Once setup, you can parse a valid case study configuration file into a required JSON object with the command below:
```
python src/case_study_parser.py <path\file_name>.xlsx
```
or 
```
python3 src/case_study_parser.py <path\file_name>.xlsx
```
The parsed result will be stored in the output folder you created.

### Uploading a Case Study JSON to Topic database
Once successfully parsed the case study into a json consists of documents,
you can run the command below to upload the json to the database.
```
python src/case_study_uploader.py output/parsed-case-study-docs.json
```
or 
```
python3 src/case_study_uploader.py output/parsed-case-study-docs.json
```
ATTENTION:
- Since only minimal validation has been made to the uploader,
  make sure only use the json file parsed from the case study parser!
- Create and use a development database e.g., 'topics-sandbox' for development and testing

## License
MIT
