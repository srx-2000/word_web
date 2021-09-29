from db.db_client import db_client

db_client = db_client()
# db_client.init_db()

result = db_client.delete_single_word("word", "单词", "2021-09-29 22:27:47", "123")

result1 = db_client.select_single_word("word", "单词", "2021-09-29 22:27:47", "123")

print(result)
print(result1)

result2 = db_client.select_single_word_id("1")

print(result2)

result4 = db_client.insert_word("123", "expire", "窒息")
print(result4)


result5=db_client.select_word_by_date("123")
print(result5)