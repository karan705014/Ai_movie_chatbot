from seleniumbase import SB

URL = "https://new1.filesdl.in/cloud/GcgwWQTP4E"


with SB(headless=True) as sb:
    print("Opening:", URL)

    sb.open(URL)

    print("PAGE TITLE:", sb.get_title())

    if sb.is_element_present("a.button"):
        print("BUTTON FOUND")

        href = sb.get_attribute("a.button", "href")

        print("FINAL LINK:", href)
    else:
        print("BUTTON NOT FOUND")