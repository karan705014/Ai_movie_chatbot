from seleniumbase import SB



from seleniumbase import SB
URL = "https://new1.filesdl.in/cloud/GcgwWQTP4E"

with SB(headless=True) as sb:
    print("Opening:", URL)

    sb.open(URL)

    print("TITLE:", sb.get_title())

    cookies = sb.driver.get_cookies()

    print("COOKIE COUNT:", len(cookies))

    for cookie in cookies:
        print(
            cookie["name"],
            "=",
            cookie.get("value")
        )

    print("SESSION TEST COMPLETE")