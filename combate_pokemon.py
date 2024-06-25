import os
import pickle
import random
from time import sleep

from pokeload import get_all_pokemons

pokemon_list = get_all_pokemons()


def get_player_profile():
    return {
        "player_name": input("¿Cuál es tu nombre? "),
        "pokemon_inventory": [random.choice(pokemon_list) for _ in range(3)],
        "combats": 0,
        "pokeball": 0,
        "health_potion": 0,
        "combat_history": [],
    }


def combat_format(attack_history, enemy_pokemon, enemy_damage, received_damage, win, caught):
    return {
        "enemy_pokemon": enemy_pokemon["name"],
        "player_pokemons": attack_history,
        "enemy_damage": enemy_damage,
        "received_damage": received_damage,
        "win": win,
        "caught": caught
    }


def any_player_pokemon_lives(player_profile):
    return sum([pokemon["current_health"] for pokemon in player_profile["pokemon_inventory"]]) > 0


def choose_pokemon(player_profile):
    players_pokemon = [pokemon for pokemon in player_profile["pokemon_inventory"]]
    print("Escoge un pokemon para ir a combate: ")
    for i, p in enumerate(players_pokemon, start=1):
        if p["current_health"] != 0:
            print("{}) {}".format(i, get_pokemon_info(p)))
    while True:
        try:
            pokemon_number = int(input("Ingrese el número de su opción: "))
            if players_pokemon[pokemon_number - 1]["current_health"] == 0:
                print("Opción inválida.")
            else:
                chosen_pokemon = players_pokemon[pokemon_number - 1]
                print("Ha seleccionado: {}".format(chosen_pokemon["name"]))
                break
        except (ValueError, IndexError):
            print("Opción inválida.")
    return chosen_pokemon


def get_pokemon_info(pokemon):
    return "{} | type: {}| lvl: {} | hp {}/{}".format("".join(pokemon["name"]), ", ".join(pokemon["types"]),
                                                      pokemon["level"], pokemon["current_health"],
                                                      pokemon["base_health"])


def random_item(player_profile):
    chance = random.randint(1, 3)
    if chance == 1:
        print("--- Has ganado una pokebola ---")
        player_profile["pokeball"] += 1
    elif chance == 2:
        print("--- Has ganado un poción de vida ---")
        player_profile["health_potion"] += 1
    else:
        print("--- No has ganado nada. ---")


def weakness_type(poke_ataque, poke):
    weakness_list = {"normal": ["lucha"], "fuego": ["agua", "tierra", "roca"], "agua": ["planta", "electrico"],
                     "planta": ["fuego", "hielo", "veneno", "volador", "bicho"], "electrico": ["tierra"],
                     "hielo": ["fuego", "lucha", "roca", "acero"], "lucha": ["volador", "psiquico", "hada"],
                     "veneno": ["tierra", "psiquico"], "tierra": ["agua", "planta", "hielo"],
                     "volador": ["electrico", "hielo", "roca"], "psiquico": ["bicho", "fantasma", "siniestro"],
                     "bicho": ["volador", "roca", "fuego"], "roca": ["agua", "planta", "lucha", "tierra", "acero"],
                     "fantasma": ["fantasma", "siniestro"], "dragon": ["hielo", "dragon", "hada"],
                     "siniestro": ["lucha", "bicho", "hada"], "acero": ["fuego", "lucha", "tierra"],
                     "hada": ["veneno", "acero"]
                     }
    for p in poke["types"]:
        if p in weakness_list:
            if poke_ataque["type"] in weakness_list.get(p):
                return True
            else:
                return False


def life_bar(chosen_pokemon, enemy_pokemon):
    barra_vida = 10
    lifebar_player = int(chosen_pokemon["current_health"] * barra_vida / chosen_pokemon["base_health"])
    print("{}:   [{}{}]  ({},{})".format(chosen_pokemon["name"], "*" * lifebar_player,
                                         " " * (barra_vida - lifebar_player),
                                         chosen_pokemon["current_health"], chosen_pokemon["base_health"]))

    lifebar_enemy = int(enemy_pokemon["current_health"] * barra_vida / enemy_pokemon["base_health"])
    print(
        "{}:    [{}{}]  ({},{})".format(enemy_pokemon["name"], "*" * lifebar_enemy,
                                        " " * (barra_vida - lifebar_enemy),
                                        enemy_pokemon["current_health"], enemy_pokemon["base_health"]))


