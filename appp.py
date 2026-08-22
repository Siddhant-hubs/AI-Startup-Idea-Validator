"""CLI tester for the complete Milestone 3 pipeline."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SERVER_URL = "http://127.0.0.1:8900/api/validate"


def main():
    idea = input("Enter Startup Idea: ").strip()
    if not idea:
        print("Please enter a non-empty idea.")
        return

    request = Request(
        SERVER_URL,
        data=json.dumps({"idea": idea}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=600) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            detail = json.loads(error.read().decode("utf-8")).get("detail", "Unknown error")
        except Exception:
            detail = "Unknown error"
        print(f"Error {error.code}: {detail}")
        return
    except URLError:
        print("Could not reach the server. Start it with: python web_search_agent.py")
        return

    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
