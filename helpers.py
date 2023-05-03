def filenameExists(filename, existing):
    if filename in existing:
        return True
    return False

def isValidUsername(username):
    usernameWords = username.split()
    # If user inputs empty string, whitespace, or multiple words as username
    if len(usernameWords) != 1:
        print("Usernames can only be one word containing letters, numbers, and special characters. " 
              "Please try again with a different username.\n")
        return False
    return True

# Sign in to existing account. Returns (errorFlag, message).
def signInExisting(username, clientDict):
    if username in clientDict:
        return (True, "Someone has already chosen this screen name. Please choose another.")
    return (False, "You have entered the text editor.")

def broadcastUpdate(filename, clientDict, savingUser):
    for client in clientDict:
        if client != savingUser:
            clientDict[client].append(filename)