def life_upgrader(chosen_pokemon, enemy_pokemon):
    if chosen_pokemon["current_health"] <= 0:
        chosen_pokemon["current_health"] = 0
    if enemy_pokemon["current_health"] <= 0:
        enemy_pokemon["current_health"] = 0


def player_attack(player_pokemon, enemy_pokemon):
    print("Es el turno de {}".format(player_pokemon["name"]))
    print("Ataques disponibles:")
    for i, attack in enumerate(player_pokemon["attacks"], start=1):
        if (attack["min_level"] == "" or int(attack["min_level"]) <= player_pokemon["level"]) \
                and attack["damage"] != 0:
            print("{}) Nombre: {} | Daño: {} | Tipo: {}".format(i, attack["name"], attack["damage"], attack["type"]))
    print("{}) Activar escudo".format(len(player_pokemon["attacks"]) + 1))
    while True:
        try:
            number_attack = int(input("Ingrese el número de su opción: "))
            if number_attack == len(player_pokemon["attacks"]) + 1:
                print("{} activo su escudo.".format(player_pokemon["name"]))
                player_pokemon["is_defending"] = True
                break
            else:
                chosen_attack = player_pokemon["attacks"][number_attack - 1]
                print("{} ataca con {}.".format(player_pokemon["name"], chosen_attack["name"]))
                if not enemy_pokemon["is_defending"]:
                    if weakness_type(chosen_attack, enemy_pokemon):
                        enemy_pokemon["current_health"] -= (int(chosen_attack["damage"]) * 1.25)
                    else:
                        enemy_pokemon["current_health"] -= int(chosen_attack["damage"])
                else:
                    print("{} estaba defendiéndose y bloqueó el ataque.".format(enemy_pokemon["name"]))
                    enemy_pokemon["is_defending"] = False
                break
        except (ValueError, IndexError, TypeError):
            print("Por favor, ingrese un número válido.")


def enemy_attack(player_pokemon, enemy_pokemon):
    print("Es el turno de {}".format(enemy_pokemon["name"]))
    if not random.choice([True, False]):
        print("{} ha activado escudo.".format(enemy_pokemon["name"]))
        enemy_pokemon["is_defending"] = True
    else:
        valid = True
        while valid:
            number_attack_e = random.randint(0, len(enemy_pokemon["attacks"]) - 1)
            chosen_attack_e = enemy_pokemon["attacks"][number_attack_e]
            if (chosen_attack_e["min_level"] == "" or int(chosen_attack_e["min_level"]) <= enemy_pokemon["level"]) \
                    and chosen_attack_e["damage"] != 0:
                valid = False
                print("{} ataca con {}.".format(enemy_pokemon["name"], chosen_attack_e["name"]))
                if not player_pokemon["is_defending"]:
                    if weakness_type(chosen_attack_e, player_pokemon):
                        player_pokemon["current_health"] -= (int(chosen_attack_e["damage"]) * 1.25)
                    else:
                        player_pokemon["current_health"] -= int(chosen_attack_e["damage"])
                else:
                    print("{} estaba defendiéndose y bloqueó el ataque.".format(player_pokemon["name"]))
                    player_pokemon["is_defending"] = False


def assign_experience(attack_history):
    for pokemon in attack_history:
        if pokemon["current_health"] == 0:
            points = 2
            pokemon["current_exp"] += points
        else:
            points = 10
            pokemon["current_exp"] += points

        while pokemon["level"] < 5 and pokemon["current_exp"] > 20:
            pokemon["current_exp"] -= 20
            pokemon["level"] += 1
            pokemon["current_health"] = pokemon["base_health"]
            print("Tu {} ha subido de nivel".format(get_pokemon_info(pokemon)))
        while pokemon["level"] < 10 and pokemon["current_exp"] > 30:
            pokemon["current_exp"] -= 30
            pokemon["level"] += 1
            pokemon["current_health"] = pokemon["base_health"]
            print("Tu {} ha subido de nivel".format(get_pokemon_info(pokemon)))
        while pokemon["level"] < 30 and pokemon["current_exp"] > 40:
            pokemon["current_exp"] -= 40
            pokemon["level"] += 1
            pokemon["current_health"] = pokemon["base_health"]
            print("Tu {} ha subido de nivel".format(get_pokemon_info(pokemon)))
        while pokemon["level"] < 40 and pokemon["current_exp"] > 50:
            pokemon["current_exp"] -= 50
            pokemon["level"] += 1
            pokemon["current_health"] = pokemon["base_health"]
            print("Tu {} ha subido de nivel".format(get_pokemon_info(pokemon)))


