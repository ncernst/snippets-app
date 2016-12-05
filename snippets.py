import logging
import argparse
import psycopg2


# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

#Postgres SQL db connection
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def checkForRow(name):
    """
    
    Checks to see if a row exists for provided keyword
    
    """
    logging.info("Checking to see if row exists for keyword ({!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT keyword FROM snippets WHERE keyword = %s", (name,))
        rowExists = cursor.fetchone()
    if not rowExists:
        return False
    else:
        return True
        

def put(name, snippet):
    """
    Store a snippet with an associated name.
    
    Returns the name and the snippet
    """
    logging.info("Storing snippet ({!r}: {!r})".format(name, snippet))
    rowExists = checkForRow(name)
    if not rowExists:
        with connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO snippets VALUES (%s, %s)", (name, snippet))
    if rowExists:
        logging.debug("User attempted to store snippet with existing keyword.")
        print("There is already a snippet with that name, do you want to update it? Y/N")
        choice = input(">>> ").lower()
        if choice == 'y':
            connection.rollback()
            update(name, snippet)
        else:
            print("Would you like to choose a new name for this snippet? Y/N")
            choice = input(">>> ").lower()
            if choice == 'y':
                logging.info("User selecting new keyword for snippet to store.")
                print("Please enter the new name")
                name = input(">>> ")
                connection.rollback()
                put(name, snippet)
            else:
                exit()

    logging.debug("Snippet stored successfully.")
    return name, snippet

def get(name):
    """
    Retrieve the snippet with a given name.
    
    If there is no such snippet, return '404: Snippet Not Found'.
    
    Returns the snippet.
    """
    logging.info("Retrieving snippet {!r}".format(name))
    cursor = connection.cursor()
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        snippet = cursor.fetchone()
    if not snippet:
        # No snippet was found with that name
        logging.debug("Snippet wasn't found with keyword provided by user.")
        return '404: Snippet Not Found'
    
    logging.debug("Snippet retrieved successfully.")
    return snippet

def catalogue():
    """
    
    Return a catalogue of all stored keywords to the user.

    """   
    logging.info("Retrieving catalogue of keywords.")
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT keyword FROM snippets")
        catalogue = cursor.fetchall()
    return catalogue

def update(name, snippet):
    """
    
    Update the snippet with a given name.

    """    
    logging.info("Updating existing keyword {!r} with {!r}.".format(name, snippet))
    with connection, connection.cursor() as cursor:
        cursor.execute("update snippets set message=%s where keyword=%s", (snippet, name))
    logging.debug("Snippet updated successfully.")
    return name, snippet
    
def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description = "Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    #Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet text")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
    #Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet of text")
    get_parser.add_argument("name", help="Name of the snippet to retrieve")
    
    #Subparser for the update command
    logging.debug("Constructing update subparser")
    update_parser = subparsers.add_parser("update", help="Update an existing snippet based on keyword")
    update_parser.add_argument("name", help="Keyword of snippet to update")
    update_parser.add_argument("snippet", help="The updated snippet text")
    
    #Subparser for the catalogue command
    logging.debug("Constructing catalogue subparser")
    catalogue_parser = subparsers.add_parser("catalogue", help="Display a list of snippet keywords")
    
    arguments = parser.parse_args()
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)

    command = arguments.pop("command")

    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "update":
        name, snippet = update(**arguments)
        print("Updated {!r} with {!r}".format(name, snippet))
    elif command == "catalogue":
        print("Keyword Catalogue:")
        keywordList = catalogue()
        for name in keywordList:
            print(name)
        


if __name__ == "__main__":
    main()