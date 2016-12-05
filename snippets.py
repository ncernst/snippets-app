import logging
import argparse
import psycopg2


# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

#Postgres SQL db connection
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def put(name, snippet):
    """
    Store a snippet with an associated name.
    
    Returns the name and the snippet
    """
    logging.info("Storing snippet ({!r}: {!r})".format(name, snippet))
    cursor = connection.cursor()
    try:
        command = "INSERT INTO snippets VALUES (%s, %s)"
        cursor.execute(command, (name, snippet))
    except psycopg2.IntegrityError as e:
        
        logging.info("User attempted to store snippet with existing keyword.")
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
                put(name, snippet)
            else:
                exit()
        
    connection.commit()
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

def update(name, snippet):
    """
    
    Update the snippet with a given name.

    """    
    logging.info("Updating existing keyword {!r} with {!r}.".format(name, snippet))
    command = "update snippets set message=%s where keyword=%s"
    cursor = connection.cursor()
    cursor.execute(command, (snippet, name))
    connection.commit()
    logging.debug("Snippet updated successfully.")

    
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


if __name__ == "__main__":
    main()