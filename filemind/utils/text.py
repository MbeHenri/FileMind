def getContentTextFile(pathfile: str):

    with open(pathfile, "r") as file:
        context = file.read()

    return {"context": context}
