from PyPDF2 import PdfReader


def getMetadataPdfFile(pathfile: str):
    reader = PdfReader(pathfile)
    metadata = reader.metadata

    if metadata is None:
        return {}

    return {
        "title": metadata.title,
        "author": metadata.author,
        "creator": metadata.creator,
        "producer": metadata.producer,
        "subject": metadata.subject,
    }
