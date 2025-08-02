import csv
import time
import gspread
import sys

# TODO: Add keywords for any recurring transacs with 'other' category
# TODO: Check month inputs for correctness. 
# TODO: GUI
# TODO: Connect to GCU so possible to login from program and download csv files. 

CATEGORY_RULES = {
    "bonus": ["cashout"],
    "amazon income": ["direct dep"],
    "transportation": ["uber", "lyft", "shell", "chevron", "gas", "exxon", "eleven", "fuel", "emiss", "parking", "dmv", "roys"],
    "food": ["mcdonald", "chipotle", "burger", "taco", "domino", "panda", "cafe", "pizza", "restaurant", "wingers", 
             "arctic", "chick", "papa", "leather", "iceberg", "subway", "garden", "in-n-", "robin"],
    "groceries": ["mart", "target", "costco", "smith", "grocery", "macey", "kroger", "supercenter"],
    "subscriptions": ["netflix", "spotify", "hulu", "disney", "apple", "youtube", "amazon prime", "audible"],
    "entertainment": ["movie", "cinema", "games", "steam", "amc", "fandango", "epc", "fortnite", "fun", "zoo"],
    "utilities": ["verizon", "t-mobile", "at&t", "comcast", "xfinity", "internet", "energy", "power"],
    "shopping": ["amazon", "ebay", "shein", "etsy", "nike", "adidas", "best buy"],
    "health": ["pharmacy", "walgreens", "cvs", "doctor", "hospital", "clinic", "dentist", "evansmiles"],
    "transfer": ["transfer"],
    "insurance": ["prog", "insurance"],
    "venmo": ["venmo"],
    "self care": ["nails", "spa", "hair", "cut", "Kelly"],
    "other": []
}

def get_input(prompt):
    user_input = input(prompt).strip()
    if user_input.lower() == "stop":
        print("Program stopped by user.")
        sys.exit(0)
    return user_input

# Categorizes transactions and returns the category 
def categorize(name: str) -> str:
    name = name.lower().strip()

    # Categorize venmo transactions by the person they are sent to... Regex for extracting the name
    if "venmo" in name and '*' in name:
        after_star = name.split('*', 1)[1].strip()
        # Remove trailing terms like 'Visa Direct', etc.
        for stopword in ['visa direct', 'nyus', 'payment', 'credit']:
            after_star = after_star.lower().replace(stopword, '')
        cleaned = ' '.join(after_star.title().split())
        return cleaned if cleaned else "other"  # 

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in name:  # Key word for category has been found              
                return category
            
    return "other"

# Get transaction info such as date, name, amount, and category.
# Returns a list of transactions with their info.
def gcuTransactions(file):

    transactions = []

    with open(file, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader, None)  # skip header
        print("Uploading transactions")
        for row in csv_reader:
            date = row[3]
            name = row[6]
            amount = row[4]
            category = categorize(name)
            transaction = ((date, name, amount, category))
            if category != "transfer":          # Ignore transfers
                transactions.append(transaction)
        return transactions

# Connect to google spreadsheet and fill in the transactions
sa = gspread.service_account()
sheet = sa.open("Personal Finances")

while True:
    
    # Get file name and account name
    print("Program started! Type 'stop' in any prompt to exit the program")
    MONTH = get_input("Enter the month for the CSV file (e.g., may): ").strip().lower()

    # FILES FROM ADAM'S ACCOUNT SHOULD BE NAMED THINGS LIKE "MAY" AND TAYLOR'S SHOULD BE NAMED "MAY1"
    # THIS PICKS THE RIGHT FILE FOR THE DESIRED PERSON
    while True:
        person = get_input("Whose account is this for? (e.g., Adam or Taylor): ").strip().lower()
        if person.startswith("a"):
            file = f"{MONTH}.csv"
            break
        if person.startswith("t"):
            file = f"{MONTH}1.csv"
            break
        else:
            print("Invalid name. Please enter either 'Adam' or 'Taylor'")


    wks = sheet.worksheet(f"{MONTH}")

    rows = gcuTransactions(file)
    for row in rows:
        wks.insert_row([row[0], row[1], row[3], row[2]], 8)
        time.sleep(1.2)     # Google spreadsheets has a quota for write requests per minute. Must slow things down to not exceed that limit

    print("Upload complete")

    wks.insert_row([1,2,3], 26)       
    again = get_input("Upload another file? (y/n): ").strip().lower()
    if again != "y":
        print("Done uploading. Goodbye!")
        break                                                                                      