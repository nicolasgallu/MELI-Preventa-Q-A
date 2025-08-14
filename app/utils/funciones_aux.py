import requests


"""FUNCION OBTENER USERS"""
def get_user_id(ACCESS_TOKEN):
    url = "https://api.mercadolibre.com/users/me"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get("id")
        else:
            print(f"Error al obtener el user_id capoooo: {response.json()}")
            return None
    except Exception as e:
        print(f"Excepción al obtener el user_id: {e}")
        return None



"""FUNCION OBTENER ITEMS PUBLICADOS"""
def fetch_items(user_id,ACCESS_TOKEN):
    url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            item_ids = response.json().get("results", [])
            print(f"IDs de los ítems encontrados: {item_ids}")
            return item_ids
        else:
            print(f"Error al obtener los ítems: {response.json()}")
            return []
    except Exception as e:
        print(f"Error al conectar con la API: {e}")
        return []


"""FUNCION OBTENER DETALLES ESPECIFICOS DE CADA ITEM"""
def fetch_item_details(item_id,ACCESS_TOKEN):
    url_details = f"https://api.mercadolibre.com/items/{item_id}"
    url_description = f"https://api.mercadolibre.com/items/{item_id}/description"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response_details = requests.get(url_details, headers=headers)
        response_description = requests.get(url_description, headers=headers)
        if response_details.status_code == 200:
            item_data = response_details.json()
            if response_description.status_code == 200:
                item_data["description"] = response_description.json().get("plain_text", "")
            else:
                item_data["description"] = None
            return item_data
        else:
            print(f"Error al obtener detalles del ítem {item_id}: {response_details.json()}")
            return None
    except Exception as e:
        print(f"Error al conectar con la API para el ítem {item_id}: {e}")
        return None