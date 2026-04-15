from pymongo import MongoClient
import sys

# Neenga copy panna link-ah inga paste pannunga
# IMPORTANT: <password> nu irukkura idathula unga password-ah type pannunga
uri = "mongodb+srv://Subha:bank123@bankingproject.iqlrqxd.mongodb.net/?appName=BankingProject"
try:
    # Localhost-ku badhila ippo uri-ah pass panrom
    client = MongoClient(uri)
    
    # Database name same-aa vachukalaam
    db = client["ai_banking"]

    users = db["users"]
    complaints = db["complaints"]
    
    # Connection check panna oru chinna test
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas Cloud!")

except Exception as e:
    print(f"❌ Connection Error: {e}")