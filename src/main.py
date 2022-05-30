# you should have received a copy of the opinionated queer license v1.0 along with this program.
# if not, see <https://oql.avris.it/license?c=sweeze>
from os.path import exists
from pathlib import Path
from requests import Response, ConnectionError  # for type hints
from requests_html import HTMLSession
import rtoml as toml
from xmltodict import parse

config: dict[str, str] = toml.load(
    Path("config.toml")
)  # config file instead of asking a bunch of questions every time

session: HTMLSession = HTMLSession()  # think of this like a browser
session.headers = {
    "User-Agent": f"Endo helper, devved by nation=sweeze in use by nation={config['main_nation']}",
}  # user agent so admin can identify the script being used, its author (me), and the person it is being used by


def make_request(
    url: str, payload: dict, action: str = "Press enter to continue"
) -> Response:
    """Makes a post request to the specified url with the specified payload

    Args:
        url (str): URL to make the request to
        payload (dict): Payload to send with the request
        action (str, optional): Action to display in the human initialization message. Defaults to "Press enter to continue"

    Returns:
        Response: Response of the request
    """
    if "cgi-bin/api.cgi" not in url.lower():  # checks if the url is an api request
        input(action)
        # so it's a human initiated request and doesn't have to follow the html rate limit
    return session.post(url, data=payload, allow_redirects=False)


def get_cross_list(point: str, nation: str) -> list:
    """Gets the cross list of the specified point for the specified nation

    Args:
        point (str): Point to get the cross list of
        nation (str): Nation you are endorsing from

    Returns:
        list: Cross list of the specified point
    """
    url: str = "https://www.nationstates.net/cgi-bin/api.cgi"
    data: dict = {
        "q": "endorsements",
        "nation": point,
    }

    response: Response = make_request(url, data)

    nations: list = parse(response.text)["NATION"]["ENDORSEMENTS"].split(",")

    if nation not in nations:
        nations.append(point)
    return nations


def get_local_id(nation: str, password: str) -> str:
    """Logs into and grabs the local ID of your nation for the sake of security checks

    Args:
        nation (str): Nation you're logging into
        password (str): Password to said nation

    Returns:
        str: local_id
    """
    data: dict[str, str] = {
        "logging_in": "1",
        "nation": nation,
        "password": password,
    }
    url: str = "https://www.nationstates.net/template-overall=none/page=settings/"

    response: Response = make_request(url, data, action="Press enter to log in")

    if response.status_code == 200:
        return response.html.find("input[name=localid]", first=True).attrs["value"]
    else:
        raise ConnectionError(response.status_code, response.reason)


def endorse(nation: str, local_id: str) -> None:
    """Endorses the specified nation

    Args:
        nation (str): Nation to endorse
        local_id (str): Localid of the nation you're endorsing from
    """
    data: dict[str, str] = {
        "localid": local_id,
        "nation": nation,
        "action": "endorse",
    }
    url: str = "https://www.nationstates.net/cgi-bin/endorse.cgi"

    response = make_request(url, data, f"Press enter to endorse {nation}")

    if response.status_code == 302:
        print(f"Endorsed {nation}")
    else:
        print(f"Failed to endorse {nation}")


def main() -> None:
    local_id: str = get_local_id(config["wa_nation"], config["password"])
    # local id for the sake of nationstates' security checks
    nations_to_endo: list = get_cross_list(config["point"], config["wa_nation"])
    for nation in nations_to_endo:
        endorse(nation, local_id)


if __name__ == "__main__":
    main()
