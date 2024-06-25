import pickle

from requests_html import HTMLSession

# Dictionary for every Pokémon
pokemon_base = {
    "name": "",
    "current_health": 100,
    "base_health": 100,
    "level": 1,
    "types": [],
    "current_exp": 0
}

# Page base link to use with every Pokémon
URL_BASE = "https://www.pokexperto.net/index2.php?seccion=nds/nationaldex/movimientos_nivel&pk="


def get_pokemon(index):
    # Enter Pokémon page
    url = f"{URL_BASE}{index}"
    session = HTMLSession()
    pokemon_page = session.get(url)

    # Creating a new dictionary
    new_pokemon = pokemon_base.copy()

    # Catching info from the page
    pokemon_name = pokemon_page.html.find(".mini", first=True).text
    pokename = pokemon_name.split("\n")
    new_pokemon["name"] = pokename[0]

    """Mi versión: 
    type_images = pokemon_page.html.find('td[valign="top"] table tr:nth-child(1) td:nth-child(2) img')
    new_pokemon["types"] = [img.attrs['alt'] for img in type_images]
    """

    # Nate's version
    new_pokemon["types"] = []
    for img in pokemon_page.html.find(".pkmain", first=True).find(".bordeambos", first=True).find("img"):
        new_pokemon["types"].append(img.attrs["alt"])

    # Getting attacks' info
    new_pokemon["attacks"] = []
    for attack_item in pokemon_page.html.find(".pkmain")[-1].find("tr .check3"):
        attack = {
            "name": attack_item.find("td", first=True).find("a", first=True).text,
            "type": attack_item.find("td")[1].find("img", first=True).attrs["alt"],
            "min_level": attack_item.find("th", first=True).text,
            "damage": int(attack_item.find("td")[3].text.replace("--", "0"))
        }
        new_pokemon["attacks"].append(attack)

    # Returning new Pokémon dictionary
    return new_pokemon


def get_all_pokemons():
    try:
        print("Cargando el archivo de Pokémon")
        with open("pokefile.pkl", "rb") as pokefile:
            all_pokemons = pickle.load(pokefile)
    except FileNotFoundError:
        print("Archivo no encontrado. Cargando Pokemons de internet")
        all_pokemons = []
        for index in range(151):
            all_pokemons.append(get_pokemon(index+1))
            print("*")
        print("\n¡Todos los Pokemons han sido descargados!")
        #Pickle
        with open("pokefile.pkl", "wb") as pokefile:
            pickle.dump(all_pokemons, pokefile)
    print("LISTA CARGADA")
    return all_pokemons
