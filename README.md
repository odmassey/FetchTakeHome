# FetchTakeHome
<!-- GETTING STARTED -->
### Running
Requires Python 3.9\
May need to install psycopg2\
May need to change AWS SQS queue hostname/port depending on source\
May need to change postgres database info depending on source\
Run python file

### Questions
How would you deploy this application in production?
>Store the file where it can access both the SQS queue and database then run the file on a cron job or another way it can periodically check the queue for new messages.

What other components would you want to add to make this production ready?
>Next steps would be a logging feature, error handling, and better config for program fields.

How can this application scale with a growing dataset?
>Put a limit on the amount of queue messages the program scans to limit the data the program reads at once.  Send the data to postgres as a group.

How can PII be recovered later on?
>Must have a seperate database for PII with its corresponding masked value.  Masked PII data can then be either looked up later or related.

What are the assumptions you made?
>Postgres tabel will not change schema.  
