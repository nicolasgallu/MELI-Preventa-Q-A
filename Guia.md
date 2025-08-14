#### MercadoLibre Preventa Bot Assistant.

### Summary
This product is builded to support bussines that focus on giving an specialized customer experience.
Our Product distinguished from other basically in this aspects:
- Historic Q&A analysis: Undestand the real situation that the bussines faced in the past.
- Question Cluster: Maximum performance to the customer attention.
- Recomendation System: The bot is able to recommend products from your available stock. 
- WPP Integration & Bot Improving Message: Unanswered questions are delivered to the bussines directly, and it end ups being enhanced by the bot before delivering to the Customer.
- Data Storage: We store the data of the customers, LLM Consume & Answers inside GBQ.
- Internal Daily FUP of the Ratio of Questions Answered by the bot.

#### Accuracy
- The bot has an accuracy between 85/90%, in any bussines exists questions that only can be answered by the final decition maker, we found out that in the mayoraty of cases thats is the common issue.

#### Next Steps:
- Improving the RDB, applying CRUD & ACID Methods, applying Postgress.
- Async Bot Focus.
- Self Managment from the customer, SaaS.
- Automatizing Historic Analysis and prompt set up.


## Setting UP.

There are somethings to setup before running the bot for the first time, this is the step by step Guide in order to have everything ready before testing the bot.


- GCP 
Site: https://console.cloud.google.com/
account creation -> Project -> Dataset 

#GBQ Creedentials needed for the project
.DATASET_ID
.TABLE_CREDENTIALS=
.TABLE_INVENTORY
.TABLE_QA_INIT
.TABLE_QA_LLM
.TABLE_PROMPTS
.TABLE_HUM_REPLY


- Meta Dev 
Site: https://developers.facebook.com/apps/
dev account -> phone number auth
reference videos:
https://www.youtube.com/watch?v=NUos_GR2JuQ&t=24s
https://www.youtube.com/watch?v=VDlyGcHlGiw&t=397s

#WPP Creedentials needed for the project
.WPP_TOKEN
.WPP_ID
.META_APP_SECRET


- Mercado Libre Dev
Site: https://developers.mercadolibre.com.ar/devcenter/
Crear aplicacion, preferiblemente separar una app solo para questions y suscribirse a los 
eventos relacionados.
El proceso de creacion de credenciales se ve en el siguente repo.


- LLM 

#LLM's Creedentials needed for the project
.OPENAI_API_KEY
.DEEPSEEK_API_KEY


- GMAIL

.SENDER_EMAIL
.SENDER_PASSWORD

- EXTERNAL PHONES
.PHONE_LIST