def cure_pokemon(player_profile, player_pokemon):
    if player_profile["health_potion"] > 0:
        while True:
            try:
                validation = input(
                    "¿Está seguro de que desea usar una poción de vida en el pokemon actualmente seleccionado?"
                    "\nADVERTENCIA: Recuerde que las pociones de vida dan 50 hp, hasta llegar al 100 de vida."
                    "\nTe quedan {} pociones de+}vida."
                    "\n[Y]es / [N]o _".format(player_profile["health_potion"]))
                if validation == "Y":
                    player_pokemon["current_health"] += 50
                    player_profile["health_potion"] -= 1
                    break
                elif validation == "N":
                    print("No se ha gastado ninguna poción de vida."
                          "Te quedan {} pociones de vida.".format(player_profile["health_potion"]))
            except (ValueError, TypeError):
                print("Ingrese una opción válida.")
    else:
        print("No cuentas con pociones de vida.")


def capture_with_pokeball(enemy_pokemon, player_profile):
    if player_profile["pokeball"] > 0:
        print("¡Haz atrapado al Pokémon!")
        sleep(2)
        print("*")
        sleep(2)
        print("*")
        sleep(2)
        print("*")
        if enemy_pokemon["current_health"] == 100:
            range_prob = 20
        elif enemy_pokemon["current_health"] > 50:
            range_prob = 10
        elif enemy_pokemon["current_health"] > 25:
            range_prob = 5
        elif enemy_pokemon["current_health"] > 5:
            range_prob = 2
        else:
            range_prob = 1
        if random.randint(1, range_prob) == 1:
            print("El Pokémon no ha escapado."
                  "\n{} añadido al inventario."
                  "\n-1 Pokeball".format(enemy_pokemon["name"]))
            player_profile["pokemon_inventory"].append(enemy_pokemon)
            player_profile["pokeball"] -= 1
        else:
            print("El Pokémon ha escapado de la pokeball."
                  "\n-1 Pokeball")
            player_profile["pokeball"] -= 1
    else:
        print("No tienes pokeballs.")


def fight(player_profile, enemy_pokemon):
    os.system("cls")
    print("----PREPARATE COMIENZA LA BATALLA----")
    print("Ha aparecido un {} de tipo/s {}.".format(enemy_pokemon["name"], ", ".join(enemy_pokemon["types"])))
    attack_history = []
    enemy_damage = 0
    received_damage = 0
    win = False
    caught = False
    player_pokemon = choose_pokemon(player_profile)
    player_pokemon['is_defending'] = False
    enemy_pokemon['is_defending'] = False
    print("\t{} VS {}".format(get_pokemon_info(player_pokemon), get_pokemon_info(enemy_pokemon)))

    while any_player_pokemon_lives(player_profile) and enemy_pokemon["current_health"] > 0:
        print("-----------------------------------------------------------")
        action = None
        while action not in ["A", "P", "V", "C", "S"]:
            action = input("¿Qué deseas hacer? [A]tacar, [P]okeball, Poción de [V]ida, [C]ambiar, [S]alir\n _")
        if action == "A":
            e_before = enemy_pokemon["current_health"]
            player_attack(player_pokemon, enemy_pokemon)
            attack_history.append(player_pokemon)
            enemy_damage = e_before - enemy_pokemon["current_health"]
            life_upgrader(player_pokemon, enemy_pokemon)
            life_bar(player_pokemon, enemy_pokemon)
        elif action == "V":
            cure_pokemon(player_profile, player_pokemon)
            life_bar(player_pokemon, enemy_pokemon)
        elif action == "P":
            capture_with_pokeball(enemy_pokemon, player_profile)
            if enemy_pokemon in player_profile["pokemon_inventory"]:
                caught = True
                break
        elif action == "C":
            player_pokemon = choose_pokemon(player_profile)
        else:
            menu(player_profile)

        if player_pokemon["current_health"] == 0 and any_player_pokemon_lives(player_profile):
            player_pokemon = choose_pokemon(player_profile)

        if enemy_pokemon["current_health"] > 0:
            p_before = player_pokemon["current_health"]
            enemy_attack(player_pokemon, enemy_pokemon)
            life_upgrader(player_pokemon, enemy_pokemon)
            life_bar(player_pokemon, enemy_pokemon)
            received_damage = p_before - player_pokemon["current_health"]

    if enemy_pokemon["current_health"] == 0:
        print("HAS GANADO.")
        random_item(player_profile)
        win = True
        enemy_damage = 100

    player_profile["combats"] += 1
    assign_experience(attack_history)
    player_profile["combat_history"].append(combat_format(attack_history, enemy_pokemon, enemy_damage, received_damage,
                                                          win, caught))
    print("----HA TERMINADO LA BATALLA----")
    input("Presione ENTER para continuar")
    os.system("cls")
    menu(player_profile)


