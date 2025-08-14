from app.services.preventa.manage_questions_llm import ProductQuestionBot
bot =  ProductQuestionBot()

#Write any question to test the Bot
question = "tenes otros platillos??"

#Select a correct Item_ID (str) that is in the DB of the User
user_id = "47015668"
item_id = "MLA753900271"

response_text = bot.generate_llm_response(user_id, question, item_id)

print(response_text)