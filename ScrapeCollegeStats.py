import urllib3


def player_page(id):
    return "https://www.basketball-reference.com/players/{0}/{1}".format(id[0], id)

#cbb_page = "https://www.sports-reference.com/cbb/players/ben-simmons-1.html"
#cbb per 100 table =