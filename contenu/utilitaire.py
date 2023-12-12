import os, datetime

def _handle_uploaded_file(file, dossier_user):
    """Fonction utilitaire d'upload de fichiers..
    """
    # verifie si dossier n'existe pas, je le cree d'abord..
    repertoire = os.path.join(
        settings.BASE_DIR,
        f'media/{dossier_user}'
    )
    if not os.path.exists(repertoire):
        os.makedirs(repertoire, exist_ok=True)
    # Write the file to media folder
    try:
        destination = open(f'{repertoire}/{file.name}', 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
    except Exception as ferr:
        print("Cannot upload file ->", ferr)
        pass

def generateUploadKey(name_folder):
    """Fonction utilitaire generant une cle pour
    creer un dossier propre a chaque user"""
    cle = None
    try:
        time = datetime.datetime.now().isoformat()
        plain = name_folder + '\0' + time
        cle = sha1(plain.encode('utf-8')).hexdigest()
    except Exception as e:
        print('er encodage ->', e)
        pass
    return cle