def look_inventory(player_profile):
    while True:
        try:
            print("-----------------------------------")
            which_inventory = int(input("Escoja el inventario que desea ver: "
                                        "\n1) Pokémon"
                                        "\n2) Artículos (pociones y pokeball)"
                                        "\n3) Historial de combates"
                                        "\n4) Volver al menú principal"
                                        "\n"))
            if which_inventory not in [1, 2, 3, 4]:
                raise ValueError("Opción fuera de rango")
        except (ValueError, TypeError) as e:
            print("Ingrese una opción válida: ", e)
            continue

        if which_inventory == 1:
            os.system("cls")
            print("-- POKÉMON --")
            for po in player_profile["pokemon_inventory"]:
                print(get_pokemon_info(po))
            input("Presione ENTER para volver ")

        elif which_inventory == 2:
            os.system("cls")
            print("-- POKEBALL Y POCIÓN DE VIDA --")
            print("Usted cuenta con:"
                  "\n- Pokeball: {}"
                  "\n- Poción de vida: {}".format(player_profile["pokeball"], player_profile["health_potion"]))
            input("Presione ENTER para volver ")

        elif which_inventory == 3:
            os.system("cls")
            print("-- HISTORIAL DE COMBATES --")
            print("Usted cuenta con un total de {} combates.".format(len(player_profile["combat_history"])))
            if not player_profile["combat_history"]:
                print("No hay registros de combates.")
            else:
                try:
                    for i, c in enumerate(player_profile["combat_history"], start=1):
                        result = "COMBATE GANADO" if c["win"] else "ENEMIGO ATRAPADO" if c["caught"] else "COMBATE " \
                                                                                                          "PERDIDO"
                        print("{}) Enemigo: {} | Pokémon usado/s: {} | Daño hecho: {} | Daño recibido: {} | {}".format(
                            i, c["enemy_pokemon"], ", ".join([p["name"] for p in c["player_pokemons"]]),
                            c["enemy_damage"], c["received_damage"], result))
                except (KeyError, Exception):
                    print("Hubo un error con los combates.")
            input("Presione ENTER para volver.")
        elif which_inventory == 4:
            os.system("cls")
            break


def save_progress(player_profile):
    print("--------------------------------------")
    try:
        print("Guardando.")
        with open("progress_file.pkl", "rb") as progress_file:
            all_players = pickle.load(progress_file)
        with open("progress_file.pkl", "wb") as progress_file:
            check_exist = False
            for p in all_players:
                if player_profile["player_name"] == p["player_name"]:
                    check_exist = True
            if check_exist:
                while True:
                    try:
                        print("¿Quiere reescribir la partida ya existente de {}?"
                              .format(player_profile["player_name"]))
                        confirmation = input("[Y]es / [N]o\n")
                        if confirmation == "Y":
                            ind = all_players.index(p)
                            all_players.remove(p)
                            all_players.insert(ind, player_profile)
                            pickle.dump(all_players, progress_file)
                            break
                        elif confirmation == "N":
                            print("No se guardó la partida.")
                            break
                    except (ValueError, TypeError):
                        print("Ingrese una opción válida.")
            else:
                all_players.append(player_profile)
                pickle.dump(all_players, progress_file)
    except FileNotFoundError:
        print("Creando guardado.")
        all_players = [player_profile]
        print("*")
        # Pickle
        with open("progress_file.pkl", "wb") as progress_file:
            pickle.dump(all_players, progress_file)
    print("GUARDADO")


def load_progress():
    print("--------------------------------------")
    try:
        with open("progress_file.pkl", "rb") as progress_file:
            all_players = pickle.load(progress_file)
        if len(all_players) != 0:
            for i, p in enumerate(all_players):
                print("{}) {}".format(i + 1, p["player_name"]))
            while True:
                try:
                    player_chosen = int(input())
                    if player_chosen <= len(all_players):
                        player_profile = all_players[player_chosen - 1]
                        print("Ha seleccionado: {}".format(player_profile["player_name"]))
                        return player_profile
                except (ValueError, TypeError):
                    print("Escoja una opción válida.")
        else:
            print("No existen partidas guardadas.")
    except FileNotFoundError:
        print("No existen partidas guardadas.")


def delete_profile(player_profile):
    print("--------------------------------------")
    try:
        with open("progress_file.pkl", "rb") as progress_file:
            all_players = pickle.load(progress_file)
        if player_profile in all_players:
            all_players.remove(player_profile)
            with open("progress_file.pkl", "wb") as progress_file:
                pickle.dump(all_players, progress_file)
            print("Partida eliminada correctamente.")
        else:
            print("Perfil no encontrado en el archivo de guardado.")
    except FileNotFoundError:
        print("No existen partidas guardadas.")


def menu(player_profile):
    while any_player_pokemon_lives(player_profile):
        enemy_pokemon = random.choice(pokemon_list)
        while True:
            try:
                print("------------------------------------------")
                print("-- BIENVENIDO {} --".format(player_profile["player_name"].upper()))
                print("Escoja una de las siguientes opciones:")
                option = int(input("1) Ver inventario y combates."
                                   "\n2) ¡Encontrar Pokémon!"
                                   "\n3) Guardar progreso."
                                   "\n4) Cargar progreso."
                                   "\n5) Eliminar partida."
                                   "\n6) Salir"
                                   "\n"))
                if option == 1:
                    look_inventory(player_profile)
                elif option == 2:
                    fight(player_profile, enemy_pokemon)
                    print("--------------------------------------")
                elif option == 3:
                    save_progress(player_profile)
                elif option == 4:
                    load_progress()
                elif option == 5:
                    while True:
                        try:
                            confirmation = input("¿Está seguro que quiere eliminar la partida?"
                                                 "[Y]es / [N]o\n")
                            if confirmation == "Y":
                                delete_profile(player_profile)
                                while True:
                                    try:
                                        after = int(input("1) Volver al inicio."
                                                          "\n2) Salir"))
                                        if after == 1:
                                            main()
                                        elif after == 2:
                                            exit()
                                    except (ValueError, TypeError):
                                        print("Ingrese una opción válida.")
                            elif confirmation == "N":
                                print("Se ha cancelado el eliminado de la partida.")
                                break
                        except (ValueError, TypeError):
                            print("Ingrese una opción válida.")
                elif option == 6:
                    exit()
            except (ValueError, TypeError):
                print("Ingrese una opción válida.")
    print("Has perdido en el combate número {}".format(player_profile["combats"]))
    delete_profile(player_profile)
    while True:
        try:
            lost_option = input("¿Desea volver a comenzar?"
                                "[Y]es / [N]o\n")
            if lost_option == "Y":
                delete_profile(player_profile)
                main()
            elif lost_option == "N":
                exit()
        except (ValueError, TypeError):
            print("Ingrese una opción válida.")


def main():
    while True:
        try:
            init = int(input("-- BIENVENIDO AL MUNDO POKEMON --\n"
                             "Escoja una de las siguientes opciones:\n"
                             "1) Crear partida.\n"
                             "2) Cargar partida.\n"
                             ""))
            if init == 1:
                player_profile = get_player_profile()
                save_progress(player_profile)
                menu(player_profile)
            elif init == 2:
                player_profile = load_progress()
                menu(player_profile)
        except (ValueError, TypeError):
            print("Ingrese una opción válida.")


if __name__ == "__main__":
    main()